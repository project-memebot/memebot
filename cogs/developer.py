import config
import discord
import datetime
import asyncio
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

    # ------------------------------------- 블랙리스트 관련 ------------------------------------- #

    blacklist = SlashCommandGroup("블랙리스트", "블랙리스트 관련 명령어입니다.")

    @blacklist.command(
        name="추가",
        description="블랙리스트에 유저를 추가합니다.",
        guild_ids=[852766855583891486],
        checks=[cog_check],
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
        if (await BLACKLIST.search_blacklist(유저.id)):
            if (await BLACKLIST.search_blacklist(유저.id))['ended_at']:
                return await ctx.respond(f"{유저.mention}은(는) 이미 블랙리스트입니다.\n>>> 사유 : ``{(await BLACKLIST.search_blacklist(유저.id))['reason']}``\n해제 예정 시각 : <t:{str((await BLACKLIST.search_blacklist(유저.id))['ended_at'].timestamp()).split('.')[0]}> (<t:{str((await BLACKLIST.search_blacklist(유저.id))['ended_at'].timestamp()).split('.')[0]}:R>)", ephemeral=True)
            else:
                return await ctx.respond(f"{유저.mention}은(는) 이미 블랙리스트입니다.\n>>> 사유 : ``{(await BLACKLIST.search_blacklist(유저.id))['reason']}``\n해제 예정 시각 : 무기한 차단", ephemeral=True)
        else:
            if 종료일:
                ended_at = datetime.datetime.strptime(str(종료일), '%y%m%d%H%M')
            else:
                ended_at = None        

        await BLACKLIST.add_blacklist(유저.id, 사유, ctx.author.id, ended_at)
        if 종료일:
            return await ctx.respond(f"{유저.mention}을(를) 블랙리스트에 추가하였습니다.\n>>> 사유 : ``{사유}``\n해제 예정 시각 : <t:{(str(ended_at.timestamp())).split('.')[0]}> (<t:{(str(ended_at.timestamp())).split('.')[0]}:R>)", ephemeral=True)
        else:
            return await ctx.respond(f"{유저.mention}을(를) 블랙리스트에 추가하였습니다.\n>>> 사유 : ``{사유}``\n해제 예정 시각 : 무기한 차단", ephemeral=True)

    @blacklist.command(
        name="제거",
        description="블랙리스트에서 유저를 제거합니다.",
        guild_ids=[852766855583891486],
        checks=[cog_check],
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
        return await ctx.respond(f"{유저.mention}을(를) 블랙리스트에서 제거하였습니다.\n>>> 사유 : ``{사유}``", ephemeral=True)

    # ------------------------------------------------------------------------------------------ #


def setup(bot):
    bot.add_cog(developer(bot))
