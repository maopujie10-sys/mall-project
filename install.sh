#!/bin/bash
# ============================================================
# Friday AI OS + TikTokMall 一键安装脚本 (Linux/macOS)
# 用法: chmod +x install.sh && ./install.sh
# ============================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "============================================"
echo -e "  Friday AI OS + TikTokMall 一键安装"
echo -e "============================================"

# 1. 检查依赖
echo -e "\n[1/6] 检查系统依赖..."
command -v docker >/dev/null 2>&1 || { echo -e "请先安装 Docker: https://docs.docker.com/engine/install/"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "请先安装 docker-compose"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo -e "请先安装 Python 3.10+"; exit 1; }
command -v node >/dev/null 2>&1 || { echo -e "Node.js 未安装(可选, 如需前端开发)"; }
echo -e "  依赖检查通过"

# 2. 配置环境变量
echo -e "\n[2/6] 配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "  已从 .env.example 创建 .env, 请编辑填入实际密钥"
    echo -e "  关键配置: AGENT_TOKEN, EBAY_SANDBOX_APP_ID, MYSQL_ROOT_PASSWORD"
fi
echo -e "  环境变量就绪"

# 3. 安装 Python 依赖
echo -e "\n[3/6] 安装 Python 依赖..."
cd backend
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate 2>/dev/null || true
pip install -r requirements.txt -q
cd ..
echo -e "  Python 依赖安装完成"

# 4. 安装前端依赖 (可选)
echo -e "\n[4/6] 安装前端依赖..."
if command -v node >/dev/null 2>&1; then
    cd frontend
    npm install --silent 2>/dev/null || echo -e "  npm install 失败(非致命), 请手动执行"
    cd ..
    echo -e "  前端依赖安装完成"
else
    echo -e "  跳过 (Node.js 未安装)"
fi

# 5. 创建必要目录
echo -e "\n[5/6] 创建必要目录..."
mkdir -p memory logs data
echo -e "  目录就绪"

# 6. 启动服务
echo -e "\n[6/6] 启动服务..."
echo -e "  请选择启动方式:"
echo -e "  1) Docker 一键启动 (推荐): docker-compose -f docker-compose.unified.yml up -d"
echo -e "  2) 本地开发模式:"
echo -e "     cd backend && python main.py"
echo -e "     cd frontend && npm run dev"
echo -e "  3) 仅启动基础设施:"
echo -e "     docker-compose -f docker-compose.unified.yml up -d mysql redis"

echo -e "\n============================================"
echo -e "  安装完成!"
echo -e "  AI控制台: http://localhost:9000/agent"
echo -e "  商城前端: http://localhost"
echo -e "  API文档:  http://localhost:9000/docs"
echo -e "============================================"