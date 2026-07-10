import random

import discord
from discord import app_commands
from discord.ext import commands

from ryo_discord_bot.config_loader import load_config


# おみくじ機能（/omikuji, /neo_omikuji）
class OmikujiCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.omikuji_list = load_config("omikuji.txt")
        self.neo_omikuji_list = load_config("neo_omikuji.txt")

    # おみくじメッセージを送信する処理
    async def _send_omikuji(
        self, interaction: discord.Interaction, messages: list[str], count: int = 1
    ) -> None:
        result = "\n".join(random.choices(messages, k=count))
        await interaction.response.send_message(result)

    @app_commands.command(name="omikuji", description="おみくじを引くことができます")
    @app_commands.describe(arg="回数（1〜3）")
    async def omikuji(
        self, interaction: discord.Interaction, arg: app_commands.Range[int, 1, 3] = 1
    ) -> None:
        await self._send_omikuji(interaction, self.omikuji_list, arg)

    @app_commands.command(name="neo_omikuji", description="すごいおみくじを引くことができます")
    async def neo_omikuji(self, interaction: discord.Interaction) -> None:
        await self._send_omikuji(interaction, self.neo_omikuji_list)
