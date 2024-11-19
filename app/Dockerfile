FROM ubuntu:24.04

# Creat a user
ARG UID=1001 \
    GID=1001
RUN groupadd -g $GID docker && \
    useradd -m -s /bin/bash -u $UID -g $GID docker

RUN apt update -y && apt upgrade -y && \
    apt install -y python3 python3-pip

RUN apt-get install -y tzdata && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV TZ Asia/Tokyo

RUN apt update -y && apt-get install -y language-pack-ja && \
    update-locale LANG=ja_JP.UTF-8 && rm -rf /var/lib/apt/lists/*
ENV LANG="ja_JP.UTF-8" \
    LANGUAGE="ja_JP:ja" \
    LC_ALL="ja_JP.UTF-8"

RUN mkdir /script
COPY script/ /script
RUN chown docker /script

USER $UID

WORKDIR /script

RUN pip3 install --break-system-packages pipenv
RUN python3 -m pipenv install -r requirements.txt

CMD python3 -m pipenv run python3 main.py