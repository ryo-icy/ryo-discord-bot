FROM ubuntu:24.04

LABEL org.opencontainers.image.source https://github.com/ryo-icy/ryo-discord-bot

# ユーザー作成
ARG UID=1001 \
    GID=1001
RUN groupadd -g $GID docker && \
    useradd -m -s /bin/bash -u $UID -g $GID docker

# システムパッケージを一括インストール
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        tzdata \
        language-pack-ja && \
    update-locale LANG=ja_JP.UTF-8 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV TZ="Asia/Tokyo" \
    LANG="ja_JP.UTF-8" \
    LANGUAGE="ja_JP:ja" \
    LC_ALL="ja_JP.UTF-8"

# pipenv のインストール
RUN pip3 install --break-system-packages pipenv

# 依存関係を先にインストール（キャッシュ活用）
RUN mkdir /script && chown docker /script
COPY --chown=docker script/requirements.txt /script/requirements.txt

USER $UID
WORKDIR /script
RUN python3 -m pipenv install -r requirements.txt

# スクリプト本体をコピー
USER root
COPY --chown=docker script/ /script

USER $UID

CMD python3 -m pipenv run python3 main.py
