import discord
import asyncio
import config
from discord.ext import commands


class listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"📡 | {self.bot.user} ({('테스트 버전' if config.BOT.TEST_MODE else '정식 버전')}) 준비 완료"
        )
        await self.bot.get_channel(int(config.BOT.LOG_CHANNEL)).send(
            f"📡 | ``{self.bot.user} ({('테스트 버전' if config.BOT.TEST_MODE else '정식 버전')})`` 준비 완료"
        )

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        error = error.original

        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.errors.CheckFailure):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            cooldown = int(error.retry_after)
            hours = cooldown // 3600
            minutes = (cooldown % 3600) // 60
            seconds = cooldown % 60
            time = []
            if not hours == 0:
                time.append(f"{hours}시간")
            if not minutes == 0:
                time.append(f"{minutes}분")
            if not seconds == 0:
                time.append(f"{seconds}초")
            embed = discord.Embed(
                colour=discord.Colour.gold(),
                title="⚠ 경고",
                description=f"사용하신 명령어는 ``{' '.join(time)}`` 뒤에 사용하실 수 있어요.",
            )
            try:
                return await ctx.respond(embed=embed, ephemeral=True)
            except:
                return await ctx.send(embed=embed)
        elif isinstance(error, commands.MaxConcurrencyReached):
            embed = discord.Embed(
                colour=discord.Colour.gold(),
                title="⚠ 경고",
                description="처리 대기중인 명령어가 있어요.",
            )
            try:
                return await ctx.respond(embed=embed, ephemeral=True)
            except:
                return await ctx.send(embed=embed)
        else:
            print(error)

def setup(bot):
    bot.add_cog(listener(bot))
