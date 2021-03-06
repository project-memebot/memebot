import asyncio

import discord
from discord.ext import commands

import config


class listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"π‘ | {self.bot.user} ({('νμ€νΈ λ²μ ' if config.BOT.TEST_MODE else 'μ μ λ²μ ')}) μ€λΉ μλ£"
        )
        await self.bot.get_channel(int(config.BOT.LOG_CHANNEL)).send(
            f"π‘ | ``{self.bot.user} ({('νμ€νΈ λ²μ ' if config.BOT.TEST_MODE else 'μ μ λ²μ ')})`` μ€λΉ μλ£"
        )

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        error = error.original

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
                time.append(f"{hours}μκ°")
            if not minutes == 0:
                time.append(f"{minutes}λΆ")
            if not seconds == 0:
                time.append(f"{seconds}μ΄")
            embed = discord.Embed(
                colour=discord.Colour.gold(),
                title="β  κ²½κ³ ",
                description=f"μ¬μ©νμ  λͺλ Ήμ΄λ ``{' '.join(time)}`` λ€μ μ¬μ©νμ€ μ μμ΄μ.",
            )
            try:
                return await ctx.respond(embed=embed, ephemeral=True)
            except:
                return await ctx.send(embed=embed)
        elif isinstance(error, commands.MaxConcurrencyReached):
            embed = discord.Embed(
                colour=discord.Colour.gold(),
                title="β  κ²½κ³ ",
                description="μ²λ¦¬ λκΈ°μ€μΈ λͺλ Ήμ΄κ° μμ΄μ.",
            )
            try:
                return await ctx.respond(embed=embed, ephemeral=True)
            except:
                return await ctx.send(embed=embed)
        else:
            print(error)


def setup(bot):
    bot.add_cog(listener(bot))
