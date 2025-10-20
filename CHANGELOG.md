All notable changes to this project will be documented here.

## [v0.3] - 2025-10-20
### Added
- **Wikimedia Commons integration**: `src/fetch_commons.py` and CLI `build-from-commons` to fetch metadata + image and auto-build/validate.
- **Richer SHACL policies**: extended shapes for **EDM** and **PREMIS** (event struct & `xsd:dateTime` checks).
- **Verification endpoint**: `/verify` returns `c2patool --detailed` report for the signed image.
- **GHCR publish workflow**: `.github/workflows/docker-publish.yml` builds and pushes Docker image on `v*` tags.
- **Tests in CI**: `tests/test_build_and_validate.py` with pytest; workflow runs tests after validation.
- **Builder normalizations**: strip HTML from creator, ISO-8601 datetime, ensure CC license URL trailing `/`, and use the binary URL as `prov:wasDerivedFrom`.

### Changed
- `README.md` updated for Phase 3 (Commons fetch, PREMIS/EDM rules, `/verify`, GHCR usage, tests).
- `api.py` extended to expose `/verify`.
- `build_metadata.py` improved normalization and provenance clarity.

## [v0.2] - 2025-09-27
### Added
- CLI (`src/cli.py`) with commands: `build`, `validate`, `sign`, `serve`, `info`.
- `metadata/source.yml` and `src/build_metadata.py` to auto-generate `metadata/record.jsonld`.
- Dynamic IIIF manifest served by the API from `record.jsonld`.
- **API fallback**: `/image` now serves `data/image.jpg` if `data/image.c2pa.jpg` is missing.
- Dockerfile for containerized FastAPI service (optional `.dockerignore` recommended).
- Example CI workflow (`.github/workflows/validate.yml`) for SHACL validation on push/PR.
- Env-driven C2PA signing in `src/sign_c2pa.sh` (uses `C2PA_SIGN_CERT`/`C2PA_PRIVATE_KEY` when present) with safe fallback to the tool’s dev signer.
- Makefile with common targets (`build`, `validate`, `sign`, `serve`, `info`, `all`).

### Changed
- README updated to reflect Phase 2 usage (CLI, dynamic IIIF, API fallback, Docker, CI).

### Removed
- Static `iiif/manifest.json` (replaced by dynamic `/iiif/manifest` route). *(If you kept the static file, ignore this line.)*

## [v0.1] - 2025-09-??
- Initial manual prototype: JSON-LD metadata, SHACL validation, C2PA signing (dev signer), static IIIF, FastAPI endpoints.