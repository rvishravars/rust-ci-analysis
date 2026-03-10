# Simple container for the Rust CI data collector
FROM python:3.11-slim

# Avoid buffering and ensure UTF-8
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system deps if needed later (kept minimal for now)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy only requirements first, for better Docker layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY collector ./collector
COPY metrics.md ./metrics.md

# Default data directory inside the container
ENV RUST_CI_DATA_DIR=/data

# The collector reads configuration from environment variables (e.g., GITHUB_TOKEN)
# and writes raw data under /data by default.

ENTRYPOINT ["python", "-m", "collector"]
