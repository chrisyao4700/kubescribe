# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

# Install build deps for psycopg binary if needed (usually none), and tzdata
RUN apt-get update && apt-get install -y --no-install-recommends     ca-certificates tzdata   && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app

# Copy project metadata first (for layer caching)
COPY pyproject.toml README.md ./
# Install deps (no dev tools here)
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir .

# Copy source
COPY src/ ./src/

# Default command
ENTRYPOINT ["python", "-m", "kubescribe_core_runner.main"]
