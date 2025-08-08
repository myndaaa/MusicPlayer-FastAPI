FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi


COPY . .
COPY docker/start.sh /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["bash", "/app/start.sh"] 
