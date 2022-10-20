import asyncio
import datetime
import os

import discord
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands

from utils.database import *
from utils.embed import *
from utils.checks import blacklist_check


class developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def dev_check(self):
        if self.author.id in self.bot.owner_ids:
            return True
        else:
            embed = discord.Embed(
                title=f"<:jbllogo:929615468233363457> 권한 부족",
                description="명령어를 실행할 권한이 부족합니다. (``개발자`` 권한 필요)",
                color=0x5865F2,
            )
            await self.respond(embed=embed, ephemeral=True)
            return False

    # ------------------------------------- 블랙리스트 관련 ------------------------------------- #

    blacklist = SlashCommandGroup("블랙리스트", "블랙리스트 관련 명령어입니다.")

    @blacklist.command(
        name="추가",
        description="[🔒 봇 관리자 전용] 블랙리스트에 유저를 추가합니다.",
        checks=[blacklist_check, dev_check],
        default_permission=False,
    )
    @commands.is_owner()
    async def 블랙리스트_추가(
        self,
        ctx,
        user: Option(discord.User, "블랙리스트에 추가할 유저를 입력해주세요.", required=True),
        reason: Option(str, "블랙리스트에 추가할 사유를 입력해주세요.", required=True),
        endat: Option(
            str, "YYMMDDhhmm 형식으로 입력해주세요. 무기한 블랙리스트는 이 칸을 입력하지 말아주세요.", required=False
        ),
    ):
        await ctx.interaction.response.defer(ephemeral=True)
        if await BLACKLIST.search(user.id):
            if (await BLACKLIST.search(user.id))["ended_at"]:
                return await ctx.respond(
                    f"{user.mention}은(는) 이미 블랙리스트입니다.\n>>> 사유 : ``{(await BLACKLIST.search(user.id))['reason']}``\n해제 예정 시각 : <t:{str((await BLACKLIST.search(user.id))['ended_at'].timestamp()).split('.')[0]}> (<t:{str((await BLACKLIST.search(user.id))['ended_at'].timestamp()).split('.')[0]}:R>)",
                    ephemeral=True,
                )
            else:
                return await ctx.respond(
                    f"{user.mention}은(는) 이미 블랙리스트입니다.\n>>> 사유 : ``{(await BLACKLIST.search(user.id))['reason']}``\n해제 예정 시각 : 무기한 차단",
                    ephemeral=True,
                )
        else:
            if endat:
                ended_at = datetime.datetime.strptime(str(endat), "%y%m%d%H%M")
            else:
                ended_at = None

        await BLACKLIST.add(user.id, reason, ctx.author.id, ended_at)
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="서포트 서버",
                emoji="<:memebot:942390428890705940>",
                style=discord.ButtonStyle.link,
                url="https://discord.gg/RSUqQBzP9B",
            )
        )
        if endat:
            try:
                await (await self.bot.fetch_user(user.id)).send(
                    f"안녕하세요, {user.mention}!\n\n당신은 <t:{(str(datetime.datetime.now().timestamp())).split('.')[0]}>에 시스템에서 블랙리스트 조치되셨습니다.\n> 사유 : ``{reason}``\n> 해제 예정 시각 : <t:{(str(ended_at.timestamp())).split('.')[0]}> (<t:{(str(ended_at.timestamp())).split('.')[0]}:R>)\n\n**이의가 있으신가요?**\n> ``짤방러 채널`` 디스코드에서 문의 부탁드립니다!",
                    view=view,
                )
            except:
                pass
            return await ctx.respond(
                f"{user.mention}을(를) 블랙리스트에 추가하였습니다.\n>>> 사유 : ``{reason}``\n해제 예정 시각 : <t:{(str(ended_at.timestamp())).split('.')[0]}> (<t:{(str(ended_at.timestamp())).split('.')[0]}:R>)",
                ephemeral=True,
            )
        else:
            try:
                await (await self.bot.fetch_user(user.id)).send(
                    f"안녕하세요, {user.mention}!\n\n당신은 <t:{(str(datetime.datetime.now().timestamp())).split('.')[0]}>에 시스템에서 블랙리스트 조치되셨습니다.\n> 사유 : ``{reason}``\n> 해제 예정 시각 : <t:{(str(ended_at.timestamp())).split('.')[0]}> (<t:{(str(ended_at.timestamp())).split('.')[0]}:R>)\n\n**이의가 있으신가요?**\n> ``짤방러 채널`` 디스코드에서 문의 부탁드립니다!",
                    view=view,
                )
            except:
                pass
            return await ctx.respond(
                f"{user.mention}을(를) 블랙리스트에 추가하였습니다.\n>>> 사유 : ``{reason}``\n해제 예정 시각 : 무기한 차단",
                ephemeral=True,
            )

    @blacklist.command(
        name="제거",
        description="[🔒 봇 관리자 전용] 블랙리스트에서 유저를 제거합니다.",
        checks=[blacklist_check, dev_check],
        default_permission=False,
    )
    @commands.is_owner()
    async def 블랙리스트_제거(
        self,
        ctx,
        user: Option(discord.User, "블랙리스트에 추가할 유저를 입력해주세요.", required=True),
        reason: Option(str, "블랙리스트에 추가할 사유를 입력해주세요.", required=True),
    ):
        await ctx.interaction.response.defer(ephemeral=True)
        if not (await BLACKLIST.search(user.id)):
            return await ctx.respond(f"{user.mention}은(는) 블랙리스트가 아닙니다.", ephemeral=True)

        await BLACKLIST.delete(user.id, reason, ctx.author.id)
        try:
            await (await self.bot.fetch_user(user.id)).send(
                f"안녕하세요, {user.mention}!\n\n이용자님의 블랙리스트가 해제되었습니다.\n> 사유 : ``{reason}``\n\n**이제 다시 짤방러 서비스를 사용하실 수 있습니다. 다만 같은 행동을 반복하신다면 다시 블랙리스트에 등재되실 수 있으니 이용에 참고해주세요.**"
            )
        except:
            pass
        return await ctx.respond(
            f"{user.mention}을(를) 블랙리스트에서 제거하였습니다.\n>>> 사유 : ``{reason}``", ephemeral=True
        )

    # ------------------------------------- 시스템 관련 ------------------------------------- #

    system = SlashCommandGroup("시스템", "시스템 관련 명령어입니다.")

    @system.command(
        name="깃풀",
        description="[🔒 봇 관리자 전용] 깃의 최신 버전을 불러옵니다.",
        checks=[blacklist_check, dev_check],
        default_permission=False,
    )
    @commands.is_owner()
    async def system_gitpull(
        self,
        ctx,
    ):
        await ctx.interaction.response.defer(ephemeral=True)
        result = os.popen("git pull").read()
        embed = discord.Embed(
            title=f"<:jbllogo:929615468233363457> {self.bot.user.name} 깃 풀",
            description=f"```{result}```",
            color=0x5865F2,
        )
        embed.set_footer(text="봇 재시작은 '/시스템 재시작' 명령어로 가능합니다.")
        await ctx.respond(embed=embed)

    @system.command(
        name="재시작",
        description="[🔒 봇 관리자 전용] 시스템을 재시작합니다.",
        checks=[blacklist_check, dev_check],
        default_permission=False,
    )
    @commands.is_owner()
    async def system_gitpull(
        self,
        ctx,
    ):
        await ctx.interaction.response.defer(ephemeral=True)
        await ctx.respond("5초 후 봇을 종료합니다. (종료 후에는 pm2로 재시작됨)")
        await asyncio.sleep(5)
        await self.bot.close()

    # ------------------------------------------------------------------------------------------ #


def setup(bot):
    bot.add_cog(developer(bot))
