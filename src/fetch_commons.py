# src/fetch_commons.py
import requests, sys, yaml
from pathlib import Path
from datetime import datetime, timezone

API = "https://commons.wikimedia.org/w/api.php"

def fetch_commons_file(title: str) -> dict:
    # title example: "File:Leibniz_University_Hannover.jpg"
    params = {
        "action": "query",
        "prop": "imageinfo",
        "titles": title,
        "iiprop": "url|user|extmetadata|mime|size|timestamp",
        "format": "json",
        "origin": "*",
    }
    r = requests.get(API, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    if "imageinfo" not in page:
        raise SystemExit(f"No imageinfo for {title}")
    ii = page["imageinfo"][0]
    em = ii.get("extmetadata", {})
    def M(k, default=""):
        return em.get(k, {}).get("value", default)

    # map to our normalized source.yml
    src = {
        "id": f"https://commons.wikimedia.org/wiki/{title}",
        "title": M("ObjectName", title.replace("File:", "")),
        "creator": M("Artist", ii.get("user", "Unknown")) or "Unknown",
        "date": (M("DateTimeOriginal") or M("DateTime") or ii["timestamp"][:10]),
        "rights_text": M("LicenseShortName") or M("Credit"),
        "license_url": M("LicenseUrl") or "https://creativecommons.org/licenses/by-sa/4.0/",
        "format": ii.get("mime", "image/jpeg"),
        "content_url": ii["url"],
        "provenance_agent_id": "https://commons.wikimedia.org",
        "provenance_agent_label": "Wikimedia Commons",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return src

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/fetch_commons.py 'File:Your_Image.jpg'")
        sys.exit(2)
    title = sys.argv[1]
    src = fetch_commons_file(title)
    Path("metadata").mkdir(parents=True, exist_ok=True)
    with open("metadata/source.yml", "w") as f:
        yaml.safe_dump(src, f, sort_keys=False)
    print("Wrote metadata/source.yml")
    # fetch the binary as data/image.jpg
    Path("data").mkdir(parents=True, exist_ok=True)
    img = requests.get(src["content_url"], timeout=30)
    img.raise_for_status()
    with open("data/image.jpg", "wb") as out:
        out.write(img.content)
    print("Wrote data/image.jpg")

if __name__ == "__main__":
    main()
