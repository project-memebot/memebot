from logging import error
import aiosqlite as aiosql
import discord
from discord.ext import commands
from tool import embedcolor, errorcolor
from discord_components import Button, ButtonStyle


class Support(commands.Cog, name="지원"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="링크",
        aliases=("ㄹㅋ", "초대", "서포트", "지원"),
        help="봇의 초대링크와 서포트 서버 링크를 보여줍니다",
    )
    async def _link(self, ctx):
        embed = discord.Embed(
            title="지원",
            description=">>> [서포트 서버 초대](http://support.memebot.kro.kr)\n\
            [봇 초대](http://invite.memebot.kro.kr)",
            color=embedcolor,
        )
        await ctx.send(embed=embed)

    @commands.command(name="규칙", aliases=("ㄱㅊ",), help="짤을 업로드할때의 규칙을 보여줍니다")
    async def _rule(self, ctx):
        await ctx.send(
            """
        1. 대한민국 법에 어긋나는 짤 업로드 금지
        2. 인신공격, 저격, 분쟁, 비방 등의 소지가 있는 짤 업로드 금지
        3. 홍보 목적으로 짤 업로드 금지
        4. 정치와 관련된 짤 업로드 금지
        5. 같은 짤 여러번 업로드 금지
        6. 특정 정치 사상을 가지거나 특정인들의 팬 등 소수들만 웃긴 짤 금지
        7. 버그 악용 금지
        8. 불쾌할 수 있는 짤 업로드 금지(특히 nsfw)
        """
        )

    @commands.command(
        name="도움", aliases=("ㄷㅇ", "help"), help="봇의 명령어들을 보여줍니다", usage="[명령어]"
    )
    async def _help(self, ctx, *, help_=None):
        async with aiosql.connect("memebot.db") as cur:
            async with cur.execute(
                "SELECT * FROM customprefix WHERE guild_id=?", (ctx.guild.id,)
            ) as result:
                prefix = await result.fetchall()
                prefix = prefix[0][1] if prefix else "ㅉ"
        if help_ is None:
            embed = discord.Embed(
                title="도움말",
                description=f"> [초대](http://invite.memebot.kro.kr),\
            [공식 서버](http://support.memebot.kro.kr) \
            \n\n> <>는 봇을 사용하는 데에 있어서 필수적인 값, []는 필수적이지 않은 값입니다. \
            \n> `[]`와 `<>`는 빼고 입력해 주세요. \
            \n\n> **Made by {await self.bot.fetch_user(745848200195473490)}**\n",
                color=embedcolor,
            )
            embed.set_footer(text=f'{ctx.guild} 서버의 접두사는 "{prefix}"입니다')
            cogs = self.bot.cogs
            for i in cogs:
                if ctx.author.id not in self.bot.owner_ids:
                    if i in ["오너", "Jishaku"]:
                        continue
                cmds = [j for j in cogs[i].get_commands()]
                for j in cmds:
                    if not j.enabled:
                        del cmds[cmds.index(j)]
                embed.add_field(
                    name=f"**{i}**",
                    value="**" + " ".join([j.name for j in cmds]) + "**",
                )
            return await ctx.reply(embed=embed)
        cmd = self.bot.get_command(help_)
        if cmd is None or (not cmd.enabled):
            return await ctx.reply(f"{cmd} 명령어를 찾을 수 없습니다.")
        embed = discord.Embed(
            title=f"도움말",
            description=f"**{cmd.qualified_name if cmd.parents else cmd.name} \
        **```diff\n+ {cmd.help}```",
            color=embedcolor,
        )
        embed.add_field(
            name="별칭",
            value=f"`{'`, `'.join(cmd.aliases)}`" if cmd.aliases else "",
        )
        embed.add_field(
            name="사용법",
            value=f"`{prefix}{cmd.qualified_name if cmd.parents else cmd.name} {'' if cmd.usage is None else cmd.usage}`",
        )
        await ctx.reply(embed=embed)

    @commands.command(
        name="크레딧",
        aliases=("기여자",),
        help="봇을 만들 때 도움을 주신 분들과 이미지들의 출처를 보여줍니다",
    )
    async def _credit(self, ctx):
        embed = discord.Embed(
            title="크레딧",
            description="[프로필 사진 원본 이미지](https://www.flaticon.com/free-icon/picture_2659360?term=image&page=1\
            &position=10&page=1&position=10&related_id=2659360&origin=search)\n\
            프로필 사진 제작자 - <@441202161481809922>",
            color=embedcolor,
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="접두사", aliases=("prefix",), help="서버의 커스텀 접두사를 변경합니다", usage="<바꿀 접두사>"
    )
    @commands.has_permissions(manage_guild=True)
    async def _prefix(self, ctx, *, prefix):
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            async with cur.execute(
                "SELECT * FROM customprefix WHERE guild_id=?", (ctx.guild.id,)
            ) as result:
                if not await result.fetchall():
                    await cur.execute(
                        f'INSERT INTO customprefix VALUES({ctx.guild.id}, "{prefix}")'
                    )
                else:
                    await cur.execute(
                        "UPDATE customprefix SET prefix=? WHERE guild_id=?",
                        (prefix, ctx.guild.id),
                    )
        await ctx.reply(f"{ctx.guild} 서버의 접두사가 `{prefix}`로 설정되었습니다.")

    @commands.command(name="가입", help="짤방러 봇의 사용 권한을 얻습니다.", enabled=False)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def _join(self, ctx):
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            async with cur.execute(
                "SELECT * FROM joined WHERE id=?", (ctx.author.id,)
            ) as result:
                if await result.fetchall():
                    return await ctx.reply(
                        embed=discord.Embed(
                            title="가입 실패", description="이미 가입되었습니다.", color=errorcolor
                        )
                    )
        embed = discord.Embed(
            title="약관 동의",
            description="[짤방러 봇의 개인정보 처리 약관](http://tos.memebot.kro.kr)에\
                동의하시면 동의, 아니면 미동의를 눌러주세요.\n\
                    미동의시 봇 사용이 불가능합니다.",
            color=embedcolor,
        )
        msg = await ctx.reply(
            embed=embed,
            components=[
                [
                    Button(style=ButtonStyle.green, label="동의", emoji="✅"),
                    Button(style=ButtonStyle.red, label="미동의", emoji="❎"),
                ]
            ],
        )
        try:
            await self.bot.wait_for(
                "button_click",
                check=lambda i: i.author == ctx.author
                and i.channel == ctx.channel
                and i.component.label == "동의",
            )
        except __import__("asyncio").TimeoutError:
            return await ctx.reply("가입이 취소되었습니다.")
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            await cur.execute(f"INSERT INTO joined VALUES ({ctx.author.id})")
        await msg.edit(embed=discord.Embed(title='가입 성공', description='성공적으로 가입되었습니다', color=embedcolor), component=[])

    @commands.command(name="탈퇴", help="짤방러 봇의 사용 권한을 포기하고 개인정보를 삭제합니다.", enabled=False)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def _leave(self, ctx):
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            async with cur.execute(
                f"SELECT * FROM joined WHERE id=?", (ctx.author.id,)
            ) as result:
                if not await result.fetchall():
                    return await ctx.reply(
                        embed=discord.Embed(
                            title="탈퇴 실패", description="가입된 적이 없습니다.", color=errorcolor
                        )
                    )
        embed = discord.Embed(
            title="짤방러 탈퇴",
            description="정말로 짤방러 서비스를 탈퇴하시겠습니까?\n모든 정보는 지워지며, 복구할 수 없습니다.",
            color=embedcolor,
        )
        msg = await ctx.reply(
            embed=embed,
            components=[
                [
                    Button(style=ButtonStyle.green, label="탈퇴", emoji="✅"),
                    Button(style=ButtonStyle.red, label="취소", emoji="❎"),
                ]
            ],
        )
        try:
            await self.bot.wait_for(
                "button_click",
                check=lambda i: i.author == ctx.author
                and i.channel == ctx.channel
                and i.component.label == "탈퇴",
            )
        except __import__("asyncio").TimeoutError:
            return await ctx.reply("탈퇴가 취소되었습니다.")
        async with aiosql.connect("memebot.db", isolation_level=None) as cur:
            async with cur.execute(
                f"SELECT * FROM usermeme WHERE id=?", (ctx.author.id,)
            ) as result:
                result = await result.fetchall()
            for i in result:
                await cur.execute(f"UPDATE joined SET id=? WHERE id=?", (0, i[0]))
            await cur.execute(f"DELETE FROM joined WHERE id=?", (ctx.author.id,))
        await msg.edit(embed=discord.Embed(title='탈퇴 완료', description='성공적으로 탈퇴되었습니다', color=embedcolor), components=[])



def setup(bot):
    bot.add_cog(Support(bot))
