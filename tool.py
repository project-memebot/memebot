import aiosqlite as aiosql


async def get_prefix(_bot, message) -> str:
    async with aiosql.connect("memebot.db") as cur:
        async with cur.execute("SELECT * FROM customprefix WHERE guild_id=?", (message.guild.id,)) as result:
            prefix = await result.fetchall()
            return 'ㅉ' if not prefix else prefix[0][1]


errorcolor = 0xFFFF00
embedcolor = 0x0000FF


class CommandOnCooldown(Exception):
    pass


class MaxConcurrencyReached(Exception):
    pass


class UserOnBlacklist(Exception):
    pass
