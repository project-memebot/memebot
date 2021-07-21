from asyncio import TimeoutError
from random import choice
import discord
import aiohttp
from EZPaginator import Paginator
from discord.ext import commands, tasks
from tool import embedcolor, sendmeme, errorcolor
from datetime import datetime, timedelta
import aiofiles
import aiosqlite as aiosql
from shutil import copy2


class Usermeme(commands.Cog, name="짤 공유"):

    """
    유저들이 짤을 공유하고 보는 명령어들
    """

    def __init__(self, bot):
        self.bot = bot
        self._backupdb.start()

    @tasks.loop(minutes=15)
    async def _backupdb(self):
        copy2("memebot.db", "backup.db")
        await (self.bot.get_channel(852767243360403497)).send(
            str(datetime.utcnow() + timedelta(hours=9)), file=discord.File("backup.db")
        )
        await (self.bot.get_channel(852767243360403497)).send(
            str(datetime.utcnow() + timedelta(hours=9)),
            file=discord.File("command.log"),
        )

    @commands.command(
        name="업로드",
        aliases=("올리기", "ㅇㄹㄷ"),
        help="유저들이 공유하고 싶은 짤을 올리는 기능입니다",
    )
    async def _upload(self, ctx):
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
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            await cur.execute(
                "INSERT INTO usermeme(id, uploader_id, title, url) VALUES(?, ?, ?, ?)",
                (msg.id, ctx.author.id, title, msg.attachments[0].url),
            )
        await ctx.reply("짤 업로드 완료")

    @commands.command(
        name="랜덤",
        aliases=("ㄹㄷ", "무작위", "랜덤보기", "뽑기"),
        help="유저들이 올린 짤들 중에서 랜덤으로 뽑아 올려줍니다",
    )
    async def _random(self, ctx):
        async with aiosql.connect("memebot.db") as cur:
            async with cur.execute("SELECT id FROM usermeme") as result:
                meme = choice(await result.fetchall())[0]
        await send_meme(
            bot=self.bot,
            memeid=meme,
            msg=await ctx.reply(
                embed=discord.Embed(title="짤을 불러오는중...", color=embedcolor)
            ),
        )

    @commands.group(
        "내짤",
        invoke_without_command=True,
        usage="<갤러리/제거/수정> [짤 ID]",
        aliases=("ㄴㅉ", "짤"),
        help="올린 짤의 목록을 보거나 지우거나 수정합니다",
    )
    async def meme(self, ctx):
        async with aiosql.connect("memebot.db") as cur:
            async with cur.execute(
                "SELECT * FROM customprefix WHERE guild_id=?", (ctx.guild.id,)
            ) as result:
                prefix = await result.fetchall()
        prefix = prefix[0][1] if prefix else "ㅉ"
        await ctx.reply(f"{prefix}내짤 <목록/제거/수정> [짤 ID]\n(짤 ID는 목록 명령어 사용시 불필요)")

    @meme.command(
        name="목록",
        aliases=("ㅁㄹ", "보기"),
        help="내가 올린 짤의 목록을 봅니다",
    )
    async def _mymeme(self, ctx):
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            async with cur.execute(
                "SELECT id FROM usermeme WHERE uploader_id=?", (ctx.author.id,)
            ) as result:
                memes = [i[0] for i in await result.fetchall()]
        msg = await send_meme(
            bot=self.bot,
            memeid=memes[-1],
            msg=await ctx.reply(
                embed=discord.Embed(title="짤을 불러오는중...", color=embedcolor)
            ),
        )
        await msg.add_reaction("⏪")
        await msg.add_reaction("◀️")
        await msg.add_reaction("⏹️")
        await msg.add_reaction("▶️")
        await msg.add_reaction("⏩")
        index = 0
        while True:
            try:
                reaction, _user = await self.bot.wait_for(
                    "reaction",
                    check=lambda reaction, user: self.bot.user.id
                    in [i.id for i in await reaction.users().flatten()]
                    and user == ctx.author
                    and reaction.message == msg,
                )
            except TimeoutError:
                break
            if reaction.emoji == "⏪":
                index = 0
            elif reaction.emoji == "◀️":
                if index != 0:
                    index -= 1
            elif reaction.emoji == "⏹️":
                break
            elif reaction.emoji == "▶️":
                if index + 1 < len(memes):
                    index += 1
            else:
                index = len(memes) - 1
            msg = await send_meme(bot=self.bot, memeid=memes[index], msg=msg)

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
        async with aiosql.connect("memebot.db") as cur:
            async with cur.execute(
                "SELECT * FROM usermeme WHERE id=?", (memeid,)
            ) as result:
                try:
                    result = await result.fetchall()[0]
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
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            await cur.execute("DELETE FROM usermeme WHERE id=?", (memeid,))
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
        async with aiosql.connect("memebot.db") as cur:
            async with cur.execute(
                "SELECT * FROM usermeme WHERE id=?", (memeid,)
            ) as result:
                if not await result.fetchall():
                    await ctx.send("짤을 찾을 수 없습니다")
        await ctx.send("바꿀 제목을 입력해 주세요")
        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
        except TimeoutError:
            return await ctx.send("취소되었습니다")
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            await cur.execute(
                "UPDATE usermeme SET title=? WHERE id=?", (msg.content, memeid)
            )
        await ctx.reply("제목이 수정되었습니다")

    @commands.command(name="조회", aliases=("ㅈㅎ",), usage="<짤 ID>", help="밈 ID로 짤을 찾습니다")
    async def _findwithid(self, ctx, memeid: int):
        msg = await ctx.reply(
            embed=discord.Embed(title="짤을 불러오는 중...", color=embedcolor)
        )
        try:
            await sendmeme(bot=self.bot, id=memeid, msg=msg)
        except ValueError:
            await msg.edit(embed=discord.Embed(title="짤을 찾을 수 없습니다.", color=errorcolor))


def setup(bot):
    bot.add_cog(Usermeme(bot))
