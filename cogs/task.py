import discord
import datetime
import asyncio, aiohttp
import config
from itertools import cycle
from discord.ext import commands, tasks
from utils.database import BLACKLIST


class task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.presence = cycle(
            [
                "{{서버}}개의 서버",
                "재미있는 짤을 한곳에서, 짤방러",
                "http://koreanbots.memebot.kro.kr",
                "http://invite.memebot.kro.kr",
            ]
        )
        self.activity_change.start()
        if not config.BOT.TEST_MODE:
            self.blacklist_check.start()
            self.update_koreanbots.start()

    def cog_unload(self):
        self.activity_change.stop()
        self.blacklist_check.stop()

    @tasks.loop(seconds=10)
    async def activity_change(self):
        await self.bot.wait_until_ready()
        await self.bot.change_presence(
            activity=discord.Game(
                f"/정보 | {str(next(self.presence)).replace('{{서버}}', str(len(self.bot.guilds)))}"
            )
        )

    @tasks.loop(minutes=1)
    async def blacklist_check(self):
        await self.bot.wait_until_ready()
        now = datetime.datetime.now()
        time_list = await BLACKLIST.blacklist_list(
            {
                "ended_at": datetime.datetime(
                    now.year, now.month, now.day, now.hour, now.minute
                )
            }
        )
        for user in time_list:
            await BLACKLIST.delete_blacklist(
                user["user_id"], "블랙리스트 기간이 끝나 자동적으로 해제되었어요.", self.bot.user.id
            )
            try:
                await (await self.bot.fetch_user(user.id)).send(
                    f"안녕하세요, {user.mention}!\n\n이용자님의 블랙리스트가 해제되었습니다.\n> 사유 : ``{reason}``\n\n**이제 다시 짤방러 서비스를 사용하실 수 있습니다. 다만 같은 행동을 반복하신다면 다시 블랙리스트에 등재되실 수 있으니 이용에 참고해주세요.**"
                )
            except:
                pass
            print(f"✅ | 블랙리스트 기간이 끝나 자동적으로 {user['user_id']}의 블랙리스트를 해제하였어요.")

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
    bot.add_cog(task(bot))
