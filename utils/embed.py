import discord
import datetime

class Embed:
    def ban_info(info:dict):
        """
        info (dict): 필수, info(utils.database 블랙 데이터 반환값)
        """
        embed = discord.Embed(title="❌ | 시스템에서 차단됨", description=f"<@{info['_id']}>님은 시스템에서 차단조치되었어요.\n사유가 올바르지 않거나, 이의를 제기하고 싶으시다면 [Studio Orora 커뮤니티](https://discord.gg/FP6JwVDRDc)의 문의 채널에서 문의 부탁드립니다!", color=0x5865F2)
        embed.add_field(name="차단 사유", value=f"```{info['reason']}```", inline=False)
        if info['ended_at']:
            embed.add_field(name="차단 해제 시각", value=f"<t:{str((info['ended_at']).timestamp()).split('.')[0]}> (<t:{str((info['ended_at']).timestamp()).split('.')[0]}:R>)", inline=False)
        return embed