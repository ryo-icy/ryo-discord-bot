# AGENTS.md

このファイルは、リポジトリで作業する際に Claude Code (claude.ai/code) へのガイダンスを提供します。

## 言語設定

- 会話は常に日本語で行う
- コード内のコメントは日本語で記述する
- エラーメッセージの説明は日本語で行う
- ドキュメントは日本語で生成する

## 開発環境

[mise](https://mise.jdx.dev/) で Python 3.12 と uv を管理している（`mise.toml`）。

```bash
mise install    # ツールのインストール
uv sync         # 依存関係のインストール（.venv）
```

## ボットの起動方法

**ローカル開発：**
```bash
uv run python -m ryo_discord_bot   # .env の環境変数を読み込んでおくこと
```

**Docker（本番は ghcr イメージ、開発時は `compose.yaml` の build をコメントイン）：**
```bash
docker compose up -d
```

## リント・フォーマット

```bash
uv run ruff check .     # リント
uv run ruff format .    # フォーマット
```

## 環境変数

`.env` ファイルに設定する（`.env.example` をコピーして使用）。読み込みと検証は `src/ryo_discord_bot/settings.py` の `Settings.from_env()` が行う。

| 変数名 | 説明 |
|---|---|
| `DISCORD_TOKEN` | Discord Developer Portal で取得したボットの認証トークン |
| `DEFAULT_ROLE_ID` | 対象メッセージにリアクションしたユーザーへ付与するロールの ID（整数） |
| `TARGET_MESSAGE_ID` | リアクションロール付与のトリガーとなるメッセージの ID（整数） |
| `NAMEMC_CHANNEL_ID` | Minecraft UUID 検知時に NameMC URL を投稿するチャンネルの ID（整数） |

## アーキテクチャ

discord.py ボット。src レイアウトで、機能ごとに Cog に分割している。

```
src/ryo_discord_bot/
├── __main__.py        # エントリポイント。Bot クラス定義・Cog 登録・tree.sync（setup_hook で1回のみ）
├── settings.py        # 環境変数の読み込み・検証（frozen dataclass）
├── config_loader.py   # config/ 内テキストファイルの読み込み（モジュール位置基準の絶対パス解決）
├── cogs/
│   ├── omikuji.py         # /omikuji（Range[int, 1, 3]）と /neo_omikuji
│   ├── reaction_role.py   # TARGET_MESSAGE_ID へのリアクションで DEFAULT_ROLE_ID を付与
│   └── message_watch.py   # Minecraft UUID 検知（NameMC URL 投稿）とメンション返答
└── config/            # 改行区切りのプレーンテキスト（omikuji / neo_omikuji / mention）
```

**機能一覧：**
1. **`/omikuji [1~3]`** — `config/omikuji.txt` からランダムに N 回おみくじを引く
2. **`/neo_omikuji`** — `config/neo_omikuji.txt` から詳細なおみくじを引く（フォーマット: `運勢, 説明`）
3. **リアクションロール** — `on_raw_reaction_add` で `TARGET_MESSAGE_ID` へのリアクション時に `DEFAULT_ROLE_ID` を付与する
4. **メンション返答** — `on_message` でボットがメンションされた際に `config/mention.txt` からランダムな一文を送信する
5. **Minecraft UUID 検知** — `on_message` で `Minecraft UUID: <uuid>` パターンを検知し、`https://ja.namemc.com/search?q=<uuid>` を `NAMEMC_CHANNEL_ID` のチャンネルへ投稿する

設定ファイルは各 Cog の `__init__` で `load_config()` により一度だけ読み込まれる。

## CI/CD

`main` ブランチへのプッシュ（`src/**`・`Dockerfile`・`pyproject.toml`・`uv.lock` 変更時）で `.github/workflows/docker.yml` が起動し、Docker イメージをビルドして `ghcr.io/ryo-icy/ryo-discord-bot:latest` へプッシュする。認証は `GITHUB_TOKEN`（`permissions: packages: write`）。

> [!NOTE]
> GHCR パッケージ `ryo-discord-bot` の push には、パッケージ側の設定（ https://github.com/users/ryo-icy/packages/container/ryo-discord-bot/settings の「Manage Actions access」）でこのリポジトリに **Write** ロールが付与されている必要がある。以前 `CR_PAT`（個人 PAT）で push していたため未リンクだった際に `permission_denied: write_package` で失敗した。リポジトリの Settings > Actions > General > Workflow permissions を `Read and write` にするだけでは不十分で、パッケージ側の許可が別途必要。

## 新機能の追加

1. `src/ryo_discord_bot/cogs/` に `commands.Cog` のサブクラスを作成する
   - スラッシュコマンドは `@app_commands.command()`、イベントは `@commands.Cog.listener()` を使う
   - `__init__(self, bot, settings)` で `self.bot` / `self.settings` を保持し、`bot.user` 等は `self.bot` 経由で参照する
2. `__main__.py` の `setup_hook()` に `add_cog` を追加する
3. 設定ファイル駆動のレスポンスは `config/` にテキストを置き、`load_config()` + `random.choice()` のパターンに従う
