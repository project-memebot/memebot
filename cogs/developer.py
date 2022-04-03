import config
import discord
import datetime
import asyncio
import os
from discord.ext import commands
from discord.commands import slash_command, Option, permissions, SlashCommandGroup
from utils.embed import *
from utils.database import *


class developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self):
        if await BLACKLIST.search_blacklist(self.author.id):
            embed = Embed.ban_info(await BLACKLIST.search_blacklist(self.author.id))
            await self.respond(embed=embed, ephemeral=True)
            return False
        else:
            return True

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
        checks=[cog_check, dev_check],
        default_permission=False,
    )
    @permissions.is_owner()
    async def 블랙리스트_추가(
        self,
        ctx,
        유저: Option(discord.User, "블랙리스트에 추가할 유저를 입력해주세요.", required=True),
        사유: Option(str, "블랙리스트에 추가할 사유를 입력해주세요.", required=True),
        종료일: Option(
            str, "YYMMDDhhmm 형식으로 입력해주세요. 무기한 블랙리스트는 이 칸을 입력하지 말아주세요.", required=False
        ),
    ):
        await ctx.interaction.response.defer(ephemeral=True)
        if await BLACKLIST.search_blacklist(유저.id):
            if (await BLACKLIST.search_blacklist(유저.id))["ended_at"]:
                return await ctx.respond(
                    f"{유저.mention}은(는) 이미 블랙리스트입니다.\n>>> 사유 : ``{(await BLACKLIST.search_blacklist(유저.id))['reason']}``\n해제 예정 시각 : <t:{str((await BLACKLIST.search_blacklist(유저.id))['ended_at'].timestamp()).split('.')[0]}> (<t:{str((await BLACKLIST.search_blacklist(유저.id))['ended_at'].timestamp()).split('.')[0]}:R>)",
                    ephemeral=True,
                )
            else:
                return await ctx.respond(
                    f"{유저.mention}은(는) 이미 블랙리스트입니다.\n>>> 사유 : ``{(await BLACKLIST.search_blacklist(유저.id))['reason']}``\n해제 예정 시각 : 무기한 차단",
                    ephemeral=True,
                )
        else:
            if 종료일:
                ended_at = datetime.datetime.strptime(str(종료일), "%y%m%d%H%M")
            else:
                ended_at = None

        await BLACKLIST.add_blacklist(유저.id, 사유, ctx.author.id, ended_at)
        if 종료일:
            return await ctx.respond(
                f"{유저.mention}을(를) 블랙리스트에 추가하였습니다.\n>>> 사유 : ``{사유}``\n해제 예정 시각 : <t:{(str(ended_at.timestamp())).split('.')[0]}> (<t:{(str(ended_at.timestamp())).split('.')[0]}:R>)",
                ephemeral=True,
            )
        else:
            return await ctx.respond(
                f"{유저.mention}을(를) 블랙리스트에 추가하였습니다.\n>>> 사유 : ``{사유}``\n해제 예정 시각 : 무기한 차단",
                ephemeral=True,
            )

    @blacklist.command(
        name="제거",
        description="[🔒 봇 관리자 전용] 블랙리스트에서 유저를 제거합니다.",
        checks=[cog_check, dev_check],
        default_permission=False,
    )
    @permissions.is_owner()
    async def 블랙리스트_제거(
        self,
        ctx,
        유저: Option(discord.User, "블랙리스트에 추가할 유저를 입력해주세요.", required=True),
        사유: Option(str, "블랙리스트에 추가할 사유를 입력해주세요.", required=True),
    ):
        await ctx.interaction.response.defer(ephemeral=True)
        if not (await BLACKLIST.search_blacklist(유저.id)):
            return await ctx.respond(f"{유저.mention}은(는) 블랙리스트가 아닙니다.", ephemeral=True)

        await BLACKLIST.delete_blacklist(유저.id, 사유, ctx.author.id)
        return await ctx.respond(
            f"{유저.mention}을(를) 블랙리스트에서 제거하였습니다.\n>>> 사유 : ``{사유}``", ephemeral=True
        )

    # ------------------------------------- 시스템 관련 ------------------------------------- #

    system = SlashCommandGroup("시스템", "시스템 관련 명령어입니다.")

    @system.command(
        name="깃풀",
        description="[🔒 봇 관리자 전용] 깃의 최신 버전을 불러옵니다.",
        checks=[cog_check, dev_check],
        default_permission=False,
    )
    @permissions.is_owner()
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
        checks=[cog_check, dev_check],
        default_permission=False,
    )
    @permissions.is_owner()
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
