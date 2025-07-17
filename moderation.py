import discord
import sqldb # type: ignore
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required for kicking/banning/muting
import discord

intents = discord.Intents.default()
intents.message_content = True  # Required to read message text

bot = commands.Bot(command_prefix="!", intents=intents)


# ✅ On Ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ❌ Error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("❌ You don’t have permission to do that.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Missing argument.")
    else:
        raise error

# 👢 Kick command
@bot.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} was kicked. Reason: {reason or 'No reason provided'}")

# 🔨 Ban command
@bot.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} was banned. Reason: {reason or 'No reason provided'}")

# 🔇 Mute command (creates 'Muted' role if needed)
@bot.command()
@has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        # Create Muted role and disable sending messages
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False, speak=False)
    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f"🔇 {member} has been muted. Reason: {reason or 'No reason provided'}")

# 🔊 Unmute command
@bot.command()
@has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role and muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f"🔊 {member} has been unmuted.")
    else:
        await ctx.send("⚠️ That user is not muted.")

# ⚠️ Warn command
@bot.command()
@has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    await ctx.send(f"⚠️ {member.mention} has been warned. Reason: {reason or 'No reason provided'}")
    try:
        await member.send(f"You were warned in **{ctx.guild.name}**: {reason or 'No reason'}")
    except discord.Forbidden:
        await ctx.send("📪 Couldn't send DM to user.")

bot.run(TOKEN)