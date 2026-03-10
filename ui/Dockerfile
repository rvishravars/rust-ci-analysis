FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY ui/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ui ./ui

ENV RUST_CI_DB_DSN=postgresql://rustci:rustci@db:5432/rustci

WORKDIR /app/ui

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
