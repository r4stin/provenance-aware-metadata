# Provenance-Aware Metadata (Phase 3)

This project demonstrates a general workflow for **provenance-aware metadata** on digital assets:
- **Model** metadata in **JSON-LD** (Dublin Core, PROV-O, Schema.org)
- **Validate** with **SHACL** (custom policy rules: EDM, PREMIS)
- **Sign** assets with **C2PA** (actions + rights)
- **Serve** via **FastAPI** and a **dynamic IIIF Presentation 3.0** manifest

---

## ✨ What’s new in Phase 3 (v0.3)

- **Fetch from Wikimedia Commons** and auto-populate `metadata/source.yml`  
  → `python src/cli.py build-from-commons --title "File:Leibniz_University_Hannover.jpg"`
- **Richer standards & policies**: extended **SHACL** shapes to cover **EDM** and **PREMIS** (e.g., event typing & dateTime checks)
- **Verification endpoint**: `/verify` returns **c2patool --detailed** output for the signed image
- **Publish container to GHCR**: GitHub Actions builds & pushes on `v*` tags → `ghcr.io/<owner>/<repo>:v0.3`
- **Tests in CI**: basic pytest to ensure build + validation keep passing
- **Builder normalizations**: clean creator (no HTML), ISO date, CC license URL trailing `/`, clearer `prov:wasDerivedFrom` (binary)

---

## 🗂️ Repository Structure

```
data/                    # Input/output assets
  image.jpg              # Original image (fetched or provided)
  image.c2pa.jpg         # Signed image (generated)

metadata/
  source.yml             # Source fields (auto from Commons or manual)
  record.jsonld          # Built JSON-LD (do not hand-edit)
  shacl.ttl              # SHACL shapes (EDM + PREMIS rules)
  claim.json             # C2PA claim (actions + rights)

src/
  fetch_commons.py       # Fetch & map Commons metadata + download image
  build_metadata.py      # Build JSON-LD from source.yml (normalizes fields)
  validate_metadata.py   # SHACL validation
  sign_c2pa.sh           # Signing (env-driven with dev fallback)
  api.py                 # FastAPI app (record, image, dynamic IIIF, /verify)
  cli.py                 # CLI: build/validate/sign/serve/info/build-from-commons

.github/
  workflows/validate.yml       # CI: SHACL + tests on push/PR
  workflows/docker-publish.yml # CI: publish Docker image to GHCR on tags

tests/
  test_build_and_validate.py   # Basic build+validate test

Makefile                 # make build | validate | sign | serve | info | all
requirements.txt         # Runtime deps (incl. pytest)
environment.yml          # Conda environment (local dev)
Dockerfile               # Containerized API service
```

---

## 🔧 Setup

### A) Conda (local dev)
```bash
conda env create -f environment.yml
conda activate Provenance-Aware-Metadata
```

### B) Install `c2patool` (CLI)
Choose one:

**Prebuilt (recommended)**
```bash
# download release for your OS (e.g., v0.9.12), then:
sudo mv c2patool /usr/local/bin/
c2patool -V
```

**Cargo (pin version)**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
cargo install --locked c2patool --version 0.9.12
~/.cargo/bin/c2patool -V
```

---

## ▶️ Run

**A) Build from Commons (Phase 3)**
```bash
# fetch & normalize source.yml and image.jpg, then build & validate
python src/cli.py build-from-commons --title "File:Leibniz_University_Hannover.jpg"
```
If your network blocks the image CDN, you can skip the binary fetch:
```bash
SKIP_DOWNLOAD=1 python src/cli.py build-from-commons --title "File:Leibniz_University_Hannover.jpg"
# or prefetch with IPv4:
wget -4 -O data/image.jpg "https://upload.wikimedia.org/wikipedia/commons/e/ea/Leibniz_University_Hannover.jpg"
```

**B) Manual workflow (Phase 2 style)**
```bash
python src/cli.py build
python src/cli.py validate          # expect: Conforms: True
python src/cli.py sign              # or: bash src/sign_c2pa.sh
python src/cli.py serve             # open http://127.0.0.1:8000
```

Endpoints:
- `/record` → JSON-LD metadata  
- `/image`  → signed image (falls back to unsigned if missing)  
- `/iiif/manifest` → dynamic IIIF Presentation 3.0  
- `/verify` → C2PA verification report (c2patool `--detailed`)

**Makefile shortcuts**
```bash
make build
make validate
make sign
make serve
# or everything (pipeline except docker):
make all
```

---

## 🐋 Docker

**Build**
```bash
docker build -t provenance-metadata:dev .
```

**Run**
```bash
# image baked in container
docker run --rm -p 8000:8000 provenance-metadata:dev

# OR mount host data folder (to use local signed file)
docker run --rm -p 8000:8000 -v "$(pwd)/data:/app/data" provenance-metadata:dev
```

**Run from GHCR (after tagging v0.3)**
```bash
docker run --rm -p 8000:8000 ghcr.io/<owner>/<repo>:v0.3
```

---

## 🚧 CI
- **Validation workflow**: `.github/workflows/validate.yml` runs SHACL + tests on push/PR to `main`/`dev`.  
- **Publish to GHCR**: `.github/workflows/docker-publish.yml` builds & pushes on tags `v*`.

Badge:
![Validate Metadata](https://github.com/<your-username>/<your-repo>/actions/workflows/validate.yml/badge.svg)

---

## 🚧 Roadmap

- **Phase 1 (done)**  
  - Manual JSON-LD modeling  
  - SHACL validation  
  - C2PA (dev key)
  - Static IIIF

- **Phase 2 (done)**  
  - CLI workflow (build/validate/sign/serve/info)  
  - YAML→JSON-LD
  - Dynamic IIIF 
  - CI validation
  - Env-driven signing (fallback)
  - Dockerized API  

- **Phase 3 (this release)**  
  - Fetch from Commons
  - Extended EDM/PREMIS SHACL
  - `/verify` endpoint 
  - GHCR publish
  - Tests in CI
  - Builder normalizations (creator/date/license/provenance)

- **Phase 4 (planned)**  
  - Integrations (Europeana/Zenodo)
  - Secure key mgmt (remote signer/KMS)
  - More datasets & examples
  - Packaging for production

---

## 📜 License
- Code: MIT  
- Image: *Leibniz University Hannover* (CC BY-SA 3.0), from [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Leibniz_University_Hannover.jpg).

---

## 🔖 Versioning
- **v0.1** — Manual prototype (metadata, SHACL, C2PA, static IIIF).  
- **v0.2** — Automation & containerization (CLI, YAML→JSON-LD, dynamic IIIF, API fallback, CI, Docker, env-driven signing).
- **v0.3** — Integrations & policies (Commons fetch, PREMIS/EDM, `/verify`, GHCR, tests)