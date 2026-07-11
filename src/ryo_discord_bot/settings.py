import os
from collections.abc import Callable
from dataclasses import dataclass


def _get_env[T](key: str, cast: Callable[[str], T]) -> T:
    value = os.getenv(key)
    if value is None:
        raise OSError(f"環境変数 '{key}' が設定されていません。")
    try:
        return cast(value)
    except ValueError as e:
        raise OSError(
            f"環境変数 '{key}' の値 '{value}' が不正です（{cast.__name__} 型が必要）。"
        ) from e


# ボットの設定値（すべて環境変数から読み込む）
@dataclass(frozen=True)
class Settings:
    discord_token: str
    default_role_id: int
    target_message_id: int
    namemc_channel_id: int
    omikuji_db_path: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            discord_token=_get_env("DISCORD_TOKEN", str),
            default_role_id=_get_env("DEFAULT_ROLE_ID", int),
            target_message_id=_get_env("TARGET_MESSAGE_ID", int),
            namemc_channel_id=_get_env("NAMEMC_CHANNEL_ID", int),
            omikuji_db_path=os.getenv("OMIKUJI_DB_PATH", "data/omikuji.db"),
        )
