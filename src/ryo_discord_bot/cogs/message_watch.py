import random
import re

import discord
from discord.ext import commands

from ryo_discord_bot.config_loader import load_config
from ryo_discord_bot.settings import Settings

# Minecraft UUID 検知パターン
UUID_PATTERN = re.compile(
    r"Minecraft UUID: ([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    re.IGNORECASE,
)


# メッセージ監視機能（Minecraft UUID 検知・メンション返答）
class MessageWatchCog(commands.Cog):
    def __init__(self, bot: commands.Bot, settings: Settings) -> None:
        self.bot = bot
        self.settings = settings
        self.mention_responses = load_config("mention.txt")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.bot.user:
            return

        # Minecraft UUID を検知したら NameMC の検索 URL を指定チャンネルへ投稿
        match = UUID_PATTERN.search(message.content)
        if match:
            url = f"https://ja.namemc.com/search?q={match.group(1)}"
            channel = self.bot.get_channel(self.settings.namemc_channel_id)
            if channel:
                await channel.send(url)

        # メンションされたらランダムな一文を返答
        if self.bot.user in message.mentions:
            await message.channel.send(random.choice(self.mention_responses))
