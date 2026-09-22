#!/usr/bin/env python3
"""Generate desktop/build/icon.ico from source artwork.

macOS .icns is generated with scripts/create-icns.sh (requires macOS
sips/iconutil). Windows .ico has no native macOS tooling, so this script
uses Pillow to write a multi-resolution .ico instead.

Usage:
    pip install pillow
    python3 scripts/generate-icons.py [source.png] [output.ico]

Defaults: ../assets/ability_glyphs_pbr.jpg -> build/icon.ico
Source should ideally be square and >= 256x256 (1024x1024 preferred).
"""
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required: pip install pillow", file=sys.stderr)
    sys.exit(1)

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / ".." / "assets" / "ability_glyphs_pbr.jpg"
DST = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / ".." / "build" / "icon.ico"

if not SRC.exists():
    print(f"ERROR: source artwork not found: {SRC}", file=sys.stderr)
    sys.exit(1)

img = Image.open(SRC).convert("RGB")
if img.width < 256 or img.height < 256:
    print(f"WARNING: source is only {img.width}x{img.height}; 1024x1024 preferred.", file=sys.stderr)
DST.parent.mkdir(parents=True, exist_ok=True)
img.save(DST, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print(f"Wrote {DST} ({DST.stat().st_size} bytes, 6 layers)")
