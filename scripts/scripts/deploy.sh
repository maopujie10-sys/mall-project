#!/bin/bash
# ============================================
# TikTokMall AI Agent — 一键部署脚本 V2
# 完整部署 + 数据库初始化 + 健康检查
# ============================================
set -e

ENV="${1:-production}"
PROJECT_DIR="/opt/claude-agent-control"
BACKUP_DIR="$PROJECT_DIR/backups"
LOG_DIR="$PROJECT_DIR/logs"
KEYS_DIR="$PROJECT_DIR/keys"

echo "============================================"
echo "  TikTokMall AI Agent 部署脚本 V2"
echo "  环境: $ENV"
echo "============================================"

# 1. 检查环境
echo "[1/7] 检查环境..."
command -v docker >/dev/null 2>&1 || { echo "❌ 需要安装 Docker"; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "❌ 需要安装 Docker Compose"; exit 1; }
command -v mysql >/dev/null 2>&1 && echo "   ✅ mysql-client 已安装" || echo "   ⚠️ mysql-client 未安装，数据库备份功能受限"

# 2. 创建目录结构
echo "[2/7] 创建目录结构..."
mkdir -p "$PROJECT_DIR" "$BACKUP_DIR" "$LOG_DIR" "$KEYS_DIR"

# 3. 配置 .env
echo "[3/7] 配置环境变量..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    [ -f .env.example ] && cp .env.example "$PROJECT_DIR/.env" || touch "$PROJECT_DIR/.env"
    echo "   ⚠️  请编辑 $PROJECT_DIR/.env 填入配置"
    echo "    必填:"
    echo "    - X_AGENT_TOKEN（安全Token）"
    echo "    - MALL_BASE_URL（商城地址）"
    echo "    可选:"
    echo "    - CLAUDE_API_KEY（AI文案/作图/视频）"
    echo "    - MALL_DB_*（数据库备份/查询）"
    echo "    - TELEGRAM_*（告警通知）"
    echo ""
    read -p "  按回车键继续..." </dev/tty
    if command -v nano &>/dev/null; then
        nano "$PROJECT_DIR/.env"
    else
        vi "$PROJECT_DIR/.env"
    fi
else
    echo "   ✅ .env 已存在"
fi

# 4. 构建 Docker 镜像
echo "[4/7] 构建 Docker 镜像..."
docker compose -f "$PROJECT_DIR/docker-compose.yml" build --no-cache

# 5. 启动服务
echo "[5/7] 启动服务..."
export APP_ENV="$ENV"
docker compose -f "$PROJECT_DIR/docker-compose.yml" up -d

# 6. 初始化 Agent 数据库
echo "[6/7] 初始化 Agent 数据库..."
DB_HOST=$(grep DB_HOST "$PROJECT_DIR/.env" | cut -d= -f2)
DB_USER=$(grep DB_USER "$PROJECT_DIR/.env" | cut -d= -f2)
DB_PASSWORD=$(grep DB_PASSWORD "$PROJECT_DIR/.env" | cut -d= -f2)
DB_NAME=$(grep DB_NAME "$PROJECT_DIR/.env" | cut -d= -f2 || echo "ai_agent")

if [ -n "$DB_HOST" ] && [ -n "$DB_USER" ] && [ "$DB_HOST" != "127.0.0.1" ]; then
    echo "   ⏳ 创建数据库表..."
    docker exec -i mall-agent mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < backend/migrations/init.sql 2>/dev/null && \
    echo "   ✅ 数据库初始化完成" || echo "   ⚠️ 数据库初始化跳过（请手动导入 migrations/init.sql）"
fi

# 7. 健康检查
echo "[7/7] 健康检查..."
echo "   ⏳ 等待服务启动..."
sleep 5

# 检查 agent
if curl -sf http://localhost:9000/agent/health >/dev/null 2>&1; then
    echo "   ✅ Agent API: http://localhost:9000 (健康)"
else
    echo "   ❌ Agent API: 启动失败，请查看日志: docker compose logs agent"
fi

# 检查前端
if curl -sf http://localhost:5173 >/dev/null 2>&1; then
    echo "   ✅ 前端: http://localhost:5173 (健康)"
else
    echo "   ⚠️ 前端: 尚未就绪，等待构建完成"
fi

echo ""
echo "============================================"
echo "  ✅ 部署完成"
echo "============================================"
echo "  访问地址:"
echo "  API:      http://localhost:9000"
echo "  文档:     http://localhost:9000/docs"
echo "  前端:     http://localhost:5173"
echo "  急救面板: http://localhost:5173/emergency"
echo ""
echo "  管理命令:"
echo "  日志:     docker compose logs -f agent"
echo "  重启:     docker compose restart agent"
echo "  停止:     docker compose down"
echo "  更新:     docker compose pull && docker compose up -d"
echo ""
echo "  首次部署后请:"
echo "  1. 编辑 .env 填入正确配置"
echo "  2. 重启服务: docker compose restart agent"
echo "============================================"
