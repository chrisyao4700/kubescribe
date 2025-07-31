# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates tzdata   && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir .

COPY app ./app

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
