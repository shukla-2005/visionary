# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.10-slim AS builder

WORKDIR /app

# System build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a prefix so we can copy them cleanly
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.10-slim AS runtime

WORKDIR /app

# Runtime system libraries only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Create required directories
RUN mkdir -p saved_models reports data

# Create non-root user and fix ownership
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

USER appuser

# Expose both service ports
EXPOSE 8000 8501

# Default: FastAPI (overridden per-service in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
