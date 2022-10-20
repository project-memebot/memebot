import asyncio
import datetime
import json
import os
import re

import aiofiles
import discord
from discord.commands import Option, SlashCommandGroup, permissions, slash_command
from discord.ext import commands, pages

import config
from utils.database import *
from utils.embed import *
from utils.checks import blacklist_check

class meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("utils/report_label.json", encoding="UTF8") as f:
            self.data = json.load(f)

        self.options = []
        for i in self.data.keys():
            self.options.append(
                discord.SelectOption(
                    value=i,
                    label=self.data[i]["label"],
                    description=self.data[i]["description"],
                )
            )

    async def account_check(self):
        if not await USER_DATABASE.find(self.author.id):
            await self.respond(
                "가입을 진행하지 않았습니다. ``/가입`` 명령어로 가입이 필요합니다.", ephemeral=True
            )
            return False
        else:
            return True

    async def selfview(self, interaction, disabled, report_code):
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="신고된 짤 보기",
                emoji="🚧",
                style=discord.ButtonStyle.green,
                custom_id=f"reportcheckmeme-{interaction.data['custom_id'].split('-')[1]}-{interaction.user.id}",
                disabled=disabled,
            )
        )
        view.add_item(
            discord.ui.Button(
                label="처리 결과 통보하기",
                emoji="🚩",
                style=discord.ButtonStyle.blurple,
                custom_id=f"reportpunishmeme-{interaction.data['custom_id'].split('-')[1]}-{interaction.user.id}-{report_code}",
                disabled=disabled,
            )
        )
        view.add_item(
            discord.ui.Button(
                label="반려 (거부) 통보하기",
                emoji="❌",
                style=discord.ButtonStyle.red,
                custom_id=f"reportdenymeme-{interaction.data['custom_id'].split('-')[1]}-{interaction.user.id}-{report_code}",
                disabled=disabled,
            )
        )
        return view

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.modal_submit:
            if interaction.data["custom_id"].startswith("reportformjakseong-"):
                report_category_list = []
                report_category_list_value = []
                for i in (interaction.data["custom_id"].split("-")[2]).split(","):
                    report_category_list.append(f"reportlabel-{i}")
                    report_category_list_value.append(
                        f"``{self.data[f'reportlabel-{i}']['label']}``"
                    )

                rp_list = ", ".join(report_category_list_value)

                embed = discord.Embed(
                    color=0x5865F2,
                    title="🚨 신고 접수됨",
                    description="신고가 접수되었습니다.\n>>> 🚩 신고 처리는 최대 7일까지 소요될 수 있으며, 처리 결과는 이용자님의 DM으로 발송됩니다.\n🙏 이용자님의 신고로 짤방러 시스템이 깨끗해질 수 있기를 기대합니다!",
                )
                embed.add_field(
                    name="신고 세부 정보",
                    value=f">>> 신고한 짤 : ``{interaction.data['custom_id'].split('-')[1]}``\n신고자 : {interaction.user.mention} (``{interaction.user.id}``)\n위반 카테고리 : {rp_list}",
                    inline=False,
                )
                embed.add_field(
                    name="신고 사유",
                    value=interaction.data["components"][0]["components"][0]["value"],
                    inline=False,
                )
                result = await REPORT.add(meme_id=interaction.data['custom_id'].split('-')[1], report_user=interaction.user.id, category=rp_list, reason=interaction.data["components"][0]["components"][0]["value"])
                await self.bot.get_channel(int(config.BOT.REPORT_CHANNEL)).send(
                    embed=embed,
                    view=await meme.selfview(self, interaction, disabled=False, report_code=result["report_code"]),
                )
                try:
                    await interaction.followup.edit_message(
                        content=None,
                        embed=embed,
                        view=None,
                    )
                except:
                    await interaction.response.edit_message(
                        content=None,
                        embed=embed,
                        view=None,
                    )
                return

            if interaction.data["custom_id"].startswith("reportpunishjakseong-"):
                if not interaction.user.id in self.bot.owner_ids:
                    return
                embed = discord.Embed(
                    color=0x5865F2,
                    title="🚨 신고 처리됨",
                    description=f"이용자님께서 신고해주신 사항이 처리가 완료되었습니다!\n이용자님의 신고로 더욱 쾌적한 짤방러 시스템이 되도록 노력하도록 하겠습니다.\n이용해주셔서 감사합니다!\n\n>>> 🚧 신고한 짤 : ``{interaction.data['custom_id'].split('-')[1]}``\n🚩 처리 결과 : {interaction.data['components'][0]['components'][0]['value']}",
                )
                try:
                    await (
                        await self.bot.fetch_user(
                            int(interaction.data["custom_id"].split("-")[2])
                        )
                    ).send(embed=embed)
                except:
                    pass
                try:
                    await interaction.followup.edit_message(
                        view=await meme.selfview(self, interaction, disabled=True, report_code=None),
                    )
                except:
                    return await interaction.response.edit_message(
                        view=await meme.selfview(self, interaction, disabled=True, report_code=None),
                    )
                return await REPORT.process(report_code=interaction.data["custom_id"].split("-")[3], process_content=interaction.data['components'][0]['components'][0]['value'], processer=interaction.user.id)

        if interaction.type == discord.InteractionType.component:
            
            if interaction.data["custom_id"].startswith("reportdenymeme-"):
                if not interaction.user.id in self.bot.owner_ids:
                    return
                embed = discord.Embed(
                    color=0x5865F2,
                    title="🚨 신고 반려됨",
                    description=f"이용자님께서 신고해주신 사항의 처리가 반려되었습니다.\n\n> 신고 사유를 명확하게 입력해주시거나, 올바르지 않은 카테고리였기 때문에 반려되었습니다.\n> 다른 문의가 있으시면 [짤방러 채널](https://discord.gg/RSUqQBzP9B)로 문의해주세요.\n\n항상 쾌적한 짤방러 시스템이 되도록 노력하겠습니다.\n이용해주셔서 감사합니다!\n\n>>> 🚧 신고한 짤 : ``{interaction.data['custom_id'].split('-')[1]}``",
                )
                try:
                    await (
                        await self.bot.fetch_user(
                            int(interaction.data["custom_id"].split("-")[2])
                        )
                    ).send(embed=embed)
                except:
                    pass
                try:
                    await interaction.followup.edit_message(
                        view=await meme.selfview(self, interaction, disabled=True, report_code=None),
                    )
                except:
                    return await interaction.response.edit_message(
                        view=await meme.selfview(self, interaction, disabled=True, report_code=None),
                    )
                return await REPORT.process(report_code=interaction.data["custom_id"].split("-")[3], process_content="신고 처리가 반려되었습니다.", processer=interaction.user.id)

            if interaction.data["custom_id"].startswith("reportcheckmeme-"):
                if not interaction.user.id in self.bot.owner_ids:
                    return
                result = await Embed.meme_embed(
                    result=await MEME_DATABASE.find(
                        interaction.data["custom_id"].split("-")[1]
                    ),
                    user=interaction.user,
                )
                try:
                    return await interaction.response.send_message(
                        embed=result["embed"],
                        view=None,
                        ephemeral=True,
                    )

                except:
                    return await interaction.followup.send_message(
                        embed=result["embed"],
                        view=None,
                        ephemeral=True,
                    )

            if interaction.data["custom_id"].startswith("reportpunishmeme-"):
                if not interaction.user.id in self.bot.owner_ids:
                    return
                modal = discord.ui.Modal(
                    title="처리 내용 작성하기",
                    custom_id=f"reportpunishjakseong-{interaction.data['custom_id'].replace('reportpunishmeme-', '')}",
                )
                modal.add_item(
                    discord.ui.InputText(
                        label="처리 내용",
                        placeholder="처리 내용을 입력해주세요. (예: 블랙리스트 7일)",
                        style=discord.InputTextStyle.long,
                        max_length=1024,
                        custom_id="description",
                        required=True,
                    )
                )
                await interaction.response.send_modal(modal)

            if interaction.data["custom_id"].startswith("report-"):
                with open("utils/report_label.json", encoding="UTF8") as f:
                    data = json.load(f)

                options = []

                for i in data.keys():
                    options.append(
                        discord.SelectOption(
                            value=i,
                            label=data[i]["label"],
                            description=data[i]["description"],
                        )
                    )

                view = discord.ui.View()
                view.add_item(
                    discord.ui.Select(
                        placeholder="신고 사유를 선택해주세요.",
                        min_values=1,
                        max_values=len(data.keys()),
                        options=options,
                        custom_id=f"reportlabel-{interaction.data['custom_id'].replace('report-', '')}",
                    )
                )
                try:
                    m = await interaction.response.send_message(
                        f"안녕하세요, {interaction.user.mention}님.\n해당 밈(``ID : {interaction.data['custom_id'].replace('report-', '')}``)에 대한 신고 사유를 선택해주세요.",
                        view=view,
                        ephemeral=True,
                    )
                except:
                    m = await interaction.followup.send(
                        f"안녕하세요, {interaction.user.mention}님.\n해당 밈(``ID : {interaction.data['custom_id'].replace('report-', '')}``)에 대한 신고 사유를 선택해주세요.",
                        view=view,
                        ephemeral=True,
                    )

            if interaction.data["custom_id"].startswith("reportlabel-"):
                reason_list = []
                value_list = []
                for value in interaction.data["values"]:
                    reason_list.append(f"``{self.data[value]['label']}``")
                    value_list.append(value.split("-")[1])
                reasons = ", ".join(reason_list)
                values = ",".join(value_list)

                view = discord.ui.View()
                view.add_item(
                    discord.ui.Button(
                        label="신고 내용 작성하기",
                        emoji="📝",
                        style=discord.ButtonStyle.blurple,
                        custom_id=f"reportformyochung-{interaction.data['custom_id'].replace('reportlabel-', '')}-{values}",
                    )
                )
                try:
                    await interaction.response.edit_message(
                        content=f"안녕하세요, {interaction.user.mention}님.\n해당 밈(``ID : {interaction.data['custom_id'].replace('reportlabel-', '')}``)에 대한 신고 사유가 선택되었습니다.\n\n> 사유 : {reasons}\n\n**``신고 내용 작성하기`` 버튼을 눌러 내용을 작성해주세요.\n\n⚠ 한 번씩 문제가 발생하는데, 버튼을 다시 누르면 해결됩니다!**",
                        view=view,
                    )
                except:
                    await interaction.followup.edit_message(
                        content=f"안녕하세요, {interaction.user.mention}님.\n해당 밈(``ID : {interaction.data['custom_id'].replace('reportlabel-', '')}``)에 대한 신고 사유가 선택되었습니다.\n\n> 사유 : {reasons}\n\n**``신고 내용 작성하기`` 버튼을 눌러 내용을 작성해주세요.\n\n⚠ 한 번씩 문제가 발생하는데, 버튼을 다시 누르면 해결됩니다!**",
                        view=view,
                    )

            if interaction.data["custom_id"].startswith("reportformyochung-"):
                modal = discord.ui.Modal(
                    title="신고 내용 작성하기",
                    custom_id=f"reportformjakseong-{interaction.data['custom_id'].replace('reportformyochung-', '')}",
                )
                modal.add_item(
                    discord.ui.InputText(
                        label="신고 사유",
                        placeholder="왜 이 짤을 신고하시게 되었나요? 자세하게 설명해주시면 처리에 도움이 됩니다!",
                        style=discord.InputTextStyle.long,
                        max_length=1024,
                        custom_id="description",
                        required=True,
                    )
                )
                await interaction.response.send_modal(modal)

            if interaction.data["custom_id"].startswith("rerandom-"):
                if (
                    int(interaction.data["custom_id"].replace("rerandom-", ""))
                    == interaction.user.id
                ):
                    result = await Embed.meme_embed(
                        result=await MEME_DATABASE.random(), user=interaction.user
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
        checks=[blacklist_check],
    )
    async def meme_random(self, ctx):
        await ctx.interaction.response.defer()
        result = await Embed.meme_embed(
            result=await MEME_DATABASE.random(), user=ctx.author
        )
        await ctx.respond(embed=result["embed"], view=result["view"])

    @commands.slash_command(
        name="검색",
        description="밈을 검색할 수 있어요.",
        checks=[blacklist_check],
    )
    async def meme_search(
        self, ctx, query: Option(str, "검색할 키워드를 입력해주세요.", name="키워드", required=True)
    ):
        await ctx.interaction.response.defer()

        meme_result = await MEME_DATABASE.search(query)

        page_list = []

        for i in meme_result:
            page_list.append(
                (await Embed.meme_embed(result=i, user=ctx.author))["embed"]
            )

        if not page_list:
            return await ctx.respond("검색 결과가 존재하지 않습니다.")
        else:
            paginator = pages.Paginator(pages=page_list, use_default_buttons=False)
            paginator.add_button(
                pages.PaginatorButton(
                    "first", emoji="⏪", style=discord.ButtonStyle.blurple
                )
            )
            paginator.add_button(
                pages.PaginatorButton(
                    "prev", emoji="◀️", style=discord.ButtonStyle.green
                )
            )
            paginator.add_button(
                pages.PaginatorButton(
                    "page_indicator", style=discord.ButtonStyle.gray, disabled=True
                )
            )
            paginator.add_button(
                pages.PaginatorButton(
                    "next", emoji="▶️", style=discord.ButtonStyle.green
                )
            )
            paginator.add_button(
                pages.PaginatorButton(
                    "last", emoji="⏩", style=discord.ButtonStyle.blurple
                )
            )
            await paginator.respond(ctx.interaction)

    # ------------------------------------- 짤 업로드 관련 ------------------------------------- #

    upload = SlashCommandGroup("업로드", "업로드 관련 명령어입니다.")

    @upload.command(
        name="파일",
        description="짤을 파일로 업로드하는 명령어에요. '.png', '.jpg', '.jpeg', '.webp', '.gif' 형식의 사진이 있는 링크로만 업로드 할 수 있어요.",
        checks=[blacklist_check, account_check],
    )
    async def meme_upload_file(
        self,
        ctx,
        title: Option(str, "짤의 이름을 입력해주세요.", name="제목", required=True),
        file: Option(discord.Attachment, "짤 파일을 업로드해주세요.", name="파일", required=True),
    ):
        await ctx.interaction.response.defer()

        url = (file.url).split("?")[0]

        if not os.path.splitext(url)[1] in ((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            return await ctx.respond(
                "지원되지 않는 파일 형식이에요.\n``.png``, ``.jpg``, ``.jpeg``, ``.webp``, ``.gif`` 형식의 링크만 지원해요."
            )

        filename = f"{str(ctx.author.id)}-{(datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y%m%d-%H%M%S')}.{url.split('.')[-1]}"

        try:
            img_msg = await self.bot.get_channel(852811274886447114).send(
                content=f"{ctx.author.mention}({ctx.author.id})",
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
            await MEME_DATABASE.insert(
                title=title, url=url, uploader_id=ctx.author.id
            )
            return await ctx.edit(
                content=f"{ctx.author.mention}, 짤 등록이 완료되었어요!",
                embed=None,
                view=None,
                allowed_mentions=discord.AllowedMentions.none(),
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
        checks=[blacklist_check, account_check],
    )
    async def meme_upload_link(
        self,
        ctx,
        title: Option(str, "짤의 이름을 입력해주세요.", name="제목", required=True),
        link: Option(str, "짤 링크를 입력해주세요.", name="링크", required=True),
    ):
        await ctx.interaction.response.defer()

        try:
            link = re.findall(
                "http[s]?://(?:[a-zA-Z]|[0-9]|[$-@.&+:/?=]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                link,
            )[0]
        except:
            return await ctx.respond("링크 형식이 아니어서 등록을 할 수 없어요.\n올바른 링크를 입력해주세요!")
        url = link.split("?")[0]

        if not os.path.splitext(url)[1] in ((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            return await ctx.respond(
                "지원되지 않는 파일 형식이에요.\n``.png``, ``.jpg``, ``.jpeg``, ``.webp``, ``.gif`` 형식의 링크만 지원해요."
            )

        filename = f"{str(ctx.author.id)}-{(datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y%m%d-%H%M%S')}.{url.split('.')[-1]}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                async with aiofiles.open(filename, "wb") as f:
                    await f.write(await resp.read())

        try:
            img_msg = await self.bot.get_channel(852811274886447114).send(
                content=f"{ctx.author.mention}({ctx.author.id})",
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
            await MEME_DATABASE.insert(
                title=title, url=url, uploader_id=ctx.author.id
            )
            return await ctx.edit(
                content=f"{ctx.author.mention}, 짤 등록이 완료되었어요!",
                embed=None,
                view=None,
                allowed_mentions=discord.AllowedMentions.none(),
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
