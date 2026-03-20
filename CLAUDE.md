# CLAUDE.md

このファイルは、リポジトリで作業する際に Claude Code (claude.ai/code) へのガイダンスを提供します。

## 言語設定

- 会話は常に日本語で行う
- コード内のコメントは日本語で記述する
- エラーメッセージの説明は日本語で行う
- ドキュメントは日本語で生成する

## ボットの起動方法

**開発時（ローカルビルドあり）：**
`docker-compose.yaml` の `build: ./app` をコメントイン、`image: ghcr.io/...` をコメントアウトしてから実行：
```bash
docker compose up -d
```

**本番環境：**
```bash
docker compose up -d
```

**Docker を使わない場合：**
```bash
pip3 install discord.py
python3 app/script/main.py
```

## 環境変数

`docker-compose.yaml` の `environment:` に設定する：

| 変数名 | 説明 |
|---|---|
| `DISCORD_TOKEN` | Discord Developer Portal で取得したボットの認証トークン |
| `DEFAULT_ROLE_ID` | 対象メッセージにリアクションしたユーザーへ付与するロールの ID（整数） |
| `TARGET_MESSAGE_ID` | リアクションロール付与のトリガーとなるメッセージの ID（整数） |

## アーキテクチャ

`app/script/main.py` の単一ファイルで構成された Discord.py ボット。Cogs/Extensions は使用しておらず、すべてのロジックが 1 ファイルにまとまっている。

**機能一覧：**
1. **`/omikuji [1~3]`** — `config/omikuji.txt` からランダムに N 回おみくじを引く
2. **`/neo_omikuji`** — `config/neo_omikuji.txt` から詳細なおみくじを引く（フォーマット: `運勢, 説明`）
3. **リアクションロール** — `on_raw_reaction_add` で `TARGET_MESSAGE_ID` へのリアクション時に `DEFAULT_ROLE_ID` を付与する
4. **メンション返答** — `on_message` でボットがメンションされた際に `config/mention.txt` からランダムな一文を送信する

**設定ファイル**（`app/script/config/`）は改行区切りのプレーンテキスト。起動時に `load_config()` で一度だけ読み込まれる。

## CI/CD

`main` ブランチへのプッシュで `.github/workflows/docker.yml` が起動し、Docker イメージをビルドして `ghcr.io/ryo-icy/ryo-discord-bot:latest` へプッシュする。

## 新機能の追加

フラットな構造のため、スラッシュコマンドは `@tree.command()` で、イベントハンドラは `@client.event` で追加する。設定ファイル駆動のレスポンスは `load_config()` でテキストファイルを読み込み `random.choice()` でサンプリングするパターンに従う。
