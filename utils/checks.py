from utils.database import BLACKLIST
from utils.embed import Embed


async def blacklist_check(self):
    if await BLACKLIST.search(self.author.id):
        embed = Embed.ban_info(await BLACKLIST.search(self.author.id))
        await self.respond(embed=embed, ephemeral=True)
        return False
    else:
        return True
