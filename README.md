# Ryo-Discord-Bot
ローカルサーバ用のDiscord Botです。

## 機能一覧

### スラッシュコマンド
| コマンド | 使い方 |
|---|---|
| `/omikuji [1~3の整数]` | 引数で渡した回数おみくじを引きます |
| `/neo_omikuji` | 説明付きのおみくじを引きます |

### その他の機能
| 機能 | 説明 |
|---|---|
| リアクションロール付与 | 特定のメッセージへのリアクション時に、指定したロールを付与します |
| メンション返答 | ボットがメンションされた際にランダムな返答を送信します |
| Minecraft UUID 検知 | 他のボットが送信するアカウント連携メッセージから Minecraft UUID を抽出し、指定チャンネルに ja.namemc.com の検索 URL を投稿します |

## Dockerコンテナで実行
1. BOTのトークンを取得 ※以下BOT作成手順参照
2. `git clone https://github.com/ryo-icy/ryo-discord-bot`
3. `.env` ファイルを作成し、環境変数を設定

    ```env
    DISCORD_TOKEN=取得したトークン
    DEFAULT_ROLE_ID=付与するロールのID
    TARGET_MESSAGE_ID=リアクション対象のメッセージID
    NAMEMC_CHANNEL_ID=NameMC URLを投稿するチャンネルのID
    ```

    `.env.example` をコピーして使うと便利です：
    ```bash
    cp .env.example .env
    ```

4. `docker compose up -d`

> [!NOTE]
> 開発時は`docker-compose.yaml`のimageをコメントアウトし、buildをアンコメントする

## BOT作成手順
1. [Developer portal](https://discord.com/developers/applications/)からApplicationを作成
    1. 右上の"New Application"をクリック
    
        ![](./doc/img/step1.png)

    2. 表示されたモーダルウィンドウにDiscord Bot名を入力し、チェックボックスにチェックをつけて"Create"をクリック

        ![](./doc/img/step2.png)
    
    3. 左メニューから"Installation"をクリックし、以下を設定
        | 設定項目 | 設定値 |
        |---|---|
        | Installation Contexts | □User Install / ■Guild Install |
        | Install Link | None |
    
    4. 左メニューから"Bot"をクリックし、以下を設定
        | 設定項目 | 設定値 |
        |---|---|
        | PUBLIC BOT | OFF |
        | Presence Intent | ON |
        | Server Members Intent | ON |
        | Message Content Intent | ON |
    
    5. "Token"の"Reset Token"をクリックし、トークンを取得する

    6. 左メニューから"OAuth2"をクリックし、以下の順番で招待用リンクを発行
        1. "OAuth2 URL Generator"の"Scope"から"bot"を選択
        2. "OAuth2 URL Generator"の"Bot Permissions"から"View Channels"と"Send Messages"を選択
        3. "OAuth2 URL Generator"の"Generated URL"をコピー
2. BOT招待用のリンクにアクセスし、参加させたいサーバを選択