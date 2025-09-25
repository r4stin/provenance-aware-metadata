# Provenance-Aware Metadata for a Cultural Heritage Image (Phase 1)

This prototype demonstrates how cultural heritage images can be enriched with **standards-based metadata**, validated against **custom policy rules**, and embedded with **C2PA provenance claims**, before being served via APIs and a **IIIF manifest**.

It is developed as a **Phase 1 manual workflow**, with future phases focusing on automation and integration.

---

## ✨ Features

- **Metadata Modeling (JSON-LD)**  
  - Uses [Dublin Core (DC)](https://www.dublincore.org/specifications/dublin-core/), [PROV-O](https://www.w3.org/TR/prov-o/), and [Schema.org](https://schema.org/).  
  - Example record: *Leibniz University Hannover* image from Wikimedia Commons.  

- **Custom Policy Validation (SHACL)**  
  - Ensures metadata includes required elements: title, rights, provenance agent.  
  - Enforces Creative Commons license URLs and correct `xsd:dateTime` types.  

- **C2PA Provenance Embedding**  
  - Uses [c2patool](https://github.com/contentauth/c2pa-rs) to embed signed provenance (actions + rights) directly into the image file.  
  - Verifiable manifest stored within the asset itself.  

- **APIs & IIIF Delivery (FastAPI)**  
  - `/record` → serves metadata JSON-LD.  
  - `/image` → serves C2PA-signed image.  
  - `/iiif/manifest` → serves a [IIIF Presentation 3.0](https://iiif.io/api/presentation/3.0/) manifest referencing the signed image.  

---

## 🗂️ Repository Structure

```
data/                  # Input and output images
  image.jpg            # Original Wikimedia Commons image
  image.c2pa.jpg       # Image with embedded C2PA claim

metadata/
  record.jsonld        # Metadata record (DC, PROV-O, Schema.org)
  shacl.ttl            # SHACL shapes (validation rules)
  claim.json           # C2PA claim (actions + rights)

src/
  validate_metadata.py # Validate metadata against SHACL
  sign_c2pa.sh         # Embed provenance claim with c2patool
  api.py               # FastAPI app exposing metadata, image, IIIF

iiif/
  manifest.json        # Minimal IIIF Presentation 3.0 manifest
```

---

## ▶️ How to Run (Phase 1)

1. **Download the source image (Wikimedia Commons)**  
   ```bash
   mkdir -p data
   wget -O data/image.jpg "https://upload.wikimedia.org/wikipedia/commons/e/ea/Leibniz_University_Hannover.jpg"
   ```

2. **Validate metadata (SHACL policy check)**  
   ```bash
   python src/validate_metadata.py
   ```
   Expected output: `Conforms: True`.

3. **Embed provenance with C2PA**  
   ```bash
   bash src/sign_c2pa.sh
   ```
   Produces `data/image.c2pa.jpg` with embedded provenance.  
   Verify:  
   ```bash
   c2patool data/image.c2pa.jpg --info
   c2patool data/image.c2pa.jpg --detailed
   ```

4. **Run API & IIIF manifest**  
   ```bash
   uvicorn src.api:app --reload
   ```
   Open in browser:  
   - [http://127.0.0.1:8000/record](http://127.0.0.1:8000/record) → JSON-LD metadata  
   - [http://127.0.0.1:8000/image](http://127.0.0.1:8000/image) → signed image  
   - [http://127.0.0.1:8000/iiif/manifest](http://127.0.0.1:8000/iiif/manifest) → IIIF manifest  

   Try loading the manifest in a IIIF viewer (e.g., [Mirador](https://iiif.io/viewers/mirador/)).

---

## 🚧 Roadmap (Next Phases)

- **Phase 2: Automation**
  - Auto-generate JSON-LD metadata from image source.  
  - Auto-validate metadata via CI pipeline.  
  - Integrate SHACL rules into API responses.  

- **Phase 3: Integration**
  - Plug into real cultural heritage platforms (Europeana, Wikimedia Commons APIs).  
  - Expand metadata to cover PREMIS, EDM, and IIIF Annotations.  
  - Implement secure key management for C2PA (replace dev signer).  

- **Phase 4: Open Data & Reusability**
  - Provide packaged Docker deployment.  
  - Publish open APIs and example datasets.  

---

## 📜 License

- The demo code: MIT License.  
- Image: *Leibniz University Hannover* (CC BY-SA 3.0), from [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Leibniz_University_Hannover.jpg).

---

## 🔖 Versioning

- **v0.1 (this branch)**: Manual workflow prototype.  
- Future releases (`v0.2+`) will add automation, CI/CD validation, and production-ready signing.
