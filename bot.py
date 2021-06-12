import discord
from discord.ext import commands
import sqlite3 as sql
from os import listdir, popen
from os.path import isfile


token = "ODUyODAyMzkwMDgzMzcxMDI4.YMMIHg.BsH_u5M8TasSLqAnTXsV6rjaiFQ"
mentions = discord.AllowedMentions.all()
mentions.replied_user = False
bot = commands.Bot(
    command_prefix=("ㅉ", "짤 "),
    allowed_mentions=mentions,
    owner_ids=(745848200195473490,),
    intents=discord.Intents.all(),
)


@bot.event
async def on_ready():
    conn = sql.connect('memebot.db', isolation_level=None)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS usermeme (id INTEGER PRIMARY KEY, uploader_id INTEGER, description text)')
    # 유저가 업로드한 밈들 id/설명 등 매칭
    cur.execute('CREATE TABLE IF NOT EXISTS blacklist (id INTEGER PRIMARY KEY, reason text)')
    cur.execute('CREATE TABLE IF NOT EXISTS webhooks (url text PRIMARY KEY, guild_id INTEGER)')
    # 유저가 업로드한 밈들 보낼 웹훅
    cur.close()
    print("ready")
    for file in [j if isfile('Cogs/' + j) else None for j in listdir('Cogs')]:
        if file is not None:
            bot.load_extension(f'Cogs.{file[:-3]}')
            print(file[:-3])
    bot.load_extension('jishaku')
    print('jishaku')
    await bot.get_channel(852767242704650290).send('켜짐')


@bot.before_invoke
async def before_invoke(ctx):
    if ctx.author.id in bot.owner_ids: ctx.command.reset_cooldown(ctx)
    await ctx.trigger_typing()


@commands.command(name="깃풀", aliases=["git pull", "깃허브 풀", "ㄱㅍ"])
@commands.is_owner()
async def _git(ctx):
    with open("restarting.py", "w") as f:
        f.write('import os, time\ntime.sleep(5)\nos.system("python bot.py")')
    result = popen("git pull").read()
    await ctx.send('완료')
    await ctx.send(f'```{result}```')
    popen("python restarting.py")
    await bot.close()

bot.run(token)
