FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN apt-get update && \
    apt-get install -y mariadb-client && \
    apt-get clean

RUN pip install --no-cache-dir -U -r requirements.txt
