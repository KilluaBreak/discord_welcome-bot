from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from datetime import datetime, timezone, timedelta

FONT_PATH = "fonts/RobotoSlab-Bold.ttf"
WELCOME_TEMPLATE = "templates/welcome_base.webp"
GOODBYE_TEMPLATE = "templates/goodbye_base.png"
WIB = timezone(timedelta(hours=7))

def crop_circle(image):
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + image.size, fill=255)
    result = Image.new("RGBA", image.size)
    result.paste(image, (0, 0), mask)
    return result

async def generate_image(member, member_count, base_path):
    base = Image.open(base_path).convert("RGBA")

    avatar_asset = member.display_avatar.replace(format="png", size=256)
    avatar_bytes = await avatar_asset.read()
    avatar = Image.open(BytesIO(avatar_bytes)).convert("RGBA")
    avatar = avatar.resize((230, 230))
    avatar = crop_circle(avatar)
    base.paste(avatar, (base.width//2 - 90, base.height//2 - 90), avatar)

    draw = ImageDraw.Draw(base)
    font_main = ImageFont.truetype(FONT_PATH, 44)
    font_small = ImageFont.truetype(FONT_PATH, 32)
    font_count = ImageFont.truetype(FONT_PATH, 38)

    now = datetime.now(WIB)
    tanggal = now.strftime("%d/%m/%Y")
    jam = now.strftime("%H:%M:%S")
    username = member.name

    draw.text((base.width//2, 40), f"user #{member_count}", font=font_count, anchor="mm", fill="#cc00ff")
    draw.text((base.width//2, base.height - 55), username, font=font_main, anchor="mm", fill="white")
    draw.text((30, base.height - 45), {tanggal}", font=font_small, fill="white")
    draw.text((base.width - 30, base.height - 40), {jam}", font=font_small, anchor="rd", fill="white")

    output = BytesIO()
    output.name = "welcome.png"
    base.save(output, format="PNG")
    output.seek(0)
    return output

async def generate_welcome_image(member, member_count):
    return await generate_image(member, member_count, WELCOME_TEMPLATE)

async def generate_goodbye_image(member, member_count):
    return await generate_image(member, member_count, GOODBYE_TEMPLATE)
