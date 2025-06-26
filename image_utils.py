from __future__ import annotations

import os
from datetime import datetime
from io import BytesIO

import pytz
from PIL import Image, ImageDraw, ImageFont

# ==========================================================
#  ▶ GENERAL CONFIG
# ==========================================================
FONT_PATH: str = os.path.join("fonts", "LibertinusMath-Regular.ttf")
TIMEZONE = pytz.timezone("Asia/Jakarta")  # WIB

TEMPLATES: dict[str, str] = {
    "welcome": os.path.join("assets", "welcome_template.png"),
    "goodbye": os.path.join("assets", "goodbye_template.png"),
}

SIZES = {
    "avatar": (250, 250),  # width, height
}

# Koordinat titik (x, y)
LAYOUT = {
    "avatar": (550, 217),   # kiri‑atas lingkaran avatar
    "name": (750, 82),      # username
    "number": (680, 630),   # nomor urut
    "time": (60, 635),      # jam
    "date": (1290, 635),    # tanggal
}

# Anchor untuk setiap teks (lihat Pillow docs)
ANCHORS = {
    "name": "lm",   # left middle
    "number": "mm", # middle
    "time": "lb",   # left bottom
    "date": "rb",   # right bottom
}

FONT_SIZES = {
    "name": 36,
    "number": 34,
    "small": 35,
}

# ==========================================================
#  ▶ HELPERS
# ==========================================================

def _load_font(px: int) -> ImageFont.FreeTypeFont:
    """Coba load font custom, fallback ke default jika gagal."""
    try:
        return ImageFont.truetype(FONT_PATH, px)
    except OSError:
        return ImageFont.load_default()


def _crop_circle(img: Image.Image) -> Image.Image:
    """Kembalikan versi bulat dari gambar (RGBA)."""
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, *img.size), fill=255)
    out = Image.new("RGBA", img.size)
    out.paste(img, (0, 0), mask)
    return out


def _fit_text(draw: ImageDraw.ImageDraw, text: str, max_width: int, start_px: int) -> ImageFont.FreeTypeFont:
    """Perkecil font sampai lebar teks ≤ max_width."""
    size = start_px
    while size > 14:
        font = _load_font(size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 2
    return _load_font(14)

# ==========================================================
#  ▶ CORE RENDERER
# ==========================================================

async def _render(kind: str, member, member_count: int) -> BytesIO:
    """Buat gambar berdasarkan `kind` (welcome/goodbye)."""

    template_path = TEMPLATES[kind]
    base = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(base)

    # --- AVATAR --------------------------------------------------------
    avatar_asset = member.display_avatar.replace(format="png", size=512)
    avatar_raw = await avatar_asset.read()
    avatar_img = Image.open(BytesIO(avatar_raw)).convert("RGBA")

    avatar_img = avatar_img.resize(SIZES["avatar"], Image.LANCZOS)
    avatar_img = _crop_circle(avatar_img)
    base.paste(avatar_img, LAYOUT["avatar"], avatar_img)

    # --- WAKTU ---------------------------------------------------------
    now = datetime.now(TIMEZONE)
    str_date = now.strftime("%d/%m/%Y")
    str_time = now.strftime("%H:%M:%S")

    # --- TEKS ----------------------------------------------------------
    name_font = _fit_text(draw, member.name.upper(), 310, FONT_SIZES["name"])

    draw.text(LAYOUT["name"], member.name.upper(), font=name_font,
              fill="white", anchor=ANCHORS["name"])

    draw.text(LAYOUT["number"], str(member_count), font=_load_font(FONT_SIZES["number"]),
              fill="white", anchor=ANCHORS["number"])

    small_font = _load_font(FONT_SIZES["small"])
    draw.text(LAYOUT["time"], str_time, font=small_font, fill="white", anchor=ANCHORS["time"])
    draw.text(LAYOUT["date"], str_date, font=small_font, fill="white", anchor=ANCHORS["date"])

    # --- OUTPUT --------------------------------------------------------
    buf = BytesIO()
    buf.name = f"{kind}.png"
    base.save(buf, "PNG")
    buf.seek(0)
    return buf

# ==========================================================
#  ▶ PUBLIC API
# ==========================================================

async def generate_welcome_image(member, member_count: int) -> BytesIO:  # noqa: N802
    """Gambar Welcome"""
    return await _render("welcome", member, member_count)


async def generate_goodbye_image(member, member_count: int) -> BytesIO:  # noqa: N802
    """Gambar Goodbye"""
    return await _render("goodbye", member, member_count)
