# src/build_metadata.py
import yaml, json, sys
from pathlib import Path
import re

SRC = Path("metadata/source.yml")
OUT = Path("metadata/record.jsonld")

TEMPLATE = {
  "@context": {
    "dc": "http://purl.org/dc/terms/",
    "edm": "http://www.europeana.eu/schemas/edm/",
    "schema": "http://schema.org/",
    "prov": "http://www.w3.org/ns/prov#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "schema:license": {"@id": "http://schema.org/license", "@type": "@id"},
    "id": "@id", "type": "@type"
  },
  "type": ["edm:ProvidedCHO", "schema:CreativeWork"]
}

def _normalize_cc_url(url: str) -> str:
    if not isinstance(url, str):
        return url
    url = url.strip()
    if url.startswith("https://creativecommons.org/licenses/") and not url.endswith("/"):
        url += "/"
    return url


def _strip_html(s: str) -> str:
    if not isinstance(s, str):
        return s
    # remove simple tags; good enough for Commons’ extmetadata
    return re.sub(r"<[^>]+>", "", s).strip()

def _normalize_datetime(s: str) -> str:
    if not isinstance(s, str) or not s.strip():
        return s
    s = s.strip()
    # already ISO 8601?
    if "T" in s and s.endswith("Z"):
        return s
    # if like "YYYY-MM-DD HH:MM:SS"
    m = re.match(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})", s)
    if m:
        return f"{m.group(1)}T{m.group(2)}Z"
    # fallback: if just a date, keep as is
    return s


def main():
    if not SRC.exists():
        sys.exit("Missing metadata/source.yml")
    data = yaml.safe_load(SRC.read_text())

    license_url = _normalize_cc_url(data.get("license_url", ""))
    creator_plain = _strip_html(data.get("creator", "Unknown"))
    date_norm = _normalize_datetime(data.get("date", ""))

    rec = TEMPLATE.copy()
    rec["id"] = data["id"]
    rec["dc:title"] = data["title"]
    rec["dc:creator"] = creator_plain
    rec["dc:date"] = date_norm
    rec["dc:rights"] = data["rights_text"]
    rec["dc:format"] = data["format"]
    rec["schema:contentUrl"] = data["content_url"]
    rec["schema:license"] = {"@id": license_url}
    rec["prov:wasDerivedFrom"] = {
        "id": data["content_url"],
        "type": "prov:Entity",
        "dc:description": "Downloaded binary from Wikimedia Commons"
    }
    rec["prov:wasAttributedTo"] = {
        "id": data["provenance_agent_id"],
        "type": "prov:Agent",
        "schema:name": data["provenance_agent_label"]
    }
    rec["prov:generatedAtTime"] = {"@value": data["generated_at"], "@type": "xsd:dateTime"}

    OUT.write_text(json.dumps(rec, indent=2))
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
