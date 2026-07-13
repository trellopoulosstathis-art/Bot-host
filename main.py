import discord
from discord.ext import commands
import asyncio
import os
import time

# ==================== BOT SETUP ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.invites = True
intents.reactions = True
intents.moderation = True

bot = commands.Bot(command_prefix="%", intents=intents)

anti_nuke_enabled = False
auto_role_id = None

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')

@bot.event
async def on_disconnect():
    print("⚠️ Bot disconnected.")

@bot.event
async def on_resumed():
    print("✅ Bot reconnected.")

async def send_embed(ctx, title, description, color=0x00ff00):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=f"Requested by {ctx.author}")
    return await ctx.send(embed=embed)

@bot.command()
async def mc(ctx):
    total = ctx.guild.member_count
    humans = len([m for m in ctx.guild.members if not m.bot])
    bots = len([m for m in ctx.guild.members if m.bot])
    embed = discord.Embed(title="👥 Member Count", color=0x00ff00)
    embed.add_field(name="Total Members", value=f"**{total}**", inline=False)
    embed.add_field(name="Humans", value=f"**{humans}**", inline=True)
    embed.add_field(name="Bots", value=f"**{bots}**", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def si(ctx):
    guild = ctx.guild
    humans = len([m for m in guild.members if not m.bot])
    bots = len([m for m in guild.members if m.bot])
    embed = discord.Embed(title=f"📊 {guild.name} Info", color=0x00aaff)
    embed.add_field(name="Created", value=guild.created_at.strftime("%B %d, %Y"), inline=False)
    embed.add_field(name="Total Members", value=f"**{guild.member_count}**", inline=True)
    embed.add_field(name="Humans", value=f"**{humans}**", inline=True)
    embed.add_field(name="Bots", value=f"**{bots}**", inline=True)
    embed.add_field(name="Channels", value=f"**{len(guild.channels)}**", inline=True)
    embed.add_field(name="Roles", value=f"**{len(guild.roles)}**", inline=True)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def create(ctx, *items):
    if not items:
        await send_embed(ctx, "Usage", "%create general memes Welcome: rules announcements", 0x00ff00)
        return
    await send_embed(ctx, "🔨 Creating...", f"Creating **{len(items)}** items...", 0x00ff00)
    created = 0
    current_cat = None
    for item in items:
        item = item.strip()
        try:
            if item.endswith(":"):
                current_cat = await ctx.guild.create_category(item[:-1])
            else:
                if current_cat:
                    await ctx.guild.create_text_channel(item, category=current_cat)
                else:
                    await ctx.guild.create_text_channel(item)
                created += 1
        except:
            pass
    await send_embed(ctx, "✅ Creation Done", f"**{created}** channels created.", 0x00ff00)

@bot.command()
@commands.has_permissions(administrator=True)
async def revamp(ctx, *items):
    if not items:
        items = ["general", "memes", "lounge", "rules", "announcements"]
    await send_embed(ctx, "🔄 Revamp Starting...", "Deleting old channels...", 0xffaa00)
    for ch in list(ctx.guild.channels):
        if ch.id != ctx.channel.id:
            try: await ch.delete()
            except: pass
    created = 0
    current_cat = None
    for item in items:
        item = item.strip()
        try:
            if item.endswith(":"):
                current_cat = await ctx.guild.create_category(item[:-1])
            else:
                if current_cat:
                    await ctx.guild.create_text_channel(item, category=current_cat)
                else:
                    await ctx.guild.create_text_channel(item)
                created += 1
        except:
            pass
    await send_embed(ctx, "✅ Revamp Complete", f"Created **{created}** channels.", 0x00ff00)

@bot.command()
@commands.has_permissions(administrator=True)
async def lock(ctx, state: str = "true"):
    state = state.lower()
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    if state in ["true", "on", "1"]:
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await send_embed(ctx, "🔒 Channel Locked", "Only admins can send messages now.", 0xff0000)
    else:
        overwrite.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await send_embed(ctx, "🔓 Channel Unlocked", "Everyone can send messages again.", 0x00ff00)

@bot.command()
@commands.has_permissions(administrator=True)
async def antinuke(ctx, state: str = "true"):
    global anti_nuke_enabled
    state = state.lower()
    if state in ["true", "on", "1"]:
        anti_nuke_enabled = True
        await send_embed(ctx, "🛡️ Anti-Nuke Enabled", "Basic protection activated.", 0x00ff00)
    else:
        anti_nuke_enabled = False
        await send_embed(ctx, "🛡️ Anti-Nuke Disabled", "Protection turned off.", 0xff0000)

@bot.command()
@commands.has_permissions(administrator=True)
async def autorole(ctx, role_id: int = None):
    global auto_role_id
    if role_id:
        auto_role_id = role_id
        role = ctx.guild.get_role(role_id)
        await send_embed(ctx, "✅ Auto Role Set", f"New members will get {role.name if role else role_id}", 0x00ff00)
    else:
        await send_embed(ctx, "Usage", "%autorole <role_id>", 0xff0000)

@bot.event
async def on_member_join(member):
    if auto_role_id:
        role = member.guild.get_role(auto_role_id)
        if role:
            try:
                await member.add_roles(role)
            except:
                pass

@bot.command()
@commands.has_permissions(administrator=True)
async def roleall(ctx, role_id: int):
    role = ctx.guild.get_role(role_id)
    if not role:
        return await send_embed(ctx, "❌ Error", "Role not found.", 0xff0000)
    await send_embed(ctx, "📢 Roleall Started", f"Giving {role.name} to all members...", 0x00aaff)
    count = 0
    for member in ctx.guild.members:
        if role not in member.roles:
            try:
                await member.add_roles(role)
                count += 1
                await asyncio.sleep(0.5)
            except:
                continue
    await send_embed(ctx, "✅ Roleall Done", f"Added role to **{count}** members.", 0x00ff00)

@bot.command()
async def memberroles(ctx):
    await send_embed(ctx, "📋 Loading...", "Fetching all members and roles...", 0x00aaff)
    data = []
    for member in ctx.guild.members:
        if member.bot: continue
        roles = [r.name for r in member.roles if r.name != "@everyone"]
        role_str = ", ".join(roles) if roles else "No roles"
        data.append(f"**{member}** ({member.id})\nRoles: {role_str}\n")
    chunk = ""
    for line in data:
        if len(chunk) + len(line) > 1900:
            await ctx.send(chunk)
            chunk = line
            await asyncio.sleep(1)
        else:
            chunk += line + "\n"
    if chunk:
        await ctx.send(chunk)
    await send_embed(ctx, "✅ Done", f"Listed {len(data)} members.", 0x00ff00)

@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await send_embed(ctx, "✅ Banned", f"**{member}** banned.", 0xff0000)

@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await send_embed(ctx, "✅ Kicked", f"**{member}** kicked.", 0xff0000)

@bot.command()
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    await member.edit(mute=True)
    await send_embed(ctx, "✅ Muted", f"**{member}** muted.", 0xffaa00)

@bot.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member, *, reason="No reason"):
    await send_embed(ctx, "⚠️ Warn", f"**{member}** warned.", 0xffff00)

