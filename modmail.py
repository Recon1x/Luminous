import discord
from discord.ext import commands
import sqlite3
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CATEGORY_NAME = "Modmail"

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.guilds = True
intents.members = True

import discord

intents = discord.Intents.default()
intents.message_content = True  # Required to read message text

bot = commands.Bot(command_prefix="!", intents=intents)


conn = sqlite3.connect("modmail.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS modmail (user_id TEXT PRIMARY KEY, channel_id TEXT)")
conn.commit()
conn.close()

def get_channel_id(user_id):
    conn = sqlite3.connect("modmail.db")
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id FROM modmail WHERE user_id = ?", (str(user_id),))
    result = cursor.fetchone()
    conn.close()
    return int(result[0]) if result else None

def set_modmail_channel(user_id, channel_id):
    conn = sqlite3.connect("modmail.db")
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO modmail (user_id, channel_id) VALUES (?, ?)", (str(user_id), str(channel_id)))
    conn.commit()
    conn.close()

def remove_modmail(user_id):
    conn = sqlite3.connect("modmail.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM modmail WHERE user_id = ?", (str(user_id),))
    conn.commit()
    conn.close()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} | ID: {bot.user.id}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 📨 Incoming DM
    if isinstance(message.channel, discord.DMChannel):
        guild = bot.get_guild(GUILD_ID)
        if not guild:
            return

        category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
        if not category:
            category = await guild.create_category(CATEGORY_NAME)

        channel_id = get_channel_id(message.author.id)
        channel = guild.get_channel(channel_id) if channel_id else None

        # Create channel if needed
        if channel is None:
            channel = await category.create_text_channel(name=f"modmail-{message.author.name}".replace(" ", "-"))
            await channel.send(f"📬 **New Modmail from {message.author}** (ID: `{message.author.id}`)")
            set_modmail_channel(message.author.id, channel.id)

        await channel.send(f"**{message.author}:** {message.content}")
        await message.channel.send("📨 Your message has been sent to the moderators, please be pateint whilst you wait for a response.")

    # 🗣️ Message in modmail channel
    elif message.guild:
        if message.channel.category and message.channel.category.name == CATEGORY_NAME:
            for user_id, channel_id in fetch_all_modmail():
                if int(channel_id) == message.channel.id:
                    user = await bot.fetch_user(int(user_id))
                    if user:
                        await user.send(f"**Mod Response:** {message.content}")
                    break

def fetch_all_modmail():
    conn = sqlite3.connect("modmail.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, channel_id FROM modmail")
    results = cursor.fetchall()
    conn.close()
    return results

@bot.command()
@commands.has_permissions(manage_channels=True)
async def close(ctx):
    """Close a modmail session"""
    if ctx.channel.category and ctx.channel.category.name == CATEGORY_NAME:
        for user_id, channel_id in fetch_all_modmail():
            if int(channel_id) == ctx.channel.id:
                remove_modmail(user_id)
                user = await bot.fetch_user(int(user_id))
                await user.send("🛑 Your modmail session has been closed.")
                await ctx.send("✅ Modmail closed. Deleting channel...")
                await ctx.channel.delete()
                return
        await ctx.send("❌ No modmail found to close.")
    else:
        await ctx.send("❌ This command can only be used in modmail channels.")

bot.run(TOKEN)
