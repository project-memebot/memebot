import config
import discord
import datetime
import asyncio
from discord.ext import commands, pages
from discord.commands import slash_command, Option, permissions, SlashCommandGroup
from utils.embed import *
from utils.database import *


class user(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# ------------------------------------- 권한 확인 관련 함수 ------------------------------------- #

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

# ---------------------------------------------------------------------------------------------- #

    @commands.slash_command(
        name="가입",
        description="'짤방러' 서비스에 가입합니다.",
        guild_ids=[852766855583891486],
        checks=[cog_check],
    )
    @commands.max_concurrency(1, commands.BucketType.user)
    async def 가입(self, ctx):
        if await USER_DATABASE.user_find(ctx.author.id):
            return await ctx.respond(f"{ctx.author.mention}, 이미 ``{self.bot.user.name} 서비스``에 가입되어 있어요.\n탈퇴는 ``/탈퇴`` 명령어로 할 수 있어요.")

        await ctx.interaction.response.defer()
        register_yes = discord.ui.Button(
            label=f"네",
            emoji="<:jblcheck:936927677070331925>",
            style=discord.ButtonStyle.green,
            custom_id=f"register_yes",
        )
        register_no = discord.ui.Button(
            label="아니요",
            emoji="<:jblcancel:936927690580189204>",
            style=discord.ButtonStyle.red,
            custom_id=f"register_no",
        )
        view = discord.ui.View()
        view.add_item(register_yes)
        view.add_item(register_no)

        msg = await ctx.respond(f"{ctx.author.mention}, ``{self.bot.user.name} 서비스``에 가입하시겠습니까?", view=view)

        def check(inter):
            return inter.user.id == ctx.author.id and inter.message.id == msg.id
        try:
            interaction_check = await self.bot.wait_for('interaction', check=check, timeout=60.0)
        except asyncio.TimeoutError:
            return await ctx.edit(content=f"{ctx.author.mention}, 시간이 초과되었어요... 언제든지 다시 ``/가입`` 명령어로 가입하실 수 있어요!", embed=None, view=None)

        if interaction_check.data['custom_id'] == "register_yes":
            await USER_DATABASE.user_insert(ctx.author.id)
            return await ctx.edit(content=f"{ctx.author.mention}, 가입이 완료되었어요!", embed=None, view=None)
        if interaction_check.data['custom_id'] == "register_no":
            return await ctx.edit(content=f"{ctx.author.mention}, 가입이 취소되었어요... 언제든지 다시 ``/가입`` 명령어로 가입하실 수 있어요!", embed=None, view=None)

def setup(bot):
    bot.add_cog(user(bot))
