# tests/test_build_and_validate.py
import json, subprocess, sys, os, yaml, pathlib

def test_build_and_validate():
    # ensure source exists (create a tiny local one if missing)
    pathlib.Path("metadata").mkdir(exist_ok=True)
    src_path = pathlib.Path("metadata/source.yml")
    if not src_path.exists():
        src_path.write_text("""\
id: "https://example.org/demo"
title: "Demo Asset"
creator: "Unknown"
date: "2024"
rights_text: "CC BY 4.0"
license_url: "https://creativecommons.org/licenses/by/4.0/"
format: "image/jpeg"
content_url: "https://upload.wikimedia.org/wikipedia/commons/9/95/Leibniz_University_Hannover.jpg"
provenance_agent_id: "https://commons.wikimedia.org"
provenance_agent_label: "Wikimedia Commons"
generated_at: "2024-01-01T00:00:00Z"
""")
    subprocess.check_call([sys.executable, "src/build_metadata.py"])
    # file exists and has key fields
    rec = json.loads(open("metadata/record.jsonld").read())
    assert "dc:title" in rec
    assert "schema:license" in rec

    # validate
    out = subprocess.check_output([sys.executable, "src/validate_metadata.py"], text=True)
    assert "Conforms: True" in out
