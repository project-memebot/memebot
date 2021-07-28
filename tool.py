import aiosqlite as aiosql
import discord
import aiofiles
import aiohttp
from discord.ext import commands
from discord_components import Button, ButtonStyle, Select, SelectOption
from os import remove


errorcolor = 0xFFFF00
embedcolor = 0x0000FF


async def get_prefix(_bot, message) -> str:
    async with aiosql.connect("memebot.db") as cur:
        async with cur.execute(
            "SELECT * FROM customprefix WHERE guild_id=?", (message.guild.id,)
        ) as result:
            prefix = await result.fetchall()
            return "ㅉ" if not prefix else prefix[0][1]


async def sendmeme(bot, memeid, msg):
    async with aiosql.connect("memebot.db") as cur:
        async with cur.execute(
            "SELECT * FROM usermeme WHERE id=?", (memeid,)
        ) as result:
            result = await result.fetchall()
    if not result:
        raise ValueError("Can't find meme")
    result = result[0]
    embed = discord.Embed(title=result[2], color=embedcolor)
    embed.set_image(url=result[3])
    uploader = await bot.fetch_user(result[1])
    embed.set_author(icon_url=uploader.avatar_url, name=str(uploader))
    embed.set_footer(text=f"짤 ID: {result[0]}")
    await msg.edit(embed=embed)
    return await msg.channel.fetch_message(msg.id)


async def set_buttons(ctx: commands.Context):
    return await ctx.send(
        embed=discord.Embed(title='밈을 불러오는중...'),
        components=[
            Button(style=ButtonStyle.red, label='🚨 신고하기')
        ]
    )


async def wait_buttons(msg, memeid, bot):
    interaction = await bot.wait_for('button_click', check=lambda i: i.component.label == '🚨 신고하기')
    await interaction.respond(content='신고 사유를 선택해 주세요', components=[
        Select(placeholder='신고 사유',
               options=[
                   SelectOption(label='1', value="1", description='대한민국 법에 어긋나는 짤(초상권, etc...)'),
                   SelectOption(label='2', value="2", description='인신공격, 저격, 분쟁, 비방, 비하 등의 위험이 있는 짤'),
                   SelectOption(label='3', value="3", description='홍보 목적으로 업로드된 짤'),
                   SelectOption(label='4', value="4", description='정치드립/19금/19금 드립 등 불쾌할 수 있는 짤'),
                   SelectOption(label='5', value="5", description='같은 짤 재업로드',),
                   SelectOption(label='6', value="6", description='특정 정치 사상을 가지거나 특정인들의 팬 등 소수들만 재미있는 짤'),
                   SelectOption(label='7', value="7", description='19금 용어 등을 모자이크하지 않음 / 모자이크되지 않은 욕설이 2개 이상'),
               ])
    ])
    interaction = await bot.wait_for('select_option')
    async with aiosql.connect('memebot.db') as cur:
        async with cur.execute('SELECT * FROM usermeme WHERE id=?', (memeid,)) as result:
            result = (await result.fetchall())[0]
    date = __import__('datetime').datetime.utcnow() + __import__('datetime').timedelta(hours=9)
    filename = f'report_{date.strftime("%y%b%d_%H%M%S")}_{msg.author.id}.{result[3].split(".")[-1]}'
    async with aiohttp.ClientSession() as session:
        async with session.get(result[3]) as resp:
            async with aiofiles.open(filename, "wb") as f:
                await f.write(await resp.read())
    await bot.get_channel(869414081411567676).send(
        f'{interaction.author.mention}: {interaction.component[0].description}\
        \n{bot.get_user(result[1]).mention} - {result[2]}',
        file=discord.File(filename)
    )
    remove(filename)
    await interaction.author.send('성공적으로 신고를 접수했습니다.\n허위 신고시 이용에 제한이 있을 수 있습니다.')


class CommandOnCooldown(Exception):
    pass


class MaxConcurrencyReached(Exception):
    pass


class UserOnBlacklist(Exception):
    pass
