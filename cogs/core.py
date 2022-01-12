import config
import discord
import datetime
import asyncio
from discord.ext import commands
from discord.commands import slash_command, Option, permissions
from utils.embed import *
from utils.database import *

class core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self):
        if await BLACKLIST.search_blacklist(self.author.id):
            embed = Embed.ban_info(await BLACKLIST.search_blacklist(self.author.id))
            await self.respond(embed=embed, ephemeral=True)
            return False
        else:
            return True

    @commands.slash_command(name="정보", description="'짤방러' 봇의 자세한 정보를 알아볼 수 있어요.", guild_ids=[852766855583891486], checks=[cog_check])
    async def 정보(self, ctx):
        # 짤 로드할 때 필요할듯 - await ctx.interaction.response.defer()
        embed = discord.Embed(
            title=f"<:jbllogo:929615468233363457> {self.bot.user.name} 정보",
            color=0x5865F2
        )
        embed.add_field(name="출시일", value=f"<t:1628870848> (<t:1628870848:R>)")
        embed.add_field(name="핑 (레이턴시)", value=f"``{round(self.bot.latency * 1000)}ms``", inline=False)
        embed.add_field(name="서버 수", value=f"``{format(len(self.bot.guilds), ',')}개``")
        embed.add_field(name="개발 팀", value=f"``Studio Orora``")
        embed.set_thumbnail(url=self.bot.user.avatar)
        await ctx.respond("https://discord.gg/FP6JwVDRDc", embed=embed)

def setup(bot):
    bot.add_cog(core(bot))