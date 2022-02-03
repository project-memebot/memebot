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
        description="즐겨찾기 목록을 조회합니다.",
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
            int, "YYMMDDhhmm 형식으로 입력해주세요. 무기한 블랙리스트는 이 칸을 입력하지 말아주세요.", required=False
        ),
    ):
        await ctx.respond(f"{str(유저)}, {str(사유)}, {str(종료일)}")


# ------------------------------------------------------------------------------------------ #


def setup(bot):
    bot.add_cog(developer(bot))
