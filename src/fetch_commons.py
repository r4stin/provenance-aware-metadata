# src/fetch_commons.py
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import requests
import yaml

API = "https://commons.wikimedia.org/w/api.php"

# Use a clear, contactable UA as per WMF policy:
UA = (
    "ProvenanceAwareMetadata/0.2 "
    "(https://github.com/your-user/your-repo; contact: youremail@example.org)"
)

def _get(params, max_retries=3, backoff=2.0):
    """GET with UA header, minimal retry on 403/429."""
    headers = {"User-Agent": UA}
    for attempt in range(1, max_retries + 1):
        r = requests.get(API, params=params, headers=headers, timeout=30)
        if r.status_code in (403, 429):
            if attempt == max_retries:
                r.raise_for_status()
            time.sleep(backoff * attempt)
            continue
        r.raise_for_status()
        return r
    raise RuntimeError("Unreachable")

def fetch_commons_file(title: str) -> dict:
    # Example title: "File:Leibniz_University_Hannover.jpg"
    params = {
        "action": "query",
        "prop": "imageinfo",
        "titles": title,
        "iiprop": "url|user|extmetadata|mime|size|timestamp",
        "redirects": 1,
        "format": "json",
        "formatversion": "2",
        # no 'origin=*' since we are not a browser (CORS)
    }
    r = _get(params)
    data = r.json()

    if "query" not in data or "pages" not in data["query"]:
        raise SystemExit(f"Unexpected response for {title}: {data}")

    pages = data["query"]["pages"]
    page = pages[0] if pages else {}
    if "imageinfo" not in page:
        raise SystemExit(f"No imageinfo for {title}. Page data: {page}")

    ii = page["imageinfo"][0]
    em = ii.get("extmetadata", {}) or {}

    def M(key, default=""):
        val = em.get(key, {})
        if isinstance(val, dict):
            return val.get("value", default) or default
        return val or default

    # Normalize/clean values
    license_url = M("LicenseUrl") or M("UsageTerms")
    if license_url and isinstance(license_url, str):
        license_url = license_url.strip()

    rights_text = M("LicenseShortName") or M("Credit") or M("UsageTerms") or "Unknown"

    dt = (
        M("DateTimeOriginal")
        or M("DateTime")
        or (ii.get("timestamp") or "")[:10]
        or str(datetime.now().date())
    )

    src = {
        "id": f"https://commons.wikimedia.org/wiki/{title}",
        "title": (M("ObjectName") or title.replace("File:", "")).strip(),
        "creator": (M("Artist") or ii.get("user") or "Unknown").strip(),
        "date": dt,
        "rights_text": rights_text,
        "license_url": license_url or "https://creativecommons.org/licenses/by-sa/4.0/",
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
    try:
        src = fetch_commons_file(title)
    except requests.HTTPError as e:
        msg = f"HTTP error from Commons: {e}. " \
              f"Make sure you have a proper User-Agent configured in fetch_commons.py (UA={UA})"
        raise SystemExit(msg)

    # Write source.yml
    Path("metadata").mkdir(parents=True, exist_ok=True)
    with open("metadata/source.yml", "w") as f:
        yaml.safe_dump(src, f, sort_keys=False)
    print("✅ Wrote metadata/source.yml")

    # Download image to data/image.jpg
    Path("data").mkdir(parents=True, exist_ok=True)
    img_headers = {"User-Agent": UA}
    img = requests.get(src["content_url"], headers=img_headers, timeout=60)
    img.raise_for_status()
    with open("data/image.jpg", "wb") as out:
        out.write(img.content)
    print("✅ Wrote data/image.jpg")

if __name__ == "__main__":
    main()
