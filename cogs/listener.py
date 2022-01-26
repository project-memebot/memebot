import discord
import asyncio, aiohttp
import config
from itertools import cycle
from discord.ext import commands, tasks


class listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.presence = cycle(["{{서버}}개의 서버", "Hello, World!", "짤방러 테스트"])
        self.activity_change.start()
        if not config.BOT.TEST_MODE:
            self.update_koreanbots.start()

    def cog_unload(self):
        self.activity_change.stop()

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
            embed = Embed.warn(
                timestamp=ctx.created_at,
                description=f"사용하신 명령어는 ``{' '.join(time)}`` 뒤에 사용하실 수 있습니다.",
            )
            Embed.user_footer(embed, ctx)
            return await ctx.respond(embed=embed, ephimeral=True)
        else:
            print(error)

    @tasks.loop(seconds=10)
    async def activity_change(self):
        await self.bot.wait_until_ready()
        await self.bot.change_presence(
            activity=discord.Game(
                f"/정보 | {str(next(self.presence)).replace('{{서버}}', str(len(self.bot.guilds)))}"
            )
        )

    @tasks.loop(hours=3)
    async def update_koreanbots(self):
        await self.bot.wait_until_ready()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://koreanbots.dev/api/v2/bots/{self.bot.user.id}/stats",
                data={"servers": len(self.bot.guilds), "shards": len(self.bot.shards)},
                headers={"Authorization": config.BOT.KOREANBOTS_TOKEN},
            ) as res:
                if res.status != 200:
                    print(f"❌ | 한디리 서버수 업데이트 실패 ({(await res.json())['message']})")
                    await self.bot.get_channel(int(config.BOT.LOG_CHANNEL)).send(
                        f"❌ | 한디리 서버수 업데이트 실패 (``{(await res.json())['message']}``)"
                    )
                else:
                    print(f"✅ | 한디리 서버수 업데이트 성공 ({(await res.json())['message']})")
                    await self.bot.get_channel(int(config.BOT.LOG_CHANNEL)).send(
                        f"✅ | 한디리 서버수 업데이트 성공 (``{(await res.json())['message']}``)"
                    )


def setup(bot):
    bot.add_cog(listener(bot))
