@echo off
chcp 65001 >nul
title Friday AI OS 一键部署
echo ============================================
echo   Friday AI OS 一键部署脚本 (Windows)
echo ============================================

echo.
echo [1/6] 检查运行环境...

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 未找到 Docker。请先安装 Docker Desktop
    pause
    exit /b 1
)
echo Docker: 已安装

docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo 未找到 Docker Compose
    pause
    exit /b 1
)
echo Docker Compose: 已安装

echo.
echo [2/6] 检查环境配置...

if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo 已从 .env.example 创建 .env 文件
        echo 请编辑 .env 填写必填变量后再运行
        pause
        exit /b 1
    ) else (
        echo 未找到 .env.example
        pause
        exit /b 1
    )
)

findstr "X_AGENT_TOKEN=change-me-in-production" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo .env 中 X_AGENT_TOKEN 仍是默认值
    pause
    exit /b 1
)
echo .env 文件存在

echo.
echo [3/6] 创建持久化目录...
mkdir backups 2>nul
mkdir logs 2>nul
mkdir data\screenshots 2>nul
mkdir memory 2>nul
mkdir state 2>nul
echo 目录创建完成

echo.
echo [4/6] 构建并启动所有服务...
docker compose -f docker-compose.unified.yml up -d --build
if %errorlevel% neq 0 (
    echo 启动失败，请查看日志
    pause
    exit /b 1
)
echo 服务已启动

echo.
echo [5/6] 等待服务就绪...

:wait_nginx
timeout /t 3 >nul
curl -s http://localhost/health >nul 2>&1
if %errorlevel% neq 0 goto wait_nginx
echo Nginx 就绪

:wait_agent
timeout /t 3 >nul
curl -s http://localhost:9000/health >nul 2>&1
if %errorlevel% neq 0 goto wait_agent
echo AI Agent 就绪

echo.
echo ============================================
echo   部署完成！
echo ============================================
echo.
docker compose -f docker-compose.unified.yml ps
echo.
echo   前端控制台: http://localhost/ai/
echo   后端 API:    http://localhost:9000
echo.
echo   查看日志: docker compose logs -f
echo   停止服务: docker compose down
echo.
pause
