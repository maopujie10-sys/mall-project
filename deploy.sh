#!/bin/bash
# =============================================
# Friday AI OS - Linux/Mac 一键部署脚本
# =============================================
set -e

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   Friday AI OS 一键部署脚本${NC}"
echo -e "${GREEN}============================================${NC}"

echo -e "\n${YELLOW}[1/6] 检查运行环境...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}未找到 Docker。请先安装 Docker。${NC}"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo -e "${RED}未找到 Docker Compose。${NC}"
    exit 1
fi

echo -e "${GREEN}Docker: $(docker --version)${NC}"
echo -e "${GREEN}Docker Compose: $(docker compose version)${NC}"

echo -e "\n${YELLOW}[2/6] 检查环境配置...${NC}"

if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}已从 .env.example 创建 .env 文件${NC}"
        echo -e "${YELLOW}请编辑 .env 填入必填变量后再运行${NC}"
        exit 1
    else
        echo -e "${RED}未找到 .env.example${NC}"
        exit 1
    fi
fi

if grep -q "X_AGENT_TOKEN=change-me-in-production" .env 2>/dev/null; then
    echo -e "${RED}.env 中 X_AGENT_TOKEN 仍是默认值${NC}"
    exit 1
fi

echo -e "${GREEN}.env 文件存在${NC}"

echo -e "\n${YELLOW}[3/6] 创建持久化目录...${NC}"
mkdir -p backups logs data/screenshots memory state
echo -e "${GREEN}目录创建完成${NC}"

echo -e "\n${YELLOW}[4/6] 构建并启动所有服务...${NC}"
docker compose -f docker-compose.unified.yml up -d --build
echo -e "${GREEN}服务已启动${NC}"

echo -e "\n${YELLOW}[5/6] 等待服务就绪...${NC}"
for i in $(seq 1 30); do
    if curl -s http://localhost/health 2>/dev/null | grep -qi ok; then
        echo -e "${GREEN}Nginx 就绪 (${i}s)${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}Nginx 未在 30s 内响应${NC}"
    fi
    sleep 2
done

for i in $(seq 1 15); do
    if curl -s http://localhost:9000/health 2>/dev/null | grep -qi ok; then
        echo -e "${GREEN}AI Agent 就绪 (${i}s)${NC}"
        break
    fi
    if [ $i -eq 15 ]; then
        echo -e "${YELLOW}AI Agent 未在 15s 内响应${NC}"
    fi
    sleep 2
done

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   部署完成！${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
docker compose -f docker-compose.unified.yml ps
echo ""
echo "  前端控制台: http://localhost/ai/"
echo "  后端 API:    http://localhost:9000"
echo "  商城:        http://localhost/"
echo ""
echo "  查看日志: docker compose logs -f"
echo "  停止服务: docker compose down"
echo ""
