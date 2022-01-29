import config
import discord
import datetime
import asyncio
from discord.ext import commands
from discord.commands import slash_command, Option, permissions
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
                    await interaction.followup.send(
                        result["message"], ephemeral=True
                    )

    @commands.slash_command(
        name="랜덤",
        description="랜덤으로 밈을 찾아볼 수 있어요!",
        guild_ids=[852766855583891486],
        checks=[cog_check],
    )
    async def 밈_랜덤(self, ctx):
        await ctx.interaction.response.defer()
        result = await Embed.meme_embed(
            result=await MEME_DATABASE.random_meme(), user=ctx.author
        )
        await ctx.respond(embed=result["embed"], view=result["view"])


def setup(bot):
    bot.add_cog(meme(bot))
