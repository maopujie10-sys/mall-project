FROM python:3.11-slim

LABEL maintainer="Friday AI OS"

WORKDIR /app

# 第1步：先COPY源码，在pip install之前就清理BOM
COPY . .

# 彻底清理所有Python文件的UTF-8 BOM（在pip安装前）
RUN python3 << 'PYEOF'
import os, glob
count = 0
for f in glob.glob('/app/**/*.py', recursive=True):
    try:
        with open(f, 'rb') as fh:
            data = fh.read()
        if data[:3] == b'\xef\xbb\xbf':
            with open(f, 'wb') as fh:
                fh.write(data[3:])
            count += 1
    except:
        pass
print(f'BOM cleaned: {count} files')
PYEOF

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    nginx \
    curl \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright + Chromium（可选，失败不阻断）
RUN pip install --no-cache-dir playwright && \
    python -m playwright install chromium 2>/dev/null || echo "playwright chromium install skipped"

# 创建必要目录和非root用户
RUN mkdir -p /app/data/screenshots /app/memory /app/state /app/backups /app/logs && \
    useradd -m -s /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser
EXPOSE 9000
ENV TZ=Asia/Shanghai

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:9000/agent/health/simple || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--workers", "2"]