import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN missing from .env")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("✅ Available commands:", list(bot.commands))

@bot.command()
@commands.is_owner()
async def reboot(ctx):
    await ctx.send("🔁 Rebooting bot...")
    await bot.change_presence(activity=discord.Game(name="🔁 Rebooting..."))
    await bot.close()
    os.execv(sys.executable, [sys.executable] + sys.argv)

bot.run(TOKEN)