@bot.command()
@commands.has_permissions(administrator=True)
async def flood(ctx, user_id: int, *, message=None):
    user = await bot.fetch_user(user_id)
    if not user:
        return await send_embed(ctx, "❌ Error", "User not found.", 0xff0000)
    if not message:
        message = "flooded nga"
    await send_embed(ctx, "🚨 DM Flood", f"Sending 150 messages to {user}...", 0xff0000)
    sent = 0
    for _ in range(150):
        try:
            await user.send(message)
            sent += 1
            await asyncio.sleep(0.7)
        except:
            break
    await send_embed(ctx, "✅ Flood Done", f"Sent **{sent}** messages to {user}", 0x00ff00)

@bot.command()
@commands.has_permissions(administrator=True)
async def spam(ctx, amount: int, *, message=None):
    if amount < 1: amount = 1
    if amount > 300: amount = 300
    if not message: message = "@everyone"
    channels = [ch for ch in ctx.guild.text_channels if ch.permissions_for(ctx.guild.me).send_messages]
    tasks = [ch.send(message) for ch in channels for _ in range(amount)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    sent = sum(1 for r in results if not isinstance(r, Exception))
    await send_embed(ctx, "✅ Spam Done", f"Sent **{sent}** messages", 0x00ff00)

@bot.command()
@commands.has_permissions(administrator=True)
async def massflood(ctx, *, message=None):
    if not message:
        message = "@everyone nga leave before data gets leaked cuz I have them"
    warning = await send_embed(ctx, "🚨 MASSFLOOD WARNING", f"Message: {message[:100]}...\nReact with ✅", 0xff0000)
    await warning.add_reaction("✅")
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == warning.id
    try:
        await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        return await send_embed(ctx, "Cancelled", "Massflood cancelled.", 0xff0000)
    try: await warning.delete()
    except: pass
    await send_embed(ctx, "🚨 MASSFLOOD STARTED", "Sending 150 DMs to everyone...", 0xff0000)
    members = [m for m in ctx.guild.members if not m.bot]
    total = 0
    for member in members:
        for _ in range(150):
            try:
                await member.send(message)
                total += 1
                await asyncio.sleep(0.7)
            except:
                break
    await send_embed(ctx, "✅ MASSFLOOD COMPLETE", f"Sent **{total}** DMs!", 0xff0000)

@bot.command()
@commands.has_permissions(administrator=True)
async def kuni(ctx):
    warning = await send_embed(ctx, "☢️ KUNI WARNING",
                              "This will delete **EVERYTHING**.\nReact with ✅ to confirm.", 0xff0000)
    await warning.add_reaction("✅")
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == warning.id
    try:
        await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        return await send_embed(ctx, "⏰ Timed Out", "Kuni cancelled.", 0xff0000)
    for ch in list(ctx.guild.channels):
        try: await ch.delete()
        except: pass
    for role in ctx.guild.roles:
        if role.name != "@everyone":
            try: await role.delete()
            except: pass
    spam_msg = "@everyone nga leave before data gets leaked cuz I have them"
    channel_list = []
    created = 0
    for i in range(10):
        try:
            cat = await ctx.guild.create_category(f"nvked bitch {i+1}")
            await asyncio.sleep(0.5)
            for _ in range(50):
                try:
                    ch = await ctx.guild.create_text_channel("get-nvkes-ngas", category=cat)
                    channel_list.append(ch)
                    created += 1
                    for _ in range(5):
                        try:
                            await ch.send(spam_msg)
                            await asyncio.sleep(0.3)
                        except:
                            break
                    await asyncio.sleep(0.3)
                except:
                    continue
        except:
            continue
    for _ in range(10):
        tasks = [ch.send(spam_msg) for ch in channel_list]
        await asyncio.gather(*tasks, return_exceptions=True)
        await asyncio.sleep(1.5)

while True:
    try:
        print("🔄 Starting bot...")
        bot.run(os.getenv("TOKEN"), reconnect=True)
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        print("🔄 Restarting in 5 seconds...")
        time.sleep(5)
