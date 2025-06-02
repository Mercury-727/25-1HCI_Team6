FROM python:3.10-slim

WORKDIR /root/dozi-api

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install

COPY ./app ./app

CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "app", "api:app"]
