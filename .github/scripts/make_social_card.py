"""Build images/social-card.jpg, the 1200x630 image shown when the site is shared.

Run by .github/workflows/social-card.yml whenever the profile changes in Pages CMS,
so the card always matches your name, role, status, photo and cover.
"""
import io
import subprocess
import urllib.request

import yaml
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
BG = (13, 17, 23)
OUT = "images/social-card.jpg"


def font_file(pattern, fallback):
    """Resolve a font with fontconfig; fall back to DejaVu (always present on Ubuntu)."""
    try:
        path = subprocess.run(["fc-match", "-f", "%{file}", pattern], capture_output=True, text=True).stdout.strip()
        if path and pattern.split(":")[0].replace(" ", "").lower() in path.replace(" ", "").lower():
            return path
    except FileNotFoundError:
        pass
    return fallback


DEJAVU = "/usr/share/fonts/truetype/dejavu/"
BOLD = font_file("Noto Sans:bold", DEJAVU + "DejaVuSans-Bold.ttf")
REG = font_file("Noto Sans:regular", DEJAVU + "DejaVuSans.ttf")
MONO = font_file("JetBrains Mono:regular", DEJAVU + "DejaVuSansMono.ttf")


def load_image(src):
    if src.startswith("http"):
        with urllib.request.urlopen(src, timeout=30) as r:
            return Image.open(io.BytesIO(r.read()))
    return Image.open(src.lstrip("/"))


def main():
    prof = yaml.safe_load(open("_data/profile.yml", encoding="utf-8")) or {}
    card = Image.new("RGB", (W, H), BG)

    # Background: the cover photo, blurred and darkened, fading to solid on the left.
    if prof.get("cover"):
        c = load_image(prof["cover"]).convert("RGB")
        r = max(W / c.width, H / c.height)
        c = c.resize((int(c.width * r) + 1, int(c.height * r) + 1), Image.LANCZOS)
        left, top = (c.width - W) // 2, (c.height - H) // 2
        c = c.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(2))
        card = Image.blend(c, card, 0.80)
    scrim = Image.new("L", (W, H))
    sd = ImageDraw.Draw(scrim)
    for x in range(W):
        sd.line([(x, 0), (x, H)], fill=int(255 * max(0.0, min(1.0, 1.15 - x / W))))
    card = Image.composite(Image.new("RGB", (W, H), BG), card, scrim)
    d = ImageDraw.Draw(card)

    # Avatar: the Pages CMS photo, or the GitHub profile picture.
    AV = 230
    av = load_image(prof.get("photo") or "https://github.com/a1if.png?size=460").convert("RGB")
    s = min(av.size)
    av = av.crop(((av.width - s) // 2, (av.height - s) // 2, (av.width + s) // 2, (av.height + s) // 2))
    av = av.resize((AV, AV), Image.LANCZOS)
    mask = Image.new("L", (AV * 4, AV * 4))
    ImageDraw.Draw(mask).ellipse([0, 0, AV * 4, AV * 4], fill=255)
    mask = mask.resize((AV, AV), Image.LANCZOS)
    ax, ay = 80, (H - AV) // 2 - 20
    d.ellipse([ax - 5, ay - 5, ax + AV + 5, ay + AV + 5], fill=(61, 68, 77))
    card.paste(av, (ax, ay), mask)

    # Text: name, role (wrapped at " · "), status pill, site address.
    tx = ax + AV + 56
    maxw = W - tx - 70
    y = ay
    name_font = ImageFont.truetype(BOLD, 70)
    d.text((tx, y), prof.get("name", "Alif Tasbir"), font=name_font, fill=(240, 246, 252))
    y += 98
    role_font = ImageFont.truetype(MONO, 25)
    lines, line = [], ""
    for part in str(prof.get("role", "")).split(" · "):
        trial = part if not line else f"{line} · {part}"
        if d.textlength(trial, font=role_font) <= maxw:
            line = trial
        else:
            lines.append(line)
            line = part
    lines.append(line)
    for l in lines[:3]:
        d.text((tx, y), l, font=role_font, fill=(201, 209, 217))
        y += 38
    status = " · ".join(str(prof.get("status", "")).split(" · ")[:2])
    if status:
        y += 18
        sf = ImageFont.truetype(REG, 24)
        tw = d.textlength(status, font=sf)
        d.rounded_rectangle([tx, y, tx + tw + 58, y + 46], radius=23, outline=(61, 68, 77), width=2, fill=(21, 27, 35))
        d.ellipse([tx + 20, y + 17, tx + 32, y + 29], fill=(63, 185, 80))
        d.text((tx + 42, y + 8), status, font=sf, fill=(201, 209, 217))
    d.line([(80, H - 92), (W - 80, H - 92)], fill=(48, 54, 61), width=2)
    d.text((80, H - 76), "a1if.github.io", font=ImageFont.truetype(MONO, 30), fill=(68, 147, 248))

    card.save(OUT, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"wrote {OUT} using {BOLD}, {REG}, {MONO}")


if __name__ == "__main__":
    main()
