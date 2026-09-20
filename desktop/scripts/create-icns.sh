#!/bin/bash
# Script to convert a 1024x1024 PNG icon to Apple's .icns format
# Usage: ./create-icns.sh path/to/icon.png output.icns

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: ./create-icns.sh <input-1024x1024.png> <output.icns>"
    exit 1
fi

INPUT_PNG=$1
OUTPUT_ICNS=$2
ICONSET_DIR="temp.iconset"

mkdir -p "$ICONSET_DIR"

# Generate the required icon sizes
sips -z 16 16     "$INPUT_PNG" --out "$ICONSET_DIR/icon_16x16.png"
sips -z 32 32     "$INPUT_PNG" --out "$ICONSET_DIR/icon_16x16@2x.png"
sips -z 32 32     "$INPUT_PNG" --out "$ICONSET_DIR/icon_32x32.png"
sips -z 64 64     "$INPUT_PNG" --out "$ICONSET_DIR/icon_32x32@2x.png"
sips -z 128 128   "$INPUT_PNG" --out "$ICONSET_DIR/icon_128x128.png"
sips -z 256 256   "$INPUT_PNG" --out "$ICONSET_DIR/icon_128x128@2x.png"
sips -z 256 256   "$INPUT_PNG" --out "$ICONSET_DIR/icon_256x256.png"
sips -z 512 512   "$INPUT_PNG" --out "$ICONSET_DIR/icon_256x256@2x.png"
sips -z 512 512   "$INPUT_PNG" --out "$ICONSET_DIR/icon_512x512.png"
sips -z 1024 1024 "$INPUT_PNG" --out "$ICONSET_DIR/icon_512x512@2x.png"

# Convert iconset to icns
iconutil -c icns "$ICONSET_DIR" -o "$OUTPUT_ICNS"

# Cleanup
rm -rf "$ICONSET_DIR"

echo "Successfully created $OUTPUT_ICNS"
