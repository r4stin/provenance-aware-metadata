#!/usr/bin/env bash
set -euo pipefail

INPUT="data/image.jpg"
OUTPUT="data/image.c2pa.jpg"
MANIFEST="metadata/claim.json"

command -v c2patool >/dev/null 2>&1 || { echo "❌ c2patool not found"; exit 1; }
[ -f "$INPUT" ] || { echo "❌ Missing $INPUT"; exit 1; }
[ -f "$MANIFEST" ] || { echo "❌ Missing $MANIFEST"; exit 1; }

if [[ -n "${C2PA_SIGN_CERT:-}" && -n "${C2PA_PRIVATE_KEY:-}" ]]; then
  CERT_PATH="$(python - <<'PY'
import os, sys
p=os.environ.get("C2PA_SIGN_CERT","")
print(os.path.abspath(p))
PY
)"
  KEY_PATH="$(python - <<'PY'
import os, sys
p=os.environ.get("C2PA_PRIVATE_KEY","")
print(os.path.abspath(p))
PY
)"
  TMPMF=$(mktemp)
  jq --arg cert "$CERT_PATH" --arg key "$KEY_PATH" \
     '. + {alg:"es256", sign_cert:$cert, private_key:$key}' "$MANIFEST" > "$TMPMF"
  c2patool "$INPUT" -m "$TMPMF" -o "$OUTPUT" -f

  rm -f "$TMPMF"
else
  echo "ℹ️ Using c2patool built-in dev signer (for development only)"
  c2patool "$INPUT" -m "$MANIFEST" -o "$OUTPUT" -f

fi

c2patool "$OUTPUT" --info
