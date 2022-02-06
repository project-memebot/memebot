import discord
import config
import datetime
import asyncio, aiohttp
from utils.database import *


class Embed:
    def ban_info(info: dict):
        """
        info (dict): 필수, info(utils.database 블랙 데이터 반환값)
        """
        embed = discord.Embed(
            title="❌ | 시스템에서 차단됨",
            description=f"<@{info['user_id']}>님은 시스템에서 차단조치되었어요.\n사유가 올바르지 않거나, 이의를 제기하고 싶으시다면 [Studio Orora 커뮤니티](https://support.studio-orora.kro.kr)의 문의 채널에서 문의 부탁드립니다!",
            color=0x5865F2,
        )
        embed.add_field(name="차단 사유", value=f"```{info['reason']}```", inline=False)
        if info["ended_at"]:
            embed.add_field(
                name="차단 해제 시각",
                value=f"<t:{str((info['ended_at']).timestamp()).split('.')[0]}> (<t:{str((info['ended_at']).timestamp()).split('.')[0]}:R>)",
                inline=False,
            )
        return embed

    async def meme_embed(result, user):
        date = result["upload_at"] + datetime.timedelta(hours=9)
        embed = discord.Embed(timestamp=date, color=0x5865F2)
        if result["title"]:
            embed.title = result["title"]
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://discord.com/api/users/{result['uploader_id']}",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bot {config.BOT.BOT_TOKEN}",
                },
            ) as res:
                re = await res.json()
                try:
                    if re["avatar"]:
                        embed.set_author(
                            name=f"{re['username']}#{re['discriminator']}",
                            icon_url=f"https://cdn.discordapp.com/avatars/{result['uploader_id']}/{re['avatar']}.png",
                            url=f"https://discord.com/users/{result['uploader_id']}",
                        )
                    else:
                        embed.set_author(
                            name=f"{re['username']}#{re['discriminator']}",
                            icon_url=f"https://pnggrid.com/wp-content/uploads/2021/05/Discord-Logo-Circle-1024x1024.png",
                            url=f"https://discord.com/users/{result['uploader_id']}",
                        )
                except:
                    embed.set_author(
                        name=f"유저를 조회할 수 없습니다.",
                        icon_url="https://pnggrid.com/wp-content/uploads/2021/05/Discord-Logo-Circle-1024x1024.png",
                    )
        embed.set_image(url=result["url"])

        favorite_button = discord.ui.Button(
            label=f"즐겨찾기",
            emoji="⭐",
            style=discord.ButtonStyle.green,
            custom_id=f"favorite-{result['_id']}",
        )
        rerandom_button = discord.ui.Button(
            label="다른 짤 보기",
            emoji="🔁",
            style=discord.ButtonStyle.blurple,
            custom_id=f"rerandom-{user.id}",
        )
        report_button = discord.ui.Button(
            label="신고하기",
            emoji="🚨",
            style=discord.ButtonStyle.red,
            custom_id=f"report-{result['_id']}",
        )
        view = discord.ui.View()
        view.add_item(favorite_button)
        view.add_item(rerandom_button)
        view.add_item(report_button)
        return {"embed": embed, "view": view}
