import discord
from discord.ext import commands
import sqlite3 as sql
from os import listdir, popen
from os.path import isfile
from Tools.var import errorcolor
from pickle import load


with open('token.bin', 'rb') as tokenfile:
    token = load(tokenfile)
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
    conn = sql.connect("memebot.db", isolation_level=None)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS usermeme (id INTEGER PRIMARY KEY, uploader_id INTEGER, description text)"
    )
    # 유저가 업로드한 밈들 id/설명 등 매칭
    cur.execute(
        "CREATE TABLE IF NOT EXISTS blacklist (id INTEGER PRIMARY KEY, reason text)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS webhooks (url text PRIMARY KEY, guild_id INTEGER)"
    )
    # 유저가 업로드한 밈들 보낼 웹훅
    cur.close()
    print("ready")
    for file in [j if isfile("Cogs/" + j) else None for j in listdir("Cogs")]:
        if file is not None:
            bot.load_extension(f"Cogs.{file[:-3]}")
            print(file[:-3])
    bot.load_extension("jishaku")
    print("jishaku")
    await bot.get_channel(852767242704650290).send("켜짐")


@bot.before_invoke
async def before_invoke(ctx):
    if ctx.author.id in bot.owner_ids:
        ctx.command.reset_cooldown(ctx)
    await ctx.trigger_typing()


@bot.command(name="깃풀", aliases=["git pull", "깃허브 풀", "ㄱㅍ"])
@commands.is_owner()
async def _git(ctx):
    with open("restarting.py", "w") as f:
        f.write('import os, time\ntime.sleep(10)\nos.system("python bot.py")')
    result = popen("git pull")
    await ctx.send("완료")
    await ctx.send(f"```{result.read()}```")
    popen("python restarting.py")
    await bot.close()


@bot.event
async def on_command_error(ctx, error):
    if type(error) in [
        commands.CommandNotFound,
        commands.NotOwner,
        commands.MaxConcurrencyReached,
        commands.DisabledCommand,
        commands.MissingPermissions,
        commands.CheckFailure,
        commands.MissingRequiredArgument,
    ]:
        return
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"`{round(error.retry_after, 2)}`초 후에 다시 시도해 주세요")
    else:
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
