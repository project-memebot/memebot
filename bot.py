import asyncio
from datetime import datetime, timedelta
from itertools import cycle
from os import listdir, remove
from pickle import load
from shutil import copy2
from koreanbots import Koreanbots
import aiofiles
import aiohttp
import aiosqlite as aiosql
import discord
from discord.ext import commands, tasks
from discord_components import DiscordComponents, Select, SelectOption
from tool import (
    OnTestMode,
    UserOnBlacklist,
    embedcolor,
    errorcolor,
    get_prefix,
)

test = __import__("platform").system() == "Windows"

with open("testertoken.bin" if test else "token.bin", "rb") as tokenfile:
    token = load(tokenfile)
bot = commands.Bot(
    command_prefix="ㅉ!" if test else get_prefix,
    allowed_mentions=discord.AllowedMentions.none(),
    owner_ids=(745848200195473490, 443691722543726592, 726350177601978438),
    intents=discord.Intents.all(),
    strip_after_prefix=True,
)
presences = []
component = DiscordComponents(bot)
if not test:
    with open('koreanbots_token.bin', 'rb') as kbtoken:
        kbtoken = load(kbtoken)
    koreanbots = Koreanbots(bot, kbtoken, run_task=True)


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
            "CREATE TABLE IF NOT EXISTS usermeme (id INTEGER PRIMARY KEY, uploader_id INTEGER, title text, url text,\
date text, stars INTEGER)"
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
    print("jishaku")
    print("ready")
    if not test:
        await backupdb()
        
        backupdb.start()
        change_presence.start()
    else:
        for i in bot.commands:
            i.enabled = True
    await bot.get_channel(852767242704650290).send(("테봇 " if test else "") + "켜짐")


@tasks.loop(seconds=10)
async def change_presence():
    await bot.change_presence(activity=next(presences))


@tasks.loop(hours=4)
async def backupdb():
    copy2("memebot.db", "backup.db")
    await (bot.get_channel(852767243360403497)).send(
        str(datetime.utcnow() + timedelta(hours=9)),
        file=discord.File("backup.db"),
    )


@bot.event
async def on_guild_join(guild):
    embed = discord.Embed(title="서버 참여", color=embedcolor)
    embed.add_field(name="서버 정보", value=f"{guild.name} ({guild.id})")
    embed.set_thumbnail(url=guild.icon_url)
    embed.set_footer(icon_url=guild.owner.avatar_url, text=f"{guild.owner}")
    await (bot.get_channel(852767242704650290)).send(embed=embed)


@bot.event
async def on_guild_remove(guild):
    embed = discord.Embed(title="서버 퇴장", color=embedcolor)
    embed.add_field(name="서버 정보", value=f"{guild.name} ({guild.id})")
    embed.set_thumbnail(url=guild.icon_url)
    embed.set_footer(icon_url=guild.owner.avatar_url, text=f"{guild.owner}")
    await (bot.get_channel(852767242704650290)).send(embed=embed)


@bot.before_invoke
async def before_invoke(ctx):
    if ctx.author.id in bot.owner_ids:
        return
    if test:
        if ctx.guild.id != 852766855583891486:
            raise OnTestMode("On test mode")
    async with aiosql.connect("memebot.db") as cur:
        async with cur.execute(
            "SELECT * FROM blacklist WHERE id=?", (ctx.author.id,)
        ) as result:
            result = await result.fetchall()
            if result:
                await ctx.reply(f"{ctx.author} 님은 `{result[0][1]}`의 사유로 차단되셨습니다.")
                raise UserOnBlacklist("User is on blacklist")
        # if ctx.command.name != "가입":
        #     async with cur.execute(
        #         "SELECT * FROM joined WHERE id=?", (ctx.author.id,)
        #     ) as result:
        #         result = await result.fetchall()
        #         if not result:
        #             await ctx.reply("가입 명령어를 통해 사용 권한을 얻으세요.")
        #             raise NotJoined('User Didn\'t Join')
    async with aiofiles.open("cmd.log", "a") as f:
        await f.write(
            f"{ctx.author}({ctx.author.id})\n{ctx.message.content}\n{ctx.message.created_at}"
        )


@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        return
    p = __import__('re').compile('<@!?875908453548326922>')
    if p.match(message.content):
        await message.channel.send(
            f"{message.guild} 서버의 접두사는 `{await get_prefix(_bot=bot, message=message)}`입니다."
        )
    await bot.process_commands(message)


@bot.event
async def on_button_click(interaction):
    if interaction.component.label == "🚨 신고하기":
        await interaction.respond(content="DM을 확인해 주세요")
        report_msg = await interaction.author.send(
            "신고 사유를 선택해 주세요",
            components=[
                Select(
                    placeholder="신고 사유",
                    options=[
                        SelectOption(
                            label="1",
                            value="1",
                            description="대한민국 법에 어긋나는 짤(초상권, etc...)",
                        ),
                        SelectOption(
                            label="2",
                            value="2",
                            description="인신공격, 저격, 분쟁, 비방, 비하 등의 위험이 있는 짤",
                        ),
                        SelectOption(
                            label="3", value="3", description="홍보 목적으로 업로드된 짤"
                        ),
                        SelectOption(
                            label="4",
                            value="4",
                            description="정치드립/19금/19금 드립 등 불쾌할 수 있는 짤",
                        ),
                        SelectOption(
                            label="5",
                            value="5",
                            description="같은 짤 재업로드",
                        ),
                        SelectOption(
                            label="6",
                            value="6",
                            description="특정 정치 사상을 가지거나 특정인들의 팬 등 소수들만 재미있는 짤",
                        ),
                        SelectOption(
                            label="7",
                            value="7",
                            description="19금 용어 등을 모자이크하지 않음 / 모자이크되지 않은 욕설이 2개 이상",
                        )
                    ],
                    max_values=7,
                )
            ]
        )
        msg = await interaction.channel.fetch_message(interaction.message.id)
        try:
            interaction = await bot.wait_for("select_option")
        except asyncio.TimeoutError:
            return await interaction.author.send("시간 초과로 신고가 취소되었습니다")
        embed = msg.embeds[0]
        date = __import__("datetime").datetime.utcnow() + __import__(
            "datetime"
        ).timedelta(hours=9)
        filename = (
                f'report_{date.strftime("%y%b%d_%H%M%S")}_{interaction.author.id}.'
                + embed.image.url.split("?")[0].split(".")[-1]
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(embed.image.url) as resp:
                async with aiofiles.open(filename, "wb") as f:
                    await f.write(await resp.read())
        await bot.get_channel(869414081411567676).send(
            f"{interaction.author.mention}: `{'`, `'.join([i for i in list(interaction.values)])}`",
            file=discord.File(filename),
            embed=embed
        )
        remove(filename)
        await report_msg.edit(content="신고 접수가 완료되었습니다", components=[])


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

    if test:
        raise error
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
    print(error)


bot.remove_command("help")
bot.run(token)
