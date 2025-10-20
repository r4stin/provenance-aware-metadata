from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
import json
import subprocess, shutil

app = FastAPI(title="Provenance Metadata (Phase 2)")

@app.get("/record")
def get_record():
    with open("metadata/record.jsonld") as f:
        return JSONResponse(json.load(f))

@app.get("/image")
def get_image():
    return FileResponse("data/image.c2pa.jpg", media_type="image/jpeg")

@app.get("/iiif/manifest")
def iiif_manifest():
    with open("metadata/record.jsonld") as f:
        rec = json.load(f)
    label = rec.get("dc:title", "Asset")
    return JSONResponse({
        "@context": "http://iiif.io/api/presentation/3/context.json",
        "id": "http://127.0.0.1:8000/iiif/manifest",
        "type": "Manifest",
        "label": {"en": [f"{label} (C2PA signed)"]},
        "items": [{
            "id": "http://127.0.0.1:8000/iiif/canvas/1",
            "type": "Canvas",
            "width": 1920, "height": 1080,
            "items": [{
                "id": "http://127.0.0.1:8000/iiif/page/1",
                "type": "AnnotationPage",
                "items": [{
                    "id": "http://127.0.0.1:8000/iiif/anno/1",
                    "type": "Annotation",
                    "motivation": "painting",
                    "target": "http://127.0.0.1:8000/iiif/canvas/1",
                    "body": {"id": "http://127.0.0.1:8000/image", "type": "Image", "format": "image/jpeg"}
                }]
            }]
        }]
    })


@app.get("/verify")
def verify():
    # ensure c2patool present
    if not shutil.which("c2patool"):
        return JSONResponse({"status":"error","message":"c2patool not on PATH"}, status_code=500)
    path = "data/image.c2pa.jpg"
    if not os.path.exists(path):
        return JSONResponse({"status":"error","message":"signed asset not found"}, status_code=404)
    # run c2patool --detailed and return stdout
    try:
        out = subprocess.check_output(["c2patool", path, "--detailed"], text=True)
        return JSONResponse({"status":"ok","report": out})
    except subprocess.CalledProcessError as e:
        return JSONResponse({"status":"error","message": e.output or str(e)}, status_code=500)
