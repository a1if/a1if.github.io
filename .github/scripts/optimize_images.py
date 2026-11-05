"""Shrink large images in images/ so the site stays fast.

Run by .github/workflows/optimize-images.yml whenever images change (e.g. uploads from
Pages CMS). Files keep their names, so links in Pages CMS keep working.
- JPEG / PNG / WebP larger than MAX_SIDE px or MAX_BYTES are resized and re-encoded.
- Camera metadata (EXIF, including any GPS location) is removed.
- GIFs and SVGs are left alone (animated GIFs would lose their animation).
"""
import io
import os
import sys

from PIL import Image, ImageOps

MAX_SIDE = 2000          # longest edge in pixels
MAX_BYTES = 500 * 1024   # anything bigger than this gets re-encoded
ROOT = sys.argv[1] if len(sys.argv) > 1 else "images"

changed = []
for dirpath, _, files in os.walk(ROOT):
    for name in files:
        ext = name.lower().rsplit(".", 1)[-1]
        if ext not in ("jpg", "jpeg", "png", "webp"):
            continue
        path = os.path.join(dirpath, name)
        before = os.path.getsize(path)
        with Image.open(path) as im:
            has_exif = bool(im.getexif())
            too_big = max(im.size) > MAX_SIDE
            if not (too_big or before > MAX_BYTES or has_exif):
                continue
            img = ImageOps.exif_transpose(im)
            img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
            buf = io.BytesIO()
            if ext in ("jpg", "jpeg"):
                img.convert("RGB").save(buf, "JPEG", quality=82, optimize=True, progressive=True)
            elif ext == "png":
                img.save(buf, "PNG", optimize=True)
            else:
                img.save(buf, "WEBP", quality=82, method=6)
        data = buf.getvalue()
        if len(data) >= before and not (too_big or has_exif):
            continue  # re-encoding wouldn't make it smaller; keep the original
        with open(path, "wb") as f:
            f.write(data)
        after = len(data)
        changed.append(f"{path}: {before // 1024} KB -> {after // 1024} KB")

print("\n".join(changed) if changed else "No images needed optimising.")
