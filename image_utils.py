# image_utils.py
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
import pytz
import os

# =======================================================
#  ───  L A Y O U T   C O N S T A N T S  ─────────────────
#  (berdasarkan template 1221×687 px)
# =======================================================
TEMPLATE_W, TEMPLATE_H = 1221, 687

# Font
FONT_PATH = os.path.join("fonts", "LibertinusMath-Regular.ttf")

# Lingkaran avatar yang ada di template
#   └─ hasil deteksi: kiri-atas (487,217) ukuran 258×258
AVATAR_BOX = (487, 217, 745, 475)          # (left, top, right, bottom)
AVATAR_SIZE = (AVATAR_BOX[2] - AVATAR_BOX[0] - 6,
               AVATAR_BOX[3] - AVATAR_BOX[1] - 6)
AVATAR_POS  = (AVATAR_BOX[0] + 3, AVATAR_BOX[1] + 3)

# Posisi teks
NAME_POS        = (880, 82)                    # {user}
USERNUM_POS     = (TEMPLATE_W // 2, 560)       # {nomor join}
TIME_POS        = (60,  TEMPLATE_H - 32)       # jam
DATE_POS        = (TEMPLATE_W - 60, TEMPLATE_H - 32)  # tanggal

# Anchor helper
A_NAME = "lm"    # left-middle
A_NUM  = "mm"    # mid-middle
A_TIME = "lb"    # left-bottom
A_DATE = "rb"    # right-bottom

# Zona waktu
WIB = pytz.timezone("Asia/Jakarta")

# =======================================================
#  ───  H E L P E R S  ───────────────────────────────────
# =======================================================
def _crop_circle(img: Image.Image) -> Image.Image:
    """Mengubah citra jadi lingkaran (dengan alpha)."""
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, *img.size), fill=255)
    out = Image.new("RGBA", img.size)
    out.paste(img, (0, 0), mask)
    return out

def _fit_font(draw: ImageDraw.Draw, text: str, max_w: int, start: int = 44):
    """Perkecil font hingga muat max_w piksel."""
    size = start
    while size > 14:
        font = ImageFont.truetype(FONT_PATH, size)
        if draw.textlength(text, font=font) <= max_w:
            return font
        size -= 2
    return ImageFont.truetype(FONT_PATH, 14)

# =======================================================
#  ───  R E N D E R E R  ─────────────────────────────────
# =======================================================
async def _render(member, member_count: int, template_path: str) -> BytesIO:
    base = Image.open(template_path).convert("RGBA")

    # 1. Avatar -----------------------------------------------------------
    avatar_asset = member.display_avatar.replace(format="png", size=512)
    avatar_img   = Image.open(BytesIO(await avatar_asset.read())).convert("RGBA")
    avatar_img   = avatar_img.resize(AVATAR_SIZE, Image.LANCZOS)
    avatar_img   = _crop_circle(avatar_img)
    base.paste(avatar_img, AVATAR_POS, avatar_img)

    # 2. Waktu ------------------------------------------------------------
    now     = datetime.now(WIB)
    t_date  = now.strftime("%d/%m/%Y")
    t_time  = now.strftime("%H:%M:%S")

    # 3. Tulisan ----------------------------------------------------------
    draw       = ImageDraw.Draw(base)
    font_name  = _fit_font(draw, member.name.upper(), max_w=310, start=36)
    font_num   = ImageFont.truetype(FONT_PATH, 30)
    font_small = ImageFont.truetype(FONT_PATH, 22)

    draw.text(NAME_POS, member.name.upper(), font=font_name, anchor=A_NAME, fill="white")
    draw.text(USERNUM_POS, str(member_count), font=font_num, anchor=A_NUM, fill="white")
    draw.text(TIME_POS, t_time, font=font_small, anchor=A_TIME, fill="white")
    draw.text(DATE_POS, t_date, font=font_small, anchor=A_DATE, fill="white")

    # 4. Keluaran ---------------------------------------------------------
    buf = BytesIO()
    buf.name = "image.png"
    base.save(buf, "PNG")
    buf.seek(0)
    return buf

# =======================================================
#  ───  W R A P P E R S  ─────────────────────────────────
# =======================================================
async def generate_welcome_image(member, member_count: int):
    return await _render(member, member_count, os.path.join("assets", "welcome_template.png"))

async def generate_goodbye_image(member, member_count: int):
    return await _render(member, member_count, os.path.join("assets", "goodbye_template.png"))
