import datetime
import discord
from discord.ext import commands
import sqlite3 as sql
from os import listdir, popen
from os.path import isfile
from Tools.var import errorcolor
from pickle import load
import koreanbots

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
bot.remove_command("help")
cooldown = {}
using_cmd = []
with open('koreanbots_token.bin', 'rb') as f:
    koreanbots_token = load(f)
BOT = koreanbots.Client(bot, koreanbots_token)


@bot.event
async def on_ready():
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
    # 유저가 업로드한 밈들 보낼 웹훅
    with conn:
        with open("backup.sql", "w") as f:
            for line in conn.iterdump():
                f.write("%s\n" % line)
    conn.close()
    await (bot.get_channel(852767243360403497)).send(
        str(datetime.datetime.utcnow() + datetime.timedelta(hours=9)),
        file=discord.File("backup.sql"),
    )
    print("ready")
    for file in [j if isfile("Cogs/" + j) else None for j in listdir("Cogs")]:
        if file is not None:
            bot.load_extension(f"Cogs.{file[:-3]}")
            print(f"Cogs.{file[:-3]}")
    bot.load_extension("jishaku")
    print("jishaku")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(
            "ㅉhelp",
            type=discord.ActivityType.listening,
            start=datetime.datetime.utcnow(),
        ),
    )
    await bot.get_channel(852767242704650290).send("켜짐")


@bot.before_invoke
async def before_invoke(ctx):
    if ctx.author.id in bot.owner_ids:
        ctx.command.reset_cooldown(ctx)
    using_cmd.append(ctx.author.id)


@bot.after_invoke
async def after_invoke(ctx):
    using_cmd.remove(ctx.author.id)


@bot.event
async def on_message(message):
    if not message.content.startswith(bot.command_prefix):
        return
    conn = sql.connect("memebot.db", isolation_level=None)
    cur = conn.cursor()
    cur.execute("SELECT * FROM blacklist WHERE id=?", (message.author.id,))
    if cur.fetchall():
        return
    conn.close()
    if message.author.id in using_cmd or (
        message.author.id in cooldown
        and (datetime.datetime.utcnow() - cooldown[message.author.id]).seconds < 3
    ):
        return
    await bot.process_commands(message)
    cooldown[message.author.id] = datetime.datetime.utcnow()


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


bot.run(token)
