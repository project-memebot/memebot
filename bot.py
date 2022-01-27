import discord
import os
import config
import jishaku
from discord.ext import commands

if config.BOT.TEST_MODE:
    prefix = config.BOT.TEST_PREFIX
    token = config.BOT.TEST_TOKEN
else:
    prefix = config.BOT.BOT_PREFIX
    token = config.BOT.BOT_TOKEN

bot = commands.AutoShardedBot(
    command_prefix=prefix,
    intents=None,
    help_command=None,
    owner_ids=config.BOT.OWNER_IDS,
    allowed_mentions=discord.AllowedMentions.none(),
)

bot.load_extension("jishaku")
print("✅ | 로드 - Jishaku")
for file in os.listdir("cogs/"):
    if file.endswith(".py"):
        try:
            bot.load_extension(f"cogs.{file[:-3]}")
            print(f"✅ | 로드 - cogs.{file[:-3]}")
        except Exception as error:
            print(f"❌ | 로드 실패 - cogs.{file[:-3]} ({error})")

bot.run(token)
