import discord
from discord.ext import commands
from Tools.var import embedcolor


class Support(commands.Cog, name="지원"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="초대",
        aliases=("ㅊㄷ", "링크", "서포트", "지원"),
        help="봇의 초대링크와 서포트 서버 링크를 보여줍니다",
        usage="ㅉ초대",
    )
    async def _link(self, ctx):
        embed = discord.Embed(
            title="지원",
            description="[서포트 서버 초대](https://discord.gg/Jjv2MFyddt) \
        [봇 초대](https://discord.com/api/oauth2/authorize?client_id=852802390083371028&permissions=537184336 \
        &redirect_uri=https%3A%2F%2Fdiscord.gg%2FJjv2MFyddt&scope=bot)",
            color=embedcolor,
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="규칙", aliases=("ㄱㅊ",), help="짤을 업로드할때의 규칙을 보여줍니다", usage="ㅉ규칙"
    )
    async def _rule(self, ctx):
        await ctx.send(
            """
        1. 대한민국 법에 어긋나는 짤 업로드 금지
        2. 인신공격, 저격, 분쟁, 비방 등의 소지가 있는 짤 업로드 금지
        3. 홍보 목적으로 짤 업로드 금지
        4. 정치와 관련된 짤 업로드 금지
        5. 같은 짤 여러번 업로드 금지
        """
        )

    @commands.command(
        name="도움", aliases=("ㄷㅇ",), help="봇의 명령어들을 보여줍니다", usage="ㅉ도움 [명령어/카테고리]"
    )
    async def _help(self, ctx, help_=None):
        if not help_:
            await ctx.send_help()
        else:
            await ctx.send_help(help_)


def setup(bot):
    bot.add_cog(Support(bot))
