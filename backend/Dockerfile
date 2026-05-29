FROM python:3.11-slim
LABEL maintainer="Friday AI OS"
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    nginx \
    mariadb-client-compat \
    docker.io \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright + Chromium（用于浏览器自动化）
RUN pip install --no-cache-dir playwright && \
    python -m playwright install chromium 2>/dev/null || echo "playwright chromium 安装跳过"

# 复制代码
COPY . .

# 创建持久化目录
RUN mkdir -p /app/data/screenshots /app/memory /app/state /app/backups /app/logs

# Docker管理需挂载宿主docker.sock: volumes: - /var/run/docker.sock:/var/run/docker.sock
EXPOSE 9000
ENV TZ=Asia/Shanghai

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9000/agent/health')" || exit 1

# 清除 BOM
RUN find /app -name "*.py" -exec sed -i "1s/^\xEF\xBB\xBF//" {} \;
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--workers", "2"]
