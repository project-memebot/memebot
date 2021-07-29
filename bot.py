import datetime
from itertools import cycle
from os import listdir
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
)
import logging
from shutil import copy2
from discord_components import DiscordComponents
from discord_slash import SlashCommand
import aiofiles


with open("token.bin", "rb") as tokenfile:
    token = load(tokenfile)
mentions = discord.AllowedMentions.all()
mentions.replied_user = False
bot = commands.Bot(
    command_prefix=get_prefix,
    allowed_mentions=mentions,
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
        # 유저가 업로드한 밈들 id/설명 등 매칭
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

    copy2("memebot.db", "backup.db")
    await (bot.get_channel(852767243360403497)).send(
        str(datetime.datetime.utcnow() + datetime.timedelta(hours=9)),
        file=discord.File("backup.db"),
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
    DiscordComponents(bot)
    change_presence.start()
    update_koreanbots.start()
    await update_koreanbots()
    await bot.get_channel(852767242704650290).send("켜짐")


@tasks.loop(seconds=7)
async def change_presence():
    await bot.change_presence(activity=next(presences))


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
    async with aiofiles.open("cmd.log", "a") as f:
        await f.write(
            f"{ctx.author}({ctx.author.id})\n{ctx.message.content}\n{ctx.message.created_at}"
        )


@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
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
