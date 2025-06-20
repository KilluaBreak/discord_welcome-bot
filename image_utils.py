from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
import pytz

# Timezone Indonesia WIB
WIB = pytz.timezone("Asia/Jakarta")

# Path ke font Kingthings Exeter
FONT_PATH = "fonts/Kingthings_Exeter.ttf"

# Ukuran & Posisi berdasarkan gambar 803x451
AVATAR_SIZE = (180, 180)
AVATAR_POSITION = (310, 120)
NAME_POSITION = (400, 40)
USER_NUMBER_POSITION = (400, 330)
DATE_POSITION = (40, 370)
TIME_POSITION = (740, 370)

# Buat crop foto jadi lingkaran
def crop_circle(image):
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + image.size, fill=255)
    result = Image.new("RGBA", image.size)
    result.paste(image, (0, 0), mask)
    return result

# Fungsi utama generate gambar
async def generate_image(member, member_count, base_path):
    base = Image.open(base_path).convert("RGBA")

    # Ambil avatar user
    avatar_asset = member.display_avatar.replace(format="png", size=256)
    avatar_bytes = await avatar_asset.read()
    avatar = Image.open(BytesIO(avatar_bytes)).convert("RGBA")
    avatar = avatar.resize(AVATAR_SIZE)
    avatar = crop_circle(avatar)
    base.paste(avatar, AVATAR_POSITION, avatar)

    # Font
    font_big = ImageFont.truetype(FONT_PATH, 36)
    font_medium = ImageFont.truetype(FONT_PATH, 28)
    font_small = ImageFont.truetype(FONT_PATH, 20)

    # Data waktu
    now = datetime.now(WIB)
    tanggal = now.strftime("%d/%m/%Y")
    jam = now.strftime("%H:%M:%S")

    draw = ImageDraw.Draw(base)

    # Nama user
    draw.text(NAME_POSITION, member.name.upper(), font=font_big, anchor="mm", fill="white")
    # Nomor ke berapa
    draw.text(USER_NUMBER_POSITION, f"#{member_count}", font=font_medium, anchor="mm", fill="white")
    # Tanggal dan Jam
    draw.text(DATE_POSITION, f"Tanggal: {tanggal}", font=font_small, fill="white")
    draw.text(TIME_POSITION, f"Jam: {jam}", font=font_small, anchor="rd", fill="white")

    # Output hasil
    output = BytesIO()
    output.name = "image.png"
    base.save(output, format="PNG")
    output.seek(0)
    return output

# Fungsi untuk welcome
async def generate_welcome_image(member, member_count):
    return await generate_image(member, member_count, "assets/welcome_template.png")

# Fungsi untuk goodbye
async def generate_goodbye_image(member, member_count):
    return await generate_image(member, member_count, "assets/goodbye_template.png")
