FROM python:3.10-slim

WORKDIR /root/dozi-api

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install

COPY entrypoint.sh ./
COPY ./backend ./backend
