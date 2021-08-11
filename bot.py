from datetime import datetime, timedelta
from itertools import cycle
from os import listdir, chdir
from os.path import isfile
from pickle import load
import aiosqlite as aiosql
import aiohttp
import discord
import koreanbots
from discord.ext import commands, tasks
from tool import (
    errorcolor,
    get_prefix,
    UserOnBlacklist,
    NotJoined,
)
import logging
from shutil import copy2
from discord_components import DiscordComponents
import aiofiles


if __import__("platform").system() == "Windows":
    chdir("python/meme-bot")

with open("token.bin", "rb") as tokenfile:
    token = load(tokenfile)
bot = commands.Bot(
    command_prefix=get_prefix,
    allowed_mentions=discord.AllowedMentions.none(),
    owner_ids=(745848200195473490,),
    intents=discord.Intents.all(),
    strip_after_prefix=True,
)
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
                name="http://koreanbots.memebot.kro.kr",
                type=discord.ActivityType.watching,
                large_image_url=bot.user.avatar_url,
            ),
        ]
    )
    async with aiosql.connect("memebot.db", isolation_level=None) as cur:
        await cur.execute(
            "CREATE TABLE IF NOT EXISTS usermeme (id INTEGER PRIMARY KEY, uploader_id INTEGER, title text, url text)"
        )
        await cur.execute(
            "CREATE TABLE IF NOT EXISTS blacklist (id INTEGER PRIMARY KEY, reason text)"
        )
        await cur.execute(
            "CREATE TABLE IF NOT EXISTS webhooks (url text PRIMARY KEY, guild_id INTEGER)"
        )
        await cur.execute(
            "CREATE TABLE IF NOT EXISTS customprefix (guild_id INTEGER PRIMARY KEY, prefix text)"
        )
        # 유저가 업로드한 밈들 보낼 웹훅
        await cur.execute("CREATE TABLE IF NOT EXISTS joined (id INTEGER PRIMARY KEY)")
        # 가입된 유저 목록
    for file in [i for i in listdir("Cogs") if i.endswith(".py")]:
        bot.load_extension(f"Cogs.{file[:-3]}")
        print(f"Cogs.{file[:-3]}")
    bot.load_extension("jishaku")
    await backupdb()
    await update_koreanbots()
    print("ready")
    print("jishaku")
    DiscordComponents(bot)
    change_presence.start()
    update_koreanbots.start()
    backupdb.start()
    await bot.get_channel(852767242704650290).send("켜짐")


@tasks.loop(seconds=10)
async def change_presence():
    await bot.change_presence(activity=next(presences))


@tasks.loop(hours=4)
async def backupdb():
    copy2("memebot.db", "backup.db")
    await (bot.get_channel(852767243360403497)).send(
        str(datetime.utcnow() + timedelta(hours=9)),
        files=[discord.File("backup.db"), discord.File("cmd.log")],
    )


@tasks.loop(minutes=30)
async def update_koreanbots():
    with open("koreanbots_token.bin", "rb") as f:
        koreanbots_token = load(f)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://koreanbots.dev/api/v2/bots/852802390083371028/stats",
            data={"servers": len(bot.guilds), "shards": 1},
            headers={"Authorization": koreanbots_token},
        ) as res:
            if res.status != 200:
                print(res)
                await (bot.get_channel(852767242704650290)).send(
                    f"Koreanbots API 요청에 실패함\n{await res.json()}"
                )


@bot.before_invoke
async def before_invoke(ctx):
    if ctx.author.id in bot.owner_ids:
        return
    async with aiosql.connect("memebot.db") as cur:
        async with cur.execute(
            "SELECT * FROM blacklist WHERE id=?", (ctx.author.id,)
        ) as result:
            result = await result.fetchall()
            if result:
                await ctx.reply(f"{ctx.author} 님은 `{result[0][1]}`의 사유로 차단되셨습니다.")
                raise UserOnBlacklist
    if ctx.command.name != "가입":
        async with aiosql.connect("memebot.db") as cur:
            async with cur.execute(
                "SELECT * FROM joined WHERE id=?", (ctx.author.id,)
            ) as result:
                result = await result.fetchall()
                if result:
                    await ctx.reply("가입 명령어를 통해 사용 권한을 얻으세요.")
                    raise NotJoined
    async with aiofiles.open("cmd.log", "a") as f:
        await f.write(
            f"{ctx.author}({ctx.author.id})\n{ctx.message.content}\n{ctx.message.created_at}"
        )


@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        return
    if str(bot.user) in [i.name + "#" + i.discriminator for i in message.mentions]:
        await message.channel.send(
            f"{message.guild} 서버의 접두사는 `{await get_prefix(_bot=bot, message=message)}`입니다."
        )
    await bot.process_commands(message)


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
    if isinstance(error, commands.CommandOnCooldown):
        return await ctx.send(f"{round(error.retry_after, 2)}초 후 다시 시도해 주세요")
    elif isinstance(error, commands.MaxConcurrencyReached):
        return await ctx.send("현재 실행중인 명령어를 먼저 마쳐 주세요")
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
    await ctx.message.add_reaction("⚠️")


bot.remove_command("help")
bot.run(token)
