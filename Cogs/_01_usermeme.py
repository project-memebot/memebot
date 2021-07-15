import sqlite3 as sql
from asyncio import TimeoutError
from random import choice
import discord
import aiohttp
from EZPaginator import Paginator
from discord.ext import commands, tasks
from tool import embedcolor
from datetime import datetime, timedelta
import aiofiles


class Usermeme(commands.Cog, name="짤 공유"):

    """
    유저들이 짤을 공유하고 보는 명령어들
    """

    def __init__(self, bot):
        self.bot = bot
        self._backupdb.start()

    @tasks.loop(minutes=15)
    async def _backupdb(self):
        conn = sql.connect("memebot.db")
        with conn:
            with open("backup.sql", "w") as f:
                for line in conn.iterdump():
                    f.write(f"{line}\n")
        conn.close()
        await (self.bot.get_channel(852767243360403497)).send(
            str(datetime.utcnow() + timedelta(hours=9)), file=discord.File("backup.sql")
        )

    @commands.command(
        name="업로드",
        aliases=("올리기", "ㅇㄹㄷ"),
        help="유저들이 공유하고 싶은 짤을 올리는 기능입니다",
    )
    async def _upload(self, ctx):
        conn = sql.connect("memebot.db", isolation_level=None)
        cur = conn.cursor()
        await ctx.send("사진(파일 또는 URL)을 업로드해 주세요.")
        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
            if not msg.attachments:
                url = msg.content
            else:
                url = msg.attachments[0].url
            if not url.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
                return await ctx.send("지원되지 않는 파일 형식입니다.")
            await ctx.send("짤의 제목을 입력해주세요\n제목이 없으면 `없음`을 입력해주세요")
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
            title = "" if msg.content == "없음" else msg.content
            embed = discord.Embed(title="확인", description=title, color=embedcolor)
            embed.set_image(url=url)
            await ctx.send(
                content="이 내용으로 짤을 등록할까요?\nOK는 `ㅇ`, X는 `ㄴ`를 입력해 주세요", embed=embed
            )
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
            if msg.content != "ㅇ":
                raise TimeoutError
        except TimeoutError:
            return await ctx.send("취소되었습니다.")
        filename = (
            str(ctx.author.id)
            + " "
            + str(datetime.utcnow() + timedelta(hours=9))
            + "."
            + url.split(".")[-1]
        )
        if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
            return await ctx.send("지원되지 않는 파일 형식입니다.")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                async with aiofiles.open(filename, "wb") as f:
                    await f.write(await resp.read())
        try:
            msg = await self.bot.get_channel(852811274886447114).send(
                file=discord.File(filename)
            )
        except discord.Forbidden:
            return await ctx.send("파일 크기가 너무 큽니다")
        cur.execute(
            "INSERT INTO usermeme(id, uploader_id, title, url) VALUES(?, ?, ?, ?)",
            (msg.id, ctx.author.id, title, msg.attachments[0].url),
        )
        await ctx.reply("짤 업로드 완료")
        conn.close()

    @commands.command(
        name="랜덤",
        aliases=("ㄹㄷ", "무작위", "랜덤보기", "뽑기"),
        help="유저들이 올린 짤들 중에서 랜덤으로 뽑아 올려줍니다",
    )
    async def _random(self, ctx):
        conn = sql.connect("memebot.db", isolation_level=None)
        cur = conn.cursor()
        cur.execute("SELECT * FROM usermeme")
        meme = choice(cur.fetchall())
        conn.close()
        embed = discord.Embed(title=meme[2], color=embedcolor)
        embed.set_image(url=meme[3])
        member = await self.bot.fetch_user(meme[1])
        embed.set_author(
            name=str(member),
            icon_url=member.avatar_url,
            url=f"https://discord.com/users/{member.id}",
        )
        embed.set_footer(text=f"짤 ID: {meme[0]}")
        await ctx.reply(embed=embed)

    @commands.group(
        "내짤",
        invoke_without_command=True,
        usage="<갤러리/제거/수정> [짤 ID]",
        aliases=("ㄴㅉ", "짤"),
        help="올린 짤의 목록을 보거나 지우거나 수정합니다",
    )
    async def meme(self, ctx):
        conn = sql.connect("memebot.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM customprefix WHERE guild_id=?", (ctx.guild.id,))
        prefix = cur.fetchall()
        prefix = prefix[0][1] if prefix else "ㅉ"
        conn.close()
        await ctx.reply(f"{prefix}내짤 <목록/제거/수정> [짤 ID]\n(짤 ID는 목록 명령어 사용시 불필요)")

    @meme.command(
        name="목록",
        aliases=("ㅁㄹ", "보기"),
        help="내가 올린 짤의 목록을 봅니다",
    )
    async def _mymeme(self, ctx):
        conn = sql.connect("memebot.db", isolation_level=None)
        cur = conn.cursor()
        cur.execute("SELECT * FROM usermeme WHERE uploader_id=?", (ctx.author.id,))
        memes = cur.fetchall()
        embeds = list()
        for i in memes:
            embed = discord.Embed(
                title=f'{"**" + i[2] + "**" if i[2] != "" else i[2]} ({i[0]})',
                color=embedcolor,
            )
            embed.set_author(name=f"내짤 목록 ({memes.index(i)+1}/{len(memes)} 페이지)")
            embed.set_image(url=i[3])
            embed.set_footer(text="짤 제목 뒤에 있는 글자는 짤 ID입니다.")
            embeds.append(embed)
        page = Paginator(
            embeds=embeds,
            bot=self.bot,
            message=await ctx.reply(embed=embeds[0]),
            use_extend=True,
        )
        await page.start()
        conn.close()

    @meme.command(
        name="제거",
        aliases=("ㅈㄱ", "삭제"),
        help="자신이 올렸던 짤을 삭제합니다",
        usage="<짤 ID>",
    )
    async def _delete(self, ctx, memeid=None):
        if memeid is None:
            return await ctx.send(
                f"사용법은 `{ctx.command.usage}`입니다.\n(짤 ID는 내짤 명령어에서 확인 할 수 있습니다.)"
            )
        conn = sql.connect("memebot.db", isolation_level=None)
        cur = conn.cursor()
        cur.execute("SELECT * FROM usermeme WHERE id=?", (memeid,))
        try:
            result = cur.fetchall()[0]
        except IndexError:
            return await ctx.send("짤을 찾을 수 없습니다")
        embed = discord.Embed(title=result[2], color=embedcolor)
        embed.set_image(url=result[3])
        m = await ctx.send("이 짤을 삭제할까요?\n`ㅇ`: OK, `ㄴ`: No", embed=embed)
        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda _m: _m.author == ctx.author and _m.channel == ctx.channel,
            )
        except TimeoutError:
            return await ctx.send("취소되었습니다")
        if msg.content != "ㅇ":
            return await ctx.send("취소되었습니다")
        await m.delete()
        cur.execute("DELETE FROM usermeme WHERE id=?", (memeid,))
        conn.close()
        await ctx.reply("삭제 완료")

    @meme.command(
        name="수정",
        aliases=("ㅅㅈ", "변경"),
        usage="<짤 ID>",
        help="자신이 올린 짤의 제목을 바꿉니다",
    )
    async def _edit(self, ctx, memeid=None):
        if memeid is None:
            return await ctx.send(
                f"사용법은 `{ctx.command.usage}`입니다.\n(짤 ID는 내짤 명령어에서 확인 할 수 있습니다.)"
            )
        conn = sql.connect("memebot.db", isolation_level=None)
        cur = conn.cursor()
        cur.execute("SELECT * FROM usermeme WHERE id=?", (memeid,))
        if not cur.fetchall():
            await ctx.send("짤을 찾을 수 없습니다")
        await ctx.send("바꿀 제목을 입력해 주세요")
        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
        except TimeoutError:
            return await ctx.send("취소되었습니다")
        cur.execute("UPDATE usermeme SET title=? WHERE id=?", (msg.content, memeid))
        conn.close()
        await ctx.reply("제목이 수정되었습니다")


def setup(bot):
    bot.add_cog(Usermeme(bot))
