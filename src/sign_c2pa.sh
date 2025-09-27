#!/usr/bin/env bash
set -euo pipefail

INPUT="data/image.jpg"
OUTPUT="data/image.c2pa.jpg"
MANIFEST="metadata/claim.json"

command -v c2patool >/dev/null 2>&1 || { echo "❌ c2patool not found"; exit 1; }
[ -f "$INPUT" ] || { echo "❌ Missing $INPUT"; exit 1; }
[ -f "$MANIFEST" ] || { echo "❌ Missing $MANIFEST"; exit 1; }

USE_ENV=false
if [[ -n "${C2PA_SIGN_CERT:-}" && -n "${C2PA_PRIVATE_KEY:-}" ]]; then
  if [[ -f "$C2PA_SIGN_CERT" && -f "$C2PA_PRIVATE_KEY" ]]; then
    USE_ENV=true
  else
    echo "⚠️  Env vars set but files not found:"
    [[ -f "$C2PA_SIGN_CERT" ]] || echo "   - missing $C2PA_SIGN_CERT"
    [[ -f "$C2PA_PRIVATE_KEY" ]] || echo "   - missing $C2PA_PRIVATE_KEY"
    echo "   Falling back to dev signer."
  fi
fi

if $USE_ENV; then
  echo "🔐 Signing with env-provided cert/key..."
  TMPMF=$(mktemp)
  jq --arg cert "$C2PA_SIGN_CERT" --arg key "$C2PA_PRIVATE_KEY" \
     '. + {alg:"es256", sign_cert:$cert, private_key:$key}' "$MANIFEST" > "$TMPMF"
  c2patool "$INPUT" -m "$TMPMF" -o "$OUTPUT"
  rm -f "$TMPMF"
else
  echo "ℹ️  Using c2patool built-in dev signer (development only)"
  c2patool "$INPUT" -m "$MANIFEST" -o "$OUTPUT"
fi

echo "✅ Signed: $OUTPUT"
c2patool "$OUTPUT" --info
