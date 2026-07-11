import asyncio
import random
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from ryo_discord_bot.config_loader import load_config
from ryo_discord_bot.settings import Settings
from ryo_discord_bot.storage import GlobalStats, OmikujiStore, PersonalStats, ResultCount


# おみくじ機能（/omikuji, /neo_omikuji, /omikuji_status）
class OmikujiCog(commands.Cog):
    def __init__(self, bot: commands.Bot, settings: Settings) -> None:
        self.bot = bot
        self.omikuji_list = load_config("omikuji.txt")
        self.neo_omikuji_list = load_config("neo_omikuji.txt")
        self.store = OmikujiStore(settings.omikuji_db_path)

    def cog_unload(self) -> None:
        self.store.close()

    # おみくじメッセージを送信し、結果を記録する処理
    async def _send_omikuji(
        self,
        interaction: discord.Interaction,
        messages: list[str],
        *,
        command: str,
        count: int = 1,
    ) -> None:
        drawn = random.choices(messages, k=count)
        await interaction.response.send_message("\n".join(drawn))

        # neo_omikuji は「運勢, 説明」形式なので、記録は運勢部分のみにする
        results = [line.split(",", 1)[0].strip() for line in drawn]
        await asyncio.to_thread(
            self.store.record, interaction.guild_id, interaction.user.id, command, results
        )

    @app_commands.command(name="omikuji", description="おみくじを引くことができます")
    @app_commands.describe(arg="回数（1〜3）")
    async def omikuji(
        self, interaction: discord.Interaction, arg: app_commands.Range[int, 1, 3] = 1
    ) -> None:
        await self._send_omikuji(interaction, self.omikuji_list, command="omikuji", count=arg)

    @app_commands.command(name="neo_omikuji", description="すごいおみくじを引くことができます")
    async def neo_omikuji(self, interaction: discord.Interaction) -> None:
        await self._send_omikuji(interaction, self.neo_omikuji_list, command="neo_omikuji")

    @app_commands.command(name="omikuji_status", description="おみくじの結果を確認できます")
    @app_commands.describe(scope="表示範囲（個人 / 全体）")
    async def omikuji_status(
        self, interaction: discord.Interaction, scope: Literal["個人", "全体"] = "個人"
    ) -> None:
        if scope == "個人":
            stats = await asyncio.to_thread(
                self.store.personal_stats, interaction.guild_id, interaction.user.id
            )
            embed = self._build_personal_embed(interaction.user, stats)
        else:
            stats = await asyncio.to_thread(self.store.global_stats, interaction.guild_id)
            embed = self._build_global_embed(stats)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # 個人統計用の Embed を組み立てる
    def _build_personal_embed(
        self, user: discord.User | discord.Member, stats: PersonalStats
    ) -> discord.Embed:
        embed = discord.Embed(title=f"{user.display_name} さんのおみくじ結果", color=0xF4C542)

        if not stats["command_counts"]:
            embed.description = "まだおみくじを引いた記録がありません。"
            return embed

        embed.add_field(
            name="実行回数",
            value="\n".join(f"{c['command']}: {c['count']}回" for c in stats["command_counts"]),
            inline=False,
        )
        embed.add_field(
            name="出た結果の回数",
            value=_format_result_counts(stats["result_counts"]),
            inline=False,
        )
        embed.add_field(
            name="直近10件",
            value="\n".join(
                f"[{d['created_at']}] {d['command']}: {d['result']}" for d in stats["recent_draws"]
            ),
            inline=False,
        )
        return embed

    # 全体統計用の Embed を組み立てる
    def _build_global_embed(self, stats: GlobalStats) -> discord.Embed:
        embed = discord.Embed(title="サーバ全体のおみくじ結果", color=0xF4C542)

        if not stats["command_counts"]:
            embed.description = "まだおみくじを引いた記録がありません。"
            return embed

        embed.add_field(
            name="実行回数",
            value="\n".join(f"{c['command']}: {c['count']}回" for c in stats["command_counts"]),
            inline=False,
        )
        embed.add_field(
            name="個人別実行回数",
            value="\n".join(f"<@{u['user_id']}>: {u['count']}回" for u in stats["user_counts"]),
            inline=False,
        )
        embed.add_field(
            name="出た結果の累計回数",
            value=_format_result_counts(stats["result_counts"]),
            inline=False,
        )
        return embed


# コマンド別に「結果: 回数」を整形する（Embed のフィールド用）
def _format_result_counts(result_counts: list[ResultCount]) -> str:
    lines: list[str] = []
    current_command: str | None = None
    for row in result_counts:
        if row["command"] != current_command:
            current_command = row["command"]
            lines.append(f"**{current_command}**")
        lines.append(f"　{row['result']}: {row['count']}回")
    return "\n".join(lines)
