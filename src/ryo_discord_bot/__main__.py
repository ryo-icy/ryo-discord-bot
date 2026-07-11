import asyncio
import logging

import discord
from discord.ext import commands

from ryo_discord_bot.cogs.message_watch import MessageWatchCog
from ryo_discord_bot.cogs.omikuji import OmikujiCog
from ryo_discord_bot.cogs.reaction_role import ReactionRoleCog
from ryo_discord_bot.settings import Settings

logger = logging.getLogger(__name__)


class RyoDiscordBot(commands.Bot):
    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="/", intents=intents)
        self.settings = settings

    # setup_hook は起動時に一度だけ呼ばれるため、再接続のたびに sync されない
    async def setup_hook(self) -> None:
        await self.add_cog(OmikujiCog(self, self.settings))
        await self.add_cog(ReactionRoleCog(self, self.settings))
        await self.add_cog(MessageWatchCog(self, self.settings))
        await self.tree.sync()

    async def on_ready(self) -> None:
        await self.change_presence(activity=discord.CustomActivity(name="りょうを監視中"))
        logger.info("%s としてログインしました。", self.user)


async def _run() -> None:
    settings = Settings.from_env()
    async with RyoDiscordBot(settings) as bot:
        await bot.start(settings.discord_token)


def main() -> None:
    discord.utils.setup_logging()
    asyncio.run(_run())


if __name__ == "__main__":
    main()
