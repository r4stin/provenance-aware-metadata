from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import json
import os

app = FastAPI(title="ECHOLOT Provenance Demo")

@app.get("/record")
def get_record():
    with open("metadata/record.jsonld") as f:
        return JSONResponse(json.load(f))

@app.get("/image")
def get_image():
    return FileResponse("data/image.c2pa.jpg", media_type="image/jpeg")

# --- IIIF helpers ---
@app.get("/iiif/manifest")
def get_manifest():
    return FileResponse("iiif/manifest.json", media_type="application/json")

@app.get("/iiif/canvas/{cid}")
def get_canvas(cid: str):
    # simple stub to please some IIIF viewers; optional
    return JSONResponse({"id": f"http://127.0.0.1:8000/iiif/canvas/{cid}", "type": "Canvas"})

@app.get("/iiif/page/{pid}")
def get_page(pid: str):
    return JSONResponse({"id": f"http://127.0.0.1:8000/iiif/page/{pid}", "type": "AnnotationPage"})

@app.get("/iiif/anno/{aid}")
def get_anno(aid: str):
    return JSONResponse({"id": f"http://127.0.0.1:8000/iiif/anno/{aid}", "type": "Annotation"})
