@echo off
chcp 65001 >nul
REM ============================================================
REM Friday AI OS + TikTokMall 一键安装脚本 (Windows)
REM 用法: 双击运行 或 install.bat
REM ============================================================

echo ============================================
echo   Friday AI OS + TikTokMall 一键安装
echo ============================================

REM 1. 检查依赖
echo.
echo [1/5] 检查系统依赖...
where docker >nul 2>&1 || (echo [错误] 请先安装 Docker Desktop && pause && exit /b 1)
where python >nul 2>&1 || (echo [警告] Python 未安装, 部分功能不可用)
where node >nul 2>&1 || (echo [警告] Node.js 未安装, 前端需手动处理)
echo   依赖检查完成

REM 2. 配置环境变量
echo.
echo [2/5] 配置环境变量...
if not exist ".env" (
    copy .env.example .env >nul
    echo   已从 .env.example 创建 .env, 请编辑填入实际密钥!
    echo   关键配置: AGENT_TOKEN, EBAY_SANDBOX_APP_ID, MYSQL_ROOT_PASSWORD
) else (
    echo   环境变量就绪
)

REM 3. 安装 Python 依赖
echo.
echo [3/5] 安装 Python 依赖...
cd backend
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)
pip install -r requirements.txt -q 2>nul || echo   pip install 失败, 请手动执行
cd ..
echo   Python 依赖安装完成

REM 4. 安装前端依赖
echo.
echo [4/5] 安装前端依赖...
where node >nul 2>&1
if %errorlevel%==0 (
    cd frontend
    call npm install --silent 2>nul || echo   npm install 失败, 请手动执行
    cd ..
    echo   前端依赖安装完成
) else (
    echo   跳过 (Node.js 未安装)
)

REM 5. 创建目录
echo.
echo [5/5] 创建必要目录...
if not exist "memory" mkdir memory
if not exist "logs" mkdir logs
if not exist "data" mkdir data
echo   目录就绪

echo.
echo ============================================
echo   安装完成!
echo.
echo   启动方式:
echo   1) Docker 一键: docker-compose -f docker-compose.unified.yml up -d
echo   2) 本地开发: 打开两个终端分别运行:
echo      cd backend ^&^& python main.py
echo      cd frontend ^&^& npm run dev
echo.
echo   AI控制台: http://localhost:9000/agent
echo   API文档:  http://localhost:9000/docs
echo ============================================
pause