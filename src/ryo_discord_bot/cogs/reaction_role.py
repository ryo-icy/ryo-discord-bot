import logging

import discord
from discord.ext import commands

from ryo_discord_bot.settings import Settings

logger = logging.getLogger(__name__)


# 特定のメッセージへのリアクションでロールを付与する機能
class ReactionRoleCog(commands.Cog):
    def __init__(self, bot: commands.Bot, settings: Settings) -> None:
        self.bot = bot
        self.settings = settings

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.message_id != self.settings.target_message_id:
            return
        member = payload.member
        if member is None or member.bot:
            return
        role = member.guild.get_role(self.settings.default_role_id)
        if role is None or role in member.roles:
            return
        try:
            await member.add_roles(role)
            logger.info("%s にロールを付与しました。", member)
        except discord.Forbidden:
            logger.error(
                "ロール(ID: %s)を付与する権限がありません。"
                "Botのロールを対象ロールより上に配置してください。",
                self.settings.default_role_id,
            )
