from asyncio import TimeoutError
from random import choice
import discord
import aiohttp
from EZPaginator import Paginator
from discord.ext import commands
from tool import embedcolor, sendmeme, errorcolor, set_buttons  # , wait_buttons
from datetime import datetime, timedelta
import aiofiles
import aiosqlite as aiosql
from shutil import rmtree
from os import remove, makedirs, listdir
from discord_components import Button, ButtonStyle
import zipfile
from os.path import isdir
from string import ascii_letters, digits


class Usermeme(commands.Cog, name="짤 공유"):

    """
    유저들이 짤을 공유하고 보는 명령어들
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="업로드",
        aliases=("올리기", "ㅇㄹㄷ"),
        help="유저들이 공유하고 싶은 짤을 올리는 기능입니다",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.user)
    async def _upload(self, ctx):
        await ctx.send("사진(파일 또는 URL)을 업로드해 주세요.")
        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
        except TimeoutError:
            return await ctx.send("취소되었습니다.")
        if not msg.attachments:
            url = msg.content
        else:
            url = msg.attachments[0].url
        url = url.split("?")[0]
        if not url.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
            return await ctx.send("지원되지 않는 파일 형식입니다.")
        filename = (
            str(ctx.author.id)
            + " "
            + (datetime.utcnow() + timedelta(hours=9)).strftime("%Y%m%d-%H%M%S")
            + "."
            + url.split(".")[-1]
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                async with aiofiles.open(filename, "wb") as f:
                    await f.write(await resp.read())
        try:
            img_msg = await self.bot.get_channel(852811274886447114).send(
                file=discord.File(filename)
            )
            remove(filename)
        except discord.Forbidden:
            remove(filename)
            return await ctx.send("파일 크기가 너무 큽니다")
        await ctx.send("짤의 제목을 입력해주세요\n제목이 없으면 `없음`을 입력해주세요")
        msg = await self.bot.wait_for(
            "message",
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
        )
        title = "" if msg.content == "없음" else msg.content
        embed = discord.Embed(title="확인", description=title, color=embedcolor)
        embed.set_image(url=url)
        msg = await ctx.send(
            content="이 내용으로 짤을 등록할까요?",
            embed=embed,
            components=[
                [
                    Button(emoji="✅", label="등록", style=ButtonStyle.green),
                    Button(emoji="❌", label="취소", style=ButtonStyle.red),
                ]
            ],
        )
        try:
            await self.bot.wait_for(
                "button_click",
                check=lambda m: m.author == ctx.author
                and m.channel == ctx.channel
                and m.component.label == "등록",
            )
        except TimeoutError:
            await img_msg.delete()
            return await ctx.reply("취소되었습니다")
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            await cur.execute(
                "INSERT INTO usermeme(id, uploader_id, title, url) VALUES(?, ?, ?, ?)",
                (img_msg.id, ctx.author.id, title, img_msg.attachments[0].url),
            )
        await msg.edit(content="짤 업로드 완료", components=[])

    @commands.command(
        name="랜덤",
        aliases=("ㄹㄷ", "무작위", "랜덤보기", "뽑기"),
        help="유저들이 올린 짤들 중에서 랜덤으로 뽑아 올려줍니다",
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def _random(self, ctx):
        async with aiosql.connect("memebot.db") as cur:
            async with cur.execute("SELECT id FROM usermeme") as result:
                meme = choice(await result.fetchall())[0]
        await sendmeme(
            bot=self.bot,
            memeid=meme,
            msg=await set_buttons(ctx),
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
    @commands.max_concurrency(1, commands.BucketType.user)
    async def _mymeme(self, ctx):
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            async with cur.execute(
                "SELECT * FROM usermeme WHERE uploader_id=?", (ctx.author.id,)
            ) as result:
                memes = await result.fetchall()
        embeds = [
            discord.Embed(
                title=f"{i[2] if i[2] != '' else '`제목 없음`'} - ({memes.index(i) + 1}/{len(memes)})",
                color=embedcolor,
            )
            .set_image(url=i[3])
            .set_footer(text=f"밈 ID: {i[0]}")
            for i in memes
        ]
        message = await ctx.reply(embed=embeds[0])
        page = Paginator(
            bot=self.bot,
            message=message,
            embeds=embeds,
            use_extend=True,
            timeout=10,
            only=ctx.author,
        )
        await page.start()

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
                "SELECT * FROM usermeme WHERE id=? AND uploader_id=?",
                (memeid, ctx.author.id),
            ) as result:
                try:
                    result = (await result.fetchall())[0]
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
    @commands.max_concurrency(1, commands.BucketType.user)
    async def _edit(self, ctx, memeid=None):
        if memeid is None:
            return await ctx.send(
                f"사용법은 `{ctx.command.usage}`입니다.\n(짤 ID는 내짤 명령어에서 확인 할 수 있습니다.)"
            )
        async with aiosql.connect("memebot.db") as cur:
            async with cur.execute(
                "SELECT * FROM usermeme WHERE id=? AND uploader_id=?",
                (memeid, ctx.author.id),
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
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def _findwithid(self, ctx, memeid: int):
        msg = await set_buttons(ctx)
        try:
            await sendmeme(
                bot=self.bot,
                memeid=memeid,
                msg=msg,
            )
        except ValueError:
            await msg.edit(embed=discord.Embed(title="짤을 찾을 수 없습니다.", color=errorcolor))

    @commands.command(
        name="여러짤업로드", aliases=("ㅇㄹㅉㅇㄹㄷ",), help="여러 짤을 업로드 합니다", enabled=True
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.user)
    async def _manymemeupload(self, ctx):
        await ctx.send("짤들을 모은 .zip 파일을 업로드 해주세요")
        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author
                and m.attachments
                and m.attachments[0].filename.endswith(".zip")
                and m.channel == ctx.channel,
            )
        except __import__("asyncio").TimeoutError:
            return await ctx.reply("취소되었습니다")
        upmsg = await ctx.send("업로드 준비중입니다. 모든 짤들은 설명이 없이 기록됩니다.")
        filename = (
            f"{ctx.author.id}-"
            + (datetime.utcnow() + timedelta(hours=9)).strftime("%Y%m%d-%H%M%S")
            + ".zip"
        )
        await msg.attachments[0].save(filename)
        await __import__("asyncio").sleep(1)
        if not isdir("memes"):
            makedirs("memes")
        if isdir(f"memes/{ctx.author.id}"):
            rmtree(f"memes/{ctx.author.id}")
        letters = digits + ascii_letters + "_"
        with zipfile.ZipFile(filename, "r") as zipped:
            if not zipped.namelist():
                return await upmsg.edit("파일이 없습니다.")
            for i in zipped.namelist():
                if not i.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
                    return await upmsg.edit("지원되지 앟는 파일이 있어 업로드에 실패했습니다.")
                for j in (".".join(i.split(".")[:-2])).split():
                    if not j in letters:
                        await ctx.reply(
                            "유해할 수 있는 파일이 있어 업로드에 실패했습니다.\n\
파일명에서 특수문자를 제거하여 주십시오.\n\
(파일명은 알파벳 대소문자, 숫자, `_`만 가능합니다)"
                        )
                        remove(filename)
                        return
            zipped.extractall(f"memes/{ctx.author.id}")
        await upmsg.edit("업로드 중...")
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            channel = self.bot.get_channel(852811274886447114)
            for i in listdir(f"memes/{ctx.author.id}"):
                msg = await channel.send(
                    file=discord.File(f"memes/{ctx.author.id}/" + i)
                )
                await cur.execute(
                    f"INSERT INTO usermeme(id, uploader_id, title, url) VALUES (?, ?, ?, ?)",
                    (msg.id, ctx.author.id, "", msg.attachments[0].url),
                )
        await upmsg.edit("업로드 완료")
        remove(filename)
        rmtree(f"memes/{ctx.author.id}")


def setup(bot):
    bot.add_cog(Usermeme(bot))
