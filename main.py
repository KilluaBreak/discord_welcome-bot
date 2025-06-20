import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from image_utils import generate_welcome_image, generate_goodbye_image

load_dotenv()
TOKEN = os.getenv("TOKEN")
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID"))
GOODBYE_CHANNEL_ID = int(os.getenv("GOODBYE_CHANNEL_ID"))

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} sudah aktif!")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    member_count = member.guild.member_count
    image = await generate_welcome_image(member, member_count)
    file = discord.File(fp=image, filename="welcome.png")
    embed = discord.Embed(title="Welcome!", description=f"{member.mention} selamat datang!", color=discord.Color.purple())
    embed.set_image(url="attachment://welcome.png")
    await channel.send(embed=embed, file=file)

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(GOODBYE_CHANNEL_ID)
    member_count = member.guild.member_count
    image = await generate_goodbye_image(member, member_count)
    file = discord.File(fp=image, filename="goodbye.png")
    embed = discord.Embed(title="Goodbye!", description=f"{member.name} telah keluar.", color=discord.Color.red())
    embed.set_image(url="attachment://goodbye.png")
    await channel.send(embed=embed, file=file)

bot.run(TOKEN)
