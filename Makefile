.PHONY: all build validate sign serve info

all: build validate sign serve

build:
	python src/build_metadata.py

validate:
	python src/validate_metadata.py

sign:
	bash src/sign_c2pa.sh

serve:
	uvicorn src.api:app --reload

info:
	c2patool data/image.c2pa.jpg --info
