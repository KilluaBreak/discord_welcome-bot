from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
import pytz

# Timezone Indonesia WIB
WIB = pytz.timezone("Asia/Jakarta")

# Path ke font dan ukuran gambar
FONT_PATH = "fonts/LibertinusMath-Regular.ttf"
AVATAR_SIZE = (250, 250)
AVATAR_POSITION = (486, 200)  # Tengah atas
NAME_POSITION = (840, 60)     # Username di kanan atas
USER_NUMBER_POSITION = (486, 480)  # Tengah kotak ungu
DATE_POSITION = (1150, 670)   # Pojok kanan bawah
TIME_POSITION = (40, 670)     # Pojok kiri bawah

# Fungsi potong gambar jadi lingkaran
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
    avatar_asset = member.display_avatar.replace(format="png", size=512)
    avatar_bytes = await avatar_asset.read()
    avatar = Image.open(BytesIO(avatar_bytes)).convert("RGBA")
    avatar = avatar.resize(AVATAR_SIZE, Image.LANCZOS)
    avatar = crop_circle(avatar)
    base.paste(avatar, AVATAR_POSITION, avatar)

    # Waktu sekarang
    now = datetime.now(WIB)
    tanggal = now.strftime("%d/%m/%Y")
    jam = now.strftime("%H:%M:%S")

    # Font
    font_name = ImageFont.truetype(FONT_PATH, 32)
    font_medium = ImageFont.truetype(FONT_PATH, 28)
    font_small = ImageFont.truetype(FONT_PATH, 22)

    draw = ImageDraw.Draw(base)

    # Tulis username (huruf besar)
    draw.text(NAME_POSITION, member.name.upper(), font=font_name, fill="white", anchor="ra")

    # Tulis nomor join
    draw.text(USER_NUMBER_POSITION, f"{member_count}", font=font_medium, fill="white", anchor="mm")

    # Tulis tanggal dan jam
    draw.text(DATE_POSITION, f"{tanggal}", font=font_small, fill="white", anchor="rd")
    draw.text(TIME_POSITION, f"{jam}", font=font_small, fill="white", anchor="ld")

    # Hasilkan file output
    output = BytesIO()
    output.name = "image.png"
    base.save(output, format="PNG")
    output.seek(0)
    return output

# Fungsi welcome
async def generate_welcome_image(member, member_count):
    return await generate_image(member, member_count, "assets/welcome_template.png")

# Fungsi goodbye
async def generate_goodbye_image(member, member_count):
    return await generate_image(member, member_count, "assets/goodbye_template.png")
