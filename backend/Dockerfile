# Python 3.11のスリム版をベースイメージに設定
FROM python:3.11-slim

# 環境変数の設定
ENV PYTHONPATH /usr/src/app

# 必要なパッケージをインストール
RUN apt-get update && \
    apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    default-mysql-client \
    procps \
    rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /usr/src/app

# 依存関係のインストール（変更が少ないためキャッシュを活用）
COPY requirements.txt /usr/src/app/
RUN python -m venv /app/.venv && \
    . /app/.venv/bin/activate && \
    pip install --no-cache-dir --timeout=1000 --retries=5 -r requirements.txt


# アプリケーションのコードをコピー
COPY . /usr/src/app

# ポート8000を公開
EXPOSE 8000