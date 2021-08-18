import aiosqlite as aiosql
import discord
import aiofiles
import aiohttp
from discord.ext import commands
from discord_components import Button, ButtonStyle, Select, SelectOption, Component, ActionRow
from os import remove
from typing import Union, List


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
            result = await result.fetchall()
    if not result:
        raise ValueError("Can't find meme")
    result = result[0]
    embed = discord.Embed(title=result[2], color=embedcolor)
    embed.set_image(url=result[3])
    if result[1] == 0:
        embed.set_author(name="탈퇴한 유저")
    else:
        try:
            uploader = await bot.fetch_user(result[1])
            embed.set_author(icon_url=uploader.avatar_url, name=str(uploader))
        except discord.NotFound:
            embed.set_author(name="사용자 정보를 찾을 수 없음")
    embed.set_footer(text=f"짤 ID: {result[0]}")
    await msg.edit(embed=embed)
    return await msg.channel.fetch_message(msg.id)


async def set_buttons(ctx: commands.Context):
    return await ctx.send(
        embed=discord.Embed(title="밈을 불러오는중..."),
        components=[Button(style=ButtonStyle.red, label="🚨 신고하기")],
    )


async def send_component_msg(
    channel: discord.abc.Messageable,
    content: str = "",
    *,
    tts: bool = False,
    embed: discord.Embed = None,
    file: discord.File = None,
    files: List[discord.File] = None,
    mention_author: bool = None,
    allowed_mentions: discord.AllowedMentions = discord.AllowedMentions.none(),
    reference: discord.Message = None,
    components: List[Union[ActionRow, Component, List[Component]]] = None,
    delete_after: float = None,
    nonce: Union[str, int] = None,
    **options,
    ) -> discord.Message:
    await channel.send(content=content, tts=tts, embed=embed, file=file, files=files, mention_author=mention_author, allowed_mentions=allowed_mentions, reference=reference, components=components, delete_after=delete_after, nonce=nonce, **options)


async def reply_component_msg_prop(msg, *args, **kwargs):
    return await send_component_msg(msg.channel, *args, **kwargs, reference=msg)


class UserOnBlacklist(Exception):
    pass


class NotJoined(Exception):
    pass
