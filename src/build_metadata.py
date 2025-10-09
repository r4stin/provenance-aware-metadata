# src/build_metadata.py
import yaml, json, sys
from pathlib import Path

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

def main():
    if not SRC.exists():
        sys.exit("Missing metadata/source.yml")
    data = yaml.safe_load(SRC.read_text())

    license_url = _normalize_cc_url(data.get("license_url", ""))

    rec = TEMPLATE.copy()
    rec["id"] = data["id"]
    rec["dc:title"] = data["title"]
    rec["dc:creator"] = data["creator"]
    rec["dc:date"] = data["date"]
    rec["dc:rights"] = data["rights_text"]
    rec["dc:format"] = data["format"]
    rec["schema:contentUrl"] = data["content_url"]
    rec["schema:license"] = {"@id": license_url}
    rec["prov:wasDerivedFrom"] = {
        "id": data["id"],
        "type": "prov:Entity",
        "dc:description": "Original file from Wikimedia Commons"
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
