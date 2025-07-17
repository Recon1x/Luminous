import discord
from discord.ext import commands
import time
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

start_time = time.time()

@bot.command()
async def ping(ctx):
    """Shows bot statistics in an embed."""
    latency = bot.latency * 1000  # ms
    uptime = timedelta(seconds=int(time.time() - start_time))
    guild_count = len(bot.guilds)
    user_count = len(set(bot.get_all_members()))
    command_count = len(bot.commands)

    embed = discord.Embed(
        title="Luminous Statistics",
        color=discord.Color.from_rgb(173, 216, 230)
    )
    embed.add_field(name="Latency", value=f"{latency:.2f} ms", inline=True)
    embed.add_field(name="Bot Uptime", value=str(uptime), inline=True)
    embed.add_field(name="Total Servers", value=str(guild_count), inline=True)
    embed.add_field(name="Total Users", value=str(user_count), inline=True)
    embed.add_field(name="Functioning Commands", value=str(command_count), inline=True)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}!")
print(f"TOKEN LOADED: {TOKEN}")
print(f"Bot is online as {bot.user}!")
print(f"Guilds: {len(bot.guilds)}")
print(f"Users: {len(set(bot.get_all_members()))}")  
bot.run(TOKEN)
from discord.ext import commands
import discord
import sqlite3

@commands.command()
@commands.has_permissions(manage_channels=True)
async def close(ctx):
    """Close the current modmail ticket."""
    channel = ctx.channel

    # Connect to database
    conn = sqlite3.connect("modmail.db")
    cursor = conn.cursor()

    # Find user ID linked to this channel
    cursor.execute("SELECT user_id FROM modmail WHERE channel_id = ?", (str(channel.id),))
    result = cursor.fetchone()

    if not result:
        await ctx.send("⚠️ This channel is not a valid modmail ticket.")
        return

    user_id = int(result[0])
    user = ctx.guild.get_member(user_id) or await ctx.bot.fetch_user(user_id)

    # Remove from DB
    cursor.execute("DELETE FROM modmail WHERE user_id = ?", (str(user_id),))
    conn.commit()
    conn.close()

    # DM the user
    try:
        await user.send("🛑 Your modmail ticket has been closed.")
    except discord.Forbidden:
        pass  # User has DMs off

    # Delete the modmail channel
    await ctx.send("✅ Closing ticket...")
    await channel.delete()      