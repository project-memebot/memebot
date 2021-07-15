import aiosqlite as aiosql


async def get_prefix(_bot, message) -> str:
    async with aiosql.connect("memebot.db") as cur:
        async with cur.execute("SELECT * FROM customprefix") as result:
            for i in result:
                if i[0] == message.guild.id:
                    return i[1]
            return "ㅉ"


errorcolor = 0xFFFF00
embedcolor = 0x0000FF
