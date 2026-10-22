# syntax=docker/dockerfile:1
# -----------------------------------------------------------------------------
# AgentOps Production Containerfile
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install curl and ca-certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast, reliable dependency installation
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Copy dependency specifications first for caching
COPY pyproject.toml uv.lock README.md /app/

# Install dependencies into virtual environment
RUN uv sync --frozen --no-dev --no-install-project

# Copy project files
COPY src /app/src
COPY alembic /app/alembic
COPY alembic.ini /app/

# Install the application
RUN uv sync --frozen --no-dev

# -----------------------------------------------------------------------------
# Runner Stage
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runner

WORKDIR /app

# Create unprivileged runtime user
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

# Copy virtual environment and application code from builder
COPY --from=builder --chown=appuser:appuser /app /app

# Ensure application environment is on PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    HOST=0.0.0.0 \
    PORT=8000

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/v1/health')" || exit 1

ENTRYPOINT ["python", "-m", "agent_ops"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
