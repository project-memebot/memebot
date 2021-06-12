import discord
from discord.ext import commands
import sqlite3 as sql
from Tools.var import embedcolor
from asyncio import TimeoutError
from datetime import datetime, timedelta
from os import remove
from random import choice


class Usermeme(commands.Cog, name='짤 공유'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='업로드', aliases=('올리기', 'ㅇㄹㄷ'))
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(3, commands.BucketType.default, wait=True)
    async def _upload(self, ctx):
        conn = sql.connect('memebot.db', isolation_level=None)
        cur = conn.cursor()
        await ctx.send('사진을 업로드해 주세요.', delete_after=5)
        try:
            msg = await self.bot.wait_for('message', timeout=20, check=lambda m: m.author == ctx.author and m.channel == ctx.channel and m.attachments != [])
            try:
                img = msg.attachments[0]
            except IndexError:
                raise TimeoutError
            await ctx.send('짤의 설명을 입력해주시고 없으면 `없음`을 입력해주세요')
            msg = await self.bot.wait_for('message', timeout=20, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            description = '' if msg.content == '없음' else msg.content
            embed = discord.Embed(title='확인', description=msg.content, color=embedcolor)
            embed.set_image(url=img.url)
            await ctx.send(content='이 내용으로 짤을 등록할까요?\nOK는 `ㅇ`, X는 `ㄴ`를 입력해 주세요', embed=embed)
            msg = await self.bot.wait_for('message', timeout=20, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            if msg.content != 'ㅇ': raise TimeoutError
        except TimeoutError:
            return await ctx.send('취소되었습니다.')
        now = datetime.utcnow() + timedelta(hours=9)
        filename = now.strftime('%y%m%d %H%M%S ') + str(ctx.author.id) + '.' + img.filename.split('.')[-1]
        await img.save(filename)
        channel = self.bot.get_channel(852811274886447114)
        try:
            msg = await channel.send(file=discord.File(filename))
        except discord.InvalidArgument:
            return await ctx.send('파일 크기가 너무 크군요....')
        cur.execute('INSERT INTO usermeme(id, uploader_id, description) VALUES(?, ?, ?)', (msg.id, ctx.author.id, description))
        await ctx.reply('짤 업로드 완료')
        remove(filename)
        conn.close()

    @commands.command(name='랜덤', aliases=('ㄹㄷ', '무작위', '랜덤보기', '뽑기'))
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def _random(self, ctx):
        conn = sql.connect('memebot.db', isolation_level=None)
        cur = conn.cursor()
        cur.execute('SELECT * FROM usermeme')
        meme = choice(cur.fetchall())
        conn.close()
        embed = discord.Embed(title='랜덤 짤', description=meme[2], color=0x0000ff)
        msg = await (self.bot.get_channel(852811274886447114)).fetch_message(meme[0])
        embed.set_image(url=msg.attachments[0].url)
        member = await self.bot.fetch_user(meme[1])
        embed.set_author(name=str(member), icon_url=member.avatar_url, url=f'https://discord.com/users/{member.id}')
        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Usermeme(bot))
