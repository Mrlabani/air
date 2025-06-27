FROM python:3.10-slim

RUN apt update && apt install -y curl aria2 && \
    pip install --no-cache-dir pyrogram tgcrypto aria2p pymongo

COPY . /app
WORKDIR /app

CMD ["bash", "aria.sh"]
