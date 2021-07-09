from discord.ext import commands
import sqlite3 as sql


class Owner(commands.Cog, name="오너"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="sql",
        aliases=("SQL", "SQLITE", "sqlite"),
        usage="<스크립트>",
        help="SQL 스크립트를 실행합니다.",
    )
    @commands.is_owner()
    async def _sql(self, ctx, *, script):
        conn = sql.connect("memebot.db", isolation_level=None)
        cur = conn.cursor()
        for i in script.split("\n"):
            cur.execute(i)
        await ctx.reply(str(cur.fetchall()))
        conn.close()

    @commands.command(
        name="강제제거", aliases=("강제삭제",), usage="<짤 id>", help="강제로 짤을 지웁니다"
    )
    @commands.is_owner()
    async def _remove_forcing(self, ctx, meme_id: int):
        conn = sql.connect("memebot.db", isolation_level=None)
        cur = conn.cursor()
        cur.execute("DELETE FROM usermeme WHERE id=?", (meme_id,))
        conn.close()
        await ctx.reply("완료")


def setup(bot):
    bot.add_cog(Owner(bot))
