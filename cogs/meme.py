import config
import discord
import datetime
import asyncio, aiofiles
import re
import os
from discord.ext import commands
from discord.commands import slash_command, Option, permissions, SlashCommandGroup
from utils.embed import *
from utils.database import *


class meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self):
        if await BLACKLIST.search_blacklist(self.author.id):
            embed = Embed.ban_info(await BLACKLIST.search_blacklist(self.author.id))
            await self.respond(embed=embed, ephemeral=True)
            return False
        else:
            return True

    async def account_check(self):
        if not await USER_DATABASE.user_find(self.author.id):
            await self.respond(
                "가입을 진행하지 않았습니다. ``/가입`` 명령어로 가입이 필요합니다.", ephemeral=True
            )
            return False
        else:
            return True

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.is_component():
            if interaction.data["custom_id"].startswith("report-"):
                view = discord.ui.View()
                try:
                    await interaction.response.send_message(
                        f"안녕하세요, {interaction.user.mention}님.\n해당 밈(``ID : {interaction.data['custom_id'].replace('report-', '')}``)에 대한 신고 사유를 선택해주세요.",
                        ephemeral=True,
                    )
                except:
                    await interaction.followup.send(
                        f"안녕하세요, {interaction.user.mention}님.\n해당 밈(``ID : {interaction.data['custom_id'].replace('report-', '')}``)에 대한 신고 사유를 선택해주세요.",
                        ephemeral=True,
                    )

            if interaction.data["custom_id"].startswith("rerandom-"):
                if (
                    int(interaction.data["custom_id"].replace("rerandom-", ""))
                    == interaction.user.id
                ):
                    result = await Embed.meme_embed(
                        result=await MEME_DATABASE.random_meme(), user=interaction.user
                    )
                    try:
                        await interaction.response.edit_message(
                            embed=result["embed"], view=result["view"]
                        )
                    except:
                        await interaction.followup.edit_message(
                            message_id=interaction.message.id,
                            embed=result["embed"],
                            view=result["view"],
                        )
                else:
                    try:
                        await interaction.response.send_message(
                            f"{interaction.user.mention}님, 이 버튼은 명령어를 실행한 유저만 사용이 가능한 버튼이에요.\n``/랜덤`` 명령어로 명령어를 사용해보세요!",
                            ephemeral=True,
                        )
                    except:
                        await interaction.followup.send(
                            f"{interaction.user.mention}님, 이 버튼은 명령어를 실행한 유저만 사용이 가능한 버튼이에요.\n``/랜덤`` 명령어로 명령어를 사용해보세요!",
                            ephemeral=True,
                        )

            if interaction.data["custom_id"].startswith("favorite-"):
                result = await USER_DATABASE.favorite_meme(
                    interaction.user.id,
                    interaction.data["custom_id"].replace("favorite-", ""),
                )
                try:
                    await interaction.response.send_message(
                        result["message"], ephemeral=True
                    )
                except:
                    await interaction.followup.send(result["message"], ephemeral=True)

    @commands.slash_command(
        name="랜덤",
        description="랜덤으로 밈을 찾아볼 수 있어요!",
        guild_ids=[852766855583891486, 941207358032465920],
        checks=[cog_check],
    )
    async def meme_random(self, ctx):
        await ctx.interaction.response.defer()
        result = await Embed.meme_embed(
            result=await MEME_DATABASE.random_meme(), user=ctx.author
        )
        await ctx.respond(embed=result["embed"], view=result["view"])

    # ------------------------------------- 짤 업로드 관련 ------------------------------------- #

    upload = SlashCommandGroup("업로드", "업로드 관련 명령어입니다.", guild_ids=[852766855583891486, 941207358032465920])

    @upload.command(name="파일", description="짤을 파일로 업로드하는 명령어에요. '.png', '.jpg', '.jpeg', '.webp', '.gif' 형식의 사진이 있는 링크로만 업로드 할 수 있어요.", guild_ids=[852766855583891486, 941207358032465920], checks=[cog_check, account_check])
    async def meme_upload_file(self, ctx, title: Option(str, "짤의 이름을 입력해주세요.", name="제목", required=True), file: Option(discord.Attachment, "짤 파일을 업로드해주세요.", name="파일", required=True)):
        await ctx.interaction.response.defer()

        url = (file.url).split("?")[0]

        if not os.path.splitext(url)[1] in ((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            return await ctx.respond("지원되지 않는 파일 형식이에요.\n``.png``, ``.jpg``, ``.jpeg``, ``.webp``, ``.gif`` 형식의 링크만 지원해요.")

        filename = f"{str(ctx.author.id)}-{(datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y%m%d-%H%M%S')}.{url.split('.')[-1]}"

        try:
            img_msg = await self.bot.get_channel(941202775272980510).send(
                content=f'{ctx.author.mention}({ctx.author.id})',
                file=await file.to_file(),
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except discord.Forbidden:
            return await ctx.respond("파일의 크기가 너무 커서 등록을 할 수 없어요.")

        embed = discord.Embed(title="등록 내용 확인", description=title, color=0x5865F2)
        embed.set_image(url=url)

        yes_button = discord.ui.Button(
            label=f"네",
            emoji="<:jblcheck:936927677070331925>",
            style=discord.ButtonStyle.green,
            custom_id=f"yes_button",
        )
        no_button = discord.ui.Button(
            label="아니요",
            emoji="<:jblcancel:936927690580189204>",
            style=discord.ButtonStyle.red,
            custom_id=f"no_button",
        )
        view = discord.ui.View()
        view.add_item(yes_button)
        view.add_item(no_button)

        msg = await ctx.respond(
            content="이 내용으로 짤을 등록할까요?",
            embed=embed,
            view=view,
        )

        def check(inter):
            return inter.user.id == ctx.author.id and inter.message.id == msg.id

        try:
            interaction_check = await self.bot.wait_for(
                "interaction", check=check, timeout=60.0
            )
        except asyncio.TimeoutError:
            return await ctx.edit(
                content=f"{ctx.author.mention}, 시간이 초과되었어요... 언제든지 다시 명령어로 업로드하실 수 있어요!",
                embed=None,
                view=None,
                allowed_mentions=discord.AllowedMentions.none(),
            )

        if interaction_check.data["custom_id"] == "yes_button":
            await MEME_DATABASE.insert_meme(title=title, url=url, uploader_id=ctx.author.id)
            return await ctx.edit(
                content=f"{ctx.author.mention}, 짤 등록이 완료되었어요!", embed=None, view=None, allowed_mentions=discord.AllowedMentions.none(),
            )
        if interaction_check.data["custom_id"] == "no_button":
            return await ctx.edit(
                content=f"{ctx.author.mention}, 등록이 취소되었어요... 언제든지 다시 명령어로 업로드하실 수 있어요!",
                embed=None,
                view=None,
                allowed_mentions=discord.AllowedMentions.none(),
            )

    @upload.command(
        name="링크",
        description="사진의 링크로 짤을 업로드하는 명령어에요. '.png', '.jpg', '.jpeg', '.webp', '.gif' 형식의 사진이 있는 링크로만 업로드 할 수 있어요.",
        guild_ids=[852766855583891486, 941207358032465920],
        checks=[cog_check, account_check],
    )
    async def meme_upload_link(self, ctx, title: Option(str, "짤의 이름을 입력해주세요.", name="제목", required=True), link: Option(str, "짤 링크를 입력해주세요.", name="링크", required=True)):
        await ctx.interaction.response.defer()

        try:
            link = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-@.&+:/?=]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', link)[0]
        except:
            return await ctx.respond("링크 형식이 아니어서 등록을 할 수 없어요.\n올바른 링크를 입력해주세요!")
        url = link.split("?")[0]

        if not os.path.splitext(url)[1] in ((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            return await ctx.respond("지원되지 않는 파일 형식이에요.\n``.png``, ``.jpg``, ``.jpeg``, ``.webp``, ``.gif`` 형식의 링크만 지원해요.")

        filename = f"{str(ctx.author.id)}-{(datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y%m%d-%H%M%S')}.{url.split('.')[-1]}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                async with aiofiles.open(filename, "wb") as f:
                    await f.write(await resp.read())

        try:
            img_msg = await self.bot.get_channel(941202775272980510).send(
                content=f'{ctx.author.mention}({ctx.author.id})',
                file=discord.File(filename),
                allowed_mentions=discord.AllowedMentions.none(),
            )
            os.remove(filename)
        except discord.Forbidden:
            os.remove(filename)
            return await ctx.respond("링크에 포함된 파일의 크기가 너무 커서 등록을 할 수 없어요.")

        embed = discord.Embed(title="등록 내용 확인", description=title, color=0x5865F2)
        embed.set_image(url=url)

        yes_button = discord.ui.Button(
            label=f"네",
            emoji="<:jblcheck:936927677070331925>",
            style=discord.ButtonStyle.green,
            custom_id=f"yes_button",
        )
        no_button = discord.ui.Button(
            label="아니요",
            emoji="<:jblcancel:936927690580189204>",
            style=discord.ButtonStyle.red,
            custom_id=f"no_button",
        )
        view = discord.ui.View()
        view.add_item(yes_button)
        view.add_item(no_button)

        msg = await ctx.respond(
            content="이 내용으로 짤을 등록할까요?",
            embed=embed,
            view=view,
        )

        def check(inter):
            return inter.user.id == ctx.author.id and inter.message.id == msg.id

        try:
            interaction_check = await self.bot.wait_for(
                "interaction", check=check, timeout=60.0
            )
        except asyncio.TimeoutError:
            return await ctx.edit(
                content=f"{ctx.author.mention}, 시간이 초과되었어요... 언제든지 다시 명령어로 업로드하실 수 있어요!",
                embed=None,
                view=None,
                allowed_mentions=discord.AllowedMentions.none(),
            )

        if interaction_check.data["custom_id"] == "yes_button":
            await MEME_DATABASE.insert_meme(title=title, url=url, uploader_id=ctx.author.id)
            return await ctx.edit(
                content=f"{ctx.author.mention}, 짤 등록이 완료되었어요!", embed=None, view=None, allowed_mentions=discord.AllowedMentions.none(),
            )
        if interaction_check.data["custom_id"] == "no_button":
            return await ctx.edit(
                content=f"{ctx.author.mention}, 등록이 취소되었어요... 언제든지 다시 명령어로 업로드하실 수 있어요!",
                embed=None,
                view=None,
                allowed_mentions=discord.AllowedMentions.none(),
            )

    # ------------------------------------------------------------------------------------------ #

def setup(bot):
    bot.add_cog(meme(bot))
