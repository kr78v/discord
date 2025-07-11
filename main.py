import discord
import asyncio
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que : {bot.user}")

# Warn
warns = {}

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="Aucune raison fournie"):
    user_id = str(member.id)
    warns.setdefault(user_id, []).append(reason)
    await ctx.send(f"⚠️ {member.mention} a été averti pour : {reason}")

# Clear
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {len(deleted)-1} messages supprimés.", delete_after=3)

# Mute (kick temporaire + réinvitation)
@bot.command()
@commands.has_permissions(kick_members=True)
async def mute(ctx, member: discord.Member, duration: int):
    try:
        await ctx.send(f"{member.mention} a été temporairement kick pour {duration} minute(s).")
        await member.kick(reason="Mute temporaire")
        await asyncio.sleep(duration * 60)
        invite = await ctx.channel.create_invite(max_age=86400, max_uses=1, reason="Réinvitation auto après mute")
        try:
            await member.send(f"Ton mute est terminé. Tu peux revenir avec ce lien : {invite.url}")
        except:
            await ctx.send(f"Impossible d’envoyer le lien à {member.name} (MP désactivés).")
    except Exception as e:
        await ctx.send(f"Erreur : {e}")

# Ban
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune raison fournie"):
    if member == ctx.author:
        return await ctx.send("❌ Tu ne peux pas te bannir toi-même.")
    if ctx.author.top_role <= member.top_role:
        return await ctx.send("❌ Tu ne peux pas bannir un membre avec un rôle égal ou supérieur.")
    if not ctx.guild.me.guild_permissions.ban_members:
        return await ctx.send("❌ Je n’ai pas la permission de bannir.")
    try:
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member.mention} a été banni pour : {reason}")
    except Exception as e:
        await ctx.send(f"❌ Erreur : {e}")

# Automod
bad_words = ["idiot", "merde", "fdp", "bite", "enculé", "connard", "pute", "salope", "salopard", "enculée", "enculés"]

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.isupper() and len(message.content) > 5:
        await message.delete()
        await message.channel.send(f"❗ {message.author.mention}, évite les majuscules !", delete_after=5)
        return

    content_lower = message.content.lower()
    if any(word in content_lower for word in bad_words):
        await message.delete()
        await message.channel.send(f"🚫 {message.author.mention}, langage interdit !", delete_after=5)
        return

    await bot.process_commands(message)

# Démarrage
token = os.environ.get('TOKEN')
if not token:
    print("❌ TOKEN non trouvé dans les variables d'environnement.")
else:
    bot.run(token)
