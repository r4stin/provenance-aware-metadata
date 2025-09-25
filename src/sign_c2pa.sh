#!/usr/bin/env bash
set -euo pipefail

INPUT="data/image.jpg"
OUTPUT="data/image.c2pa.jpg"
MANIFEST="metadata/claim.json"

# 1) Ensure input image exists
[ -f "$INPUT" ] || { echo "❌ Missing $INPUT"; exit 1; }

# 2) Minimal manifest if missing (uses built-in test cert/key)
if [ ! -f "$MANIFEST" ]; then
  echo "ℹ️  Creating minimal $MANIFEST ..."
  mkdir -p metadata
  cat > "$MANIFEST" <<'JSON'
{
  "title": "Provenance for demo-image-001",
  "claim_generator": "echolot-demo/0.1",
  "assertions": [
    {
      "label": "c2pa.actions",
      "data": { "actions": [
        { "action": "c2pa.created",
          "when": "2025-09-25T12:00:00Z",
          "softwareAgent": "Library XYZ Digitization Lab" }
      ]}
    },
    {
      "label": "c2pa.rights",
      "data": {
        "rights": "CC BY 4.0",
        "url": "https://creativecommons.org/licenses/by/4.0/"
      }
    }
  ]
}
JSON
fi

echo "✍️  Embedding C2PA claim with built-in signer..."
c2patool "$INPUT" \
  --manifest "$MANIFEST" \
  --output "$OUTPUT"

echo "✅ Signed image saved as $OUTPUT"
echo "🔍 Verification info:"
c2patool "$OUTPUT" --info
