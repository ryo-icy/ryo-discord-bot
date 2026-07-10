from pathlib import Path

# モジュール位置基準で解決するため、実行時のカレントディレクトリに依存しない
CONFIG_DIR = Path(__file__).parent / "config"


# コンフィグファイルの読み込み（空行はスキップ）
def load_config(filename: str) -> list[str]:
    with open(CONFIG_DIR / filename, encoding="utf-8") as f:
        return [line for line in f.read().splitlines() if line.strip()]
