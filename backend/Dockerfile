FROM python:3.11-slim

LABEL maintainer="Friday AI OS"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    nginx \
    curl \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright + Chromium (browser automation)
RUN pip install --no-cache-dir playwright && \
    python -m playwright install chromium 2>/dev/null || echo "playwright chromium install skipped"

# Copy app code
COPY . .

# Create required directories
RUN mkdir -p /app/data/screenshots /app/memory /app/state /app/backups /app/logs

# Docker socket: mount via volumes: - /var/run/docker.sock:/var/run/docker.sock
EXPOSE 9000
ENV TZ=Asia/Shanghai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9000/agent/health')" || exit 1

# Clean BOM from Python files
RUN find /app -name "*.py" -exec sed -i "1s/^\\xEF\\xBB\\xBF//" {} \;

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--workers", "2"]
