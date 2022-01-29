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

    @commands.slash_command(
        name="가이드라인",
        description="'짤방러' 봇의 가이드라인을 확인할 수 있어요.",
        guild_ids=[852766855583891486],
        checks=[cog_check],
    )
    async def 가이드라인(self, ctx):
        embed = discord.Embed(
            title=f"<:jbllogo:929615468233363457> {self.bot.user.name} 가이드라인",
            description="""
**1. 대한민국 법을 준수해주세요.** 대한민국 법은 아래의 가이드라인들보다 우선 적용됩니다.

**2. 인신공격, 저격, 분쟁, 비방 등 논란의 소지가 있는 짤은 업로드가 금지돼요.**

**3. 홍보 목적으로 짤을 올리지 마세요.** 의도치 않은 상호 노출은 가능합니다. (신고 시 개발진 판단에 따라 결정됩니다.)

**4. 정치와 관련된 짤은 올릴 수 없어요.** 정치는 위 2번 규칙과 같이 논란의 소지가 있을 수 있어요.

**5. 같은 짤을 고의로 여러 번 올리시면 안 돼요.** 실수라면 몇 번 봐 드릴 수 있습니다만, 고의로 하신다면 사용 차단이 될 수 있습니다.

**6. 특정 소수만 알 수 있는 짤은 주의해주세요.** 업로드가 아예 금지되지는 않지만, 모두의 짤방러이니 모두가 재밌는 짤을 업로드 부탁드립니다.

**7. 다른 유저들이 불쾌할 수 있는 짤은 올리실 수 없어요.** 모두가 사용하는 짤방러인 만큼 양해 부탁드립니다.

**8. NSFW (19금) 등 야한 사진, 성적인 짤은 업로드가 금지돼요.** 여러 나이의 사람들이 사용하는 만큼 양해 부탁드립니다!

**9. 버그를 악용하지 말아주세요.** 짤방러는 개발자가 열심히 만든다고 만들었지만, 버그가 존재할 수 있고, 그를 악용하면 짤방러의 운영이 중단될 수 있습니다.
""",
            color=0x5865F2,
        )
        await ctx.respond(embed=embed)

    @commands.slash_command(
        name="정보",
        description="'짤방러' 봇의 자세한 정보를 알아볼 수 있어요.",
        guild_ids=[852766855583891486],
        checks=[cog_check],
    )
    async def 정보(self, ctx):
        embed = discord.Embed(
            title=f"<:jbllogo:929615468233363457> {self.bot.user.name} 정보",
            color=0x5865F2,
        )
        embed.add_field(name="출시일", value=f"<t:1628870848> (<t:1628870848:R>)")
        embed.add_field(
            name="핑 (레이턴시)",
            value=f"``{round(self.bot.latency * 1000)}ms``",
            inline=False,
        )
        embed.add_field(name="서버 수", value=f"``{format(len(self.bot.guilds), ',')}개``")
        embed.add_field(name="개발 팀", value=f"``Studio Orora``")
        embed.set_thumbnail(url=self.bot.user.avatar)
        await ctx.respond("https://discord.gg/FP6JwVDRDc", embed=embed)

    @commands.slash_command(
        name="크레딧",
        description="'짤방러' 봇의 크레딧(기타 정보)을 알아볼 수 있어요.",
        guild_ids=[852766855583891486],
        checks=[cog_check],
    )
    async def 크레딧(self, ctx):
        embed = discord.Embed(
            title=f"<:jbllogo:929615468233363457> {self.bot.user.name} 크레딧",
            description="**프로필 관련**\n\n- [프로필 사진 원본 이미지](https://www.flaticon.com/free-icon/picture_2659360?term=image&page=1&position=10&page=1&position=10&related_id=2659360&origin=search)\n- 프로필 사진 제작자 : <@441202161481809922>",
            color=0x5865F2,
        )
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(core(bot))
