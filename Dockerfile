FROM python:3.12-slim

LABEL org.opencontainers.image.source=https://github.com/ryo-icy/ryo-discord-bot

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    TZ=Asia/Tokyo

# uv（スタティックバイナリ）
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /usr/local/bin/uv

WORKDIR /app

# 依存関係を先にインストール（レイヤーキャッシュ活用）
COPY pyproject.toml uv.lock ./
COPY src ./src
RUN uv sync --frozen --no-dev

ENV PATH="/opt/venv/bin:${PATH}"

# 非 root ユーザーで実行（おみくじ記録用の data ディレクトリを事前に作成し所有権を渡す）
RUN useradd -m -u 1001 bot && mkdir -p /app/data && chown bot:bot /app/data
USER bot

CMD ["python", "-m", "ryo_discord_bot"]
