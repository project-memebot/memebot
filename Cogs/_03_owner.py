from discord.ext import commands
import discord
import aiosqlite as aiosql


class Owner(commands.Cog, name="오너"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="블랙", aliases=("밴", "차단"), usage="<유저 멘션> <이유>", help="봇에게서 유저를 차단합니다."
    )
    @commands.is_owner()
    async def _addblack(self, ctx, user: discord.User, *, reason=None):
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            await cur.execute(f'INSERT INTO blacklist VALUES({user.id}, "{reason}")')
        await ctx.reply(f"{user.mention} 유저가 정상적으로 차단 처리 되었습니다.")
        await user.send('`' + reason + '`라는 이유로 짤방러에게서 차단 처리되었습니다.\n이의는 서포트 서버에서 티켓을 열어 주세요.')

    @commands.command(
        name="강제제거", aliases=("강제삭제",), usage="<짤 id>", help="강제로 짤을 지웁니다"
    )
    @commands.is_owner()
    async def _remove_forcing(self, ctx, meme_id: int):
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            await cur.execute("DELETE FROM usermeme WHERE id=?", (meme_id,))
        await (
            await self.bot.get_channel(852811274886447114).fetch_message(meme_id)
        ).delete()
        await ctx.reply("완료")


def setup(bot):
    bot.add_cog(Owner(bot))
