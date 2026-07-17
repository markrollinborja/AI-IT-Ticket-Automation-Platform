# --- Build stage: install dependencies into an isolated virtual environment ---
FROM python:3.13-slim AS builder

WORKDIR /code

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Runtime stage: copy only the built environment and app code, nothing else ---
FROM python:3.13-slim

WORKDIR /code

# Copy the pre-built virtual environment instead of reinstalling here -
# keeps pip's build cache and installer metadata out of the final image.
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Run as a non-root user. If the app is ever compromised, this limits
# what an attacker inside the container can actually do - no write access
# outside what's explicitly needed, can't install packages, etc. Running
# containers as root is a common, easily avoidable finding in a security
# review.
RUN useradd --create-home --shell /bin/bash appuser

COPY --chown=appuser:appuser app ./app

USER appuser

EXPOSE 8000

# Lets `docker ps` / container orchestrators see whether the app is
# actually responding, not just whether the process exists. Deliberately
# hits /health (liveness), not /health/ready - a container healthcheck
# shouldn't restart the container just because the database is
# temporarily unreachable; that's what the readiness endpoint is for.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
