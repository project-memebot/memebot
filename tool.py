import aiosqlite as aiosql
import discord


errorcolor = 0xFFFF00
embedcolor = 0x0000FF


async def get_prefix(_bot, message) -> str:
    async with aiosql.connect("memebot.db") as cur:
        async with cur.execute(
            "SELECT * FROM customprefix WHERE guild_id=?", (message.guild.id,)
        ) as result:
            prefix = await result.fetchall()
            return "ㅉ" if not prefix else prefix[0][1]


async def sendmeme(bot, memeid, msg):
    async with aiosql.connect("memebot.db") as cur:
        async with cur.execute(
            "SELECT * FROM usermeme WHERE id=?", (memeid,)
        ) as result:
            result = (await result.fetchall())[0]
            if not result:
                raise ValueError("Can't find meme")
            embed = discord.Embed(title=result[2], color=embedcolor)
            embed.set_image(url=result[3])
            uploader = await bot.fetch_user(result[1])
            embed.set_author(icon_url=uploader.avatar_url, name=str(uploader))
            embed.set_footer(text=f"짤 ID: {result[0]}")
            return await msg.edit(embed=embed)


class CommandOnCooldown(Exception):
    pass


class MaxConcurrencyReached(Exception):
    pass


class UserOnBlacklist(Exception):
    pass
