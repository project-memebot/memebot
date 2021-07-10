import datetime
import discord
from discord.ext import commands, tasks
import sqlite3 as sql
from os import listdir
from os.path import isfile
from Tools.var import errorcolor
from pickle import load
import koreanbots
from itertools import cycle
from keep_alive import keep_alive


with open("token.bin", "rb") as tokenfile:
    token = load(tokenfile)
mentions = discord.AllowedMentions.all()
mentions.replied_user = False
bot = commands.Bot(
    command_prefix=("ㅉ", "짤 "),
    allowed_mentions=mentions,
    owner_ids=(745848200195473490,),
    intents=discord.Intents.all(),
)
cooldown = {}
using_cmd = []
with open("koreanbots_token.bin", "rb") as f:
    koreanbots_token = load(f)
BOT = koreanbots.Client(bot, koreanbots_token)

presences = []


@bot.event
async def on_ready():
    global presences
    presences = cycle(
        [
            discord.Activity(
                name="짤",
                type=discord.ActivityType.watching,
                large_image_url=bot.user.avatar_url,
            ),
            discord.Activity(
                name="ㅉhelp",
                type=discord.ActivityType.listening,
                large_image_url=bot.user.avatar_url,
            ),
            discord.Activity(
                name=f"{len(bot.guilds)}서버",
                type=discord.ActivityType.playing,
                large_image_url=bot.user.avatar_url,
            ),
            discord.Activity(
                name="http://invite.memebot.kro.kr",
                type=discord.ActivityType.watching,
                large_image_url=bot.user.avatar_url,
            ),
            discord.Activity(
                name="http://support.memebot.kro.kr",
                type=discord.ActivityType.watching,
                large_image_url=bot.user.avatar_url,
            ),
            discord.Activity(
                name="http://koreanbots.kro.kr",
                type=discord.ActivityType.watching,
                large_image_url=bot.user.avatar_url,
            ),
        ]
    )
    conn = sql.connect("memebot.db", isolation_level=None)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS usermeme (id INTEGER PRIMARY KEY, uploader_id INTEGER, title text, url text)"
    )
    # 유저가 업로드한 밈들 id/설명 등 매칭
    cur.execute(
        "CREATE TABLE IF NOT EXISTS blacklist (id INTEGER PRIMARY KEY, reason text)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS webhooks (url text PRIMARY KEY, guild_id INTEGER)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS customprefix (guild_id INTEGER PRIMARY KEY, prefix text)"
    )
    # 유저가 업로드한 밈들 보낼 웹훅
    with conn:
        with open("backup.sql", "w", encoding="UTF-8") as backupfile:
            for line in conn.iterdump():
                backupfile.write(f"{line}\n")
    conn.close()
    await (bot.get_channel(852767243360403497)).send(
        str(datetime.datetime.utcnow() + datetime.timedelta(hours=9)),
        file=discord.File("backup.sql"),
    )
    print("ready")
    cogs = [j if isfile("Cogs/" + j) else "" for j in listdir("Cogs")]
    cogs.sort()
    for file in cogs:
        if file != "":
            bot.load_extension(f"Cogs.{file[:-3]}")
            print(f"Cogs.{file[:-3]}")
    bot.load_extension("jishaku")
    print("jishaku")
    change_presence.start()
    await bot.get_channel(852767242704650290).send("켜짐")


@tasks.loop(seconds=5)
async def change_presence():
    await bot.change_presence(activity=next(presences))


@bot.before_invoke
async def before_invoke(ctx):
    using_cmd.append(ctx.author.id)
    if ctx.author.id in bot.owner_ids and ctx.author.id in cooldown:
        del cooldown[ctx.author.id]


@bot.after_invoke
async def after_invoke(ctx):
    using_cmd.remove(ctx.author.id)


@bot.event
async def on_message(message):
    conn = sql.connect("memebot.db", isolation_level=None)
    cur = conn.cursor()
    cur.execute("SELECT * FROM blacklist WHERE id=?", (message.author.id,))
    if cur.fetchall():
        return
    cur.execute("SELECT * FROM customprefix WHERE guild_id=?", (message.guild.id,))
    data = cur.fetchall()
    if data:
        if not message.content.startswith(data[0][1]):
            return None
        message.content = "ㅉ" + "".join(message.content.split(data[0][1])[1:])
    else:
        if not message.content.startswith(bot.command_prefix):
            return None
    conn.close()
    if message.author.id in bot.owner_ids:
        return await bot.process_commands(message)
    if message.author.id in using_cmd:
        return await message.channel.send("현재 실행중인 명령어를 먼저 끝내 주세요.")
    if (
        message.author.id in cooldown
        and (datetime.datetime.utcnow() - cooldown[message.author.id]).seconds < 3
    ):
        retry_after = datetime.datetime.utcnow() - cooldown[message.author.id]
        return await message.channel.send(
            f"현재 쿨타임에 있습니다.\n{retry_after.seconds}초 후 다시 시도해 주세요"
        )
    await bot.process_commands(message)
    cooldown[message.author.id] = datetime.datetime.utcnow()

'''
@bot.event
async def on_command_error(ctx, error):
    if type(error) in [
        commands.CommandNotFound,
        commands.NotOwner,
        commands.DisabledCommand,
        commands.MissingPermissions,
        commands.CheckFailure,
        commands.MissingRequiredArgument,
    ]:
        return

    embed = discord.Embed(
        title="오류", description=f"`{ctx.message.content}`", color=errorcolor
    )
    embed.add_field(
        name="오류 발생자", value=f"{ctx.author} ({ctx.author.id})\n{ctx.author.mention}"
    )
    embed.add_field(
        name="오류 발생지",
        value=f"{ctx.guild.name} ({ctx.guild.id})\n{ctx.channel.name} ({ctx.channel.id})",
    )
    embed.add_field(name="오류 내용", value=f"```py\n{error}```")
    await (bot.get_channel(852767242704650290)).send(embed=embed)
'''
keep_alive()
bot.remove_command("help")
bot.run(token)
