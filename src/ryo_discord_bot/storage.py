import sqlite3
import threading
from pathlib import Path
from typing import TypedDict


# おみくじの実行結果を記録・集計する SQLite ストア
class CommandCount(TypedDict):
    command: str
    count: int


class ResultCount(TypedDict):
    command: str
    result: str
    count: int


class RecentDraw(TypedDict):
    command: str
    result: str
    created_at: str


class UserCount(TypedDict):
    user_id: int
    count: int


class PersonalStats(TypedDict):
    command_counts: list[CommandCount]
    result_counts: list[ResultCount]
    recent_draws: list[RecentDraw]


class GlobalStats(TypedDict):
    command_counts: list[CommandCount]
    user_counts: list[UserCount]
    result_counts: list[ResultCount]


class OmikujiStore:
    def __init__(self, db_path: str) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        # asyncio.to_thread で呼び出されるため複数スレッドから同一接続を共有する。
        # sqlite3 は接続の共有時、書き込み操作の直列化を呼び出し側に要求するため
        # threading.Lock で全操作を直列化する。
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS omikuji_draws (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id   INTEGER,
                    user_id    INTEGER NOT NULL,
                    command    TEXT    NOT NULL,
                    result     TEXT    NOT NULL,
                    created_at TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
                )
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_draws_guild ON omikuji_draws(guild_id)"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_draws_user ON omikuji_draws(guild_id, user_id)"
            )
            self._conn.commit()

    # おみくじの実行結果を記録する（1コマンド実行で複数件になる場合がある）
    def record(self, guild_id: int | None, user_id: int, command: str, results: list[str]) -> None:
        with self._lock:
            self._conn.executemany(
                "INSERT INTO omikuji_draws (guild_id, user_id, command, result) "
                "VALUES (?, ?, ?, ?)",
                [(guild_id, user_id, command, result) for result in results],
            )
            self._conn.commit()

    # 個人の統計（コマンド別実行回数・結果内訳・直近10件）を取得する
    def personal_stats(self, guild_id: int | None, user_id: int) -> PersonalStats:
        with self._lock:
            guild_clause = "guild_id IS ?" if guild_id is None else "guild_id = ?"

            command_counts = self._conn.execute(
                f"SELECT command, COUNT(*) AS count FROM omikuji_draws "
                f"WHERE {guild_clause} AND user_id = ? "
                f"GROUP BY command ORDER BY command",
                (guild_id, user_id),
            ).fetchall()

            result_counts = self._conn.execute(
                f"SELECT command, result, COUNT(*) AS count FROM omikuji_draws "
                f"WHERE {guild_clause} AND user_id = ? "
                f"GROUP BY command, result ORDER BY command, count DESC",
                (guild_id, user_id),
            ).fetchall()

            recent_draws = self._conn.execute(
                f"SELECT command, result, created_at FROM omikuji_draws "
                f"WHERE {guild_clause} AND user_id = ? "
                f"ORDER BY id DESC LIMIT 10",
                (guild_id, user_id),
            ).fetchall()

            return {
                "command_counts": [{"command": row[0], "count": row[1]} for row in command_counts],
                "result_counts": [
                    {"command": row[0], "result": row[1], "count": row[2]} for row in result_counts
                ],
                "recent_draws": [
                    {"command": row[0], "result": row[1], "created_at": row[2]}
                    for row in recent_draws
                ],
            }

    # サーバ全体の統計（コマンド別総回数・個人別実行回数・結果累計回数）を取得する
    def global_stats(self, guild_id: int | None) -> GlobalStats:
        with self._lock:
            guild_clause = "guild_id IS ?" if guild_id is None else "guild_id = ?"

            command_counts = self._conn.execute(
                f"SELECT command, COUNT(*) AS count FROM omikuji_draws "
                f"WHERE {guild_clause} "
                f"GROUP BY command ORDER BY command",
                (guild_id,),
            ).fetchall()

            user_counts = self._conn.execute(
                f"SELECT user_id, COUNT(*) AS count FROM omikuji_draws "
                f"WHERE {guild_clause} "
                f"GROUP BY user_id ORDER BY count DESC LIMIT 10",
                (guild_id,),
            ).fetchall()

            result_counts = self._conn.execute(
                f"SELECT command, result, COUNT(*) AS count FROM omikuji_draws "
                f"WHERE {guild_clause} "
                f"GROUP BY command, result ORDER BY command, count DESC",
                (guild_id,),
            ).fetchall()

            return {
                "command_counts": [{"command": row[0], "count": row[1]} for row in command_counts],
                "user_counts": [{"user_id": row[0], "count": row[1]} for row in user_counts],
                "result_counts": [
                    {"command": row[0], "result": row[1], "count": row[2]} for row in result_counts
                ],
            }

    def close(self) -> None:
        with self._lock:
            self._conn.close()
