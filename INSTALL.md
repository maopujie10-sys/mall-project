# Friday AI OS + TikTokMall 安装教程

> 最后更新: 2026-05-28 | 版本: v4.0

---

## 📋 系统要求

| 组件 | 最低版本 | 说明 |
|------|---------|------|
| Docker | 24.0+ | 容器化运行 |
| Docker Compose | v2 | 多服务编排 |
| Python | 3.10+ | AI Agent 后端 |
| Node.js | 18+ | 前端开发(可选) |
| 内存 | 8GB+ | ChromaDB + MySQL 较吃内存 |
| 磁盘 | 20GB+ | 含镜像和依赖 |

---

## 🚀 快速开始 (Docker 一键)

### 1. 克隆项目
\\\ash
git clone https://github.com/maopujie10-sys/mall-project.git
cd mall-project
\\\

### 2. 配置密钥
\\\ash
cp .env.example .env
# 编辑 .env 填入必要配置:
#   AGENT_TOKEN=你的Agent密钥
#   EBAY_SANDBOX_APP_ID=你的eBay沙盒AppID
#   EBAY_SANDBOX_CERT_ID=你的eBay沙盒CertID
#   MYSQL_ROOT_PASSWORD=你的MySQL密码
\\\

### 3. 一键启动
\\\ash
# Linux/macOS
chmod +x install.sh && ./install.sh
docker-compose -f docker-compose.unified.yml up -d

# Windows
install.bat
docker-compose -f docker-compose.unified.yml up -d
\\\

### 4. 访问
| 服务 | 地址 |
|------|------|
| AI 控制台 | http://localhost:9000/agent |
| API 文档 | http://localhost:9000/docs |
| 商城前台 | http://localhost |
| 商城后台 | http://localhost:8080 |

---

## 🛠️ 手动安装 (开发模式)

### 后端
\\\ash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py  # 启动在 :9000
\\\

### 前端
\\\ash
cd frontend
npm install
npm run dev  # 启动在 :5173
\\\

### 基础设施
\\\ash
docker-compose -f docker-compose.unified.yml up -d mysql redis
\\\

---

## 🔑 关键配置说明

### .env 必填项
\\\env
# AI Agent 认证
AGENT_TOKEN=your-secret-token-here

# 数据库
MYSQL_ROOT_PASSWORD=your-password
DB_HOST=localhost
DB_NAME=ai_agent

# eBay API (采集系统)
EBAY_SANDBOX_APP_ID=your-sandbox-app-id
EBAY_SANDBOX_CERT_ID=your-sandbox-cert-id
EBAY_PRODUCTION_APP_ID=your-prod-app-id  # 可选
EBAY_PRODUCTION_CERT_ID=your-prod-cert-id  # 可选
EBAY_DEV_ID=your-dev-id

# 商城API
MALL_BASE_URL=http://localhost:8080
\\\

### eBay API 获取
1. 注册 [eBay Developers Program](https://developer.ebay.com)
2. 创建应用获取 Sandbox 密钥(免费)
3. 配置到 .env 即可使用采集系统

---

## 📦 项目结构
\\\
mall-project/
├── backend/           # AI Agent 后端 (FastAPI)
│   ├── agents/        # 7大Agent (Master/Code/Trend/Vision/Playwright/MultiModel/Memory)
│   ├── routers/       # 35+ 路由模块
│   ├── tools/         # 采集引擎/虚拟数据/记忆同步/向量检索
│   └── main.py        # 主入口 (:9000)
├── frontend/          # AI 控制台前端 (Vue3 + Element Plus)
│   ├── src/views/     # 30+ 功能页面
│   ├── electron/      # Electron 桌面版
│   └── public/        # PWA 离线支持
├── mall-app/          # 商城后端 (Spring Boot)
├── memory/            # AI 记忆归档
├── docker-compose.unified.yml  # 统一编排
├── nginx.conf         # 统一入口
├── install.sh         # Linux 安装脚本
├── install.bat        # Windows 安装脚本
└── INSTALL.md         # 本文件
\\\

---

## 🔧 故障排查

### Docker 启动失败
\\\ash
# 检查日志
docker-compose -f docker-compose.unified.yml logs -f

# 重建
docker-compose -f docker-compose.unified.yml down -v
docker-compose -f docker-compose.unified.yml up -d --build
\\\

### 数据库连接失败
- 确认 MySQL 容器已启动: docker ps | grep mysql
- 确认 .env 中密码与 docker-compose 一致
- 首次启动需等待 MySQL 初始化(约30秒)

### 前端白屏
- 确认后端已启动: curl http://localhost:9000/agent/health
- 检查浏览器控制台网络请求

### 采集系统无数据
- 确认 eBay API 密钥已配置到 .env
- eBay Sandbox 返回的是测试数据，生产需切换 Production 密钥
- 其他平台(Amazon/Wish等)走反反爬HTML采集，需要稳定的网络环境

---

## 📝 开发文档
- FRIDAY.md — 电脑端 AI 工作状态
- FRIDAY_SERVER.md — 服务器端 AI 工作状态
- memory/HANDOFF_COMPLETE.md — 完整交接文档
- memory/ebay-api-keys.md — eBay API 配置说明

---


---

## ⚠️ 部署前必读

### 商城前端构建
docker-compose 需要已构建的商城前端文件：
\\\ash
cd mall-app/frontend/pc && npm install && npm run build
cd mall-app/frontend/h5 && npm install && npm run build
\\\
构建产物会输出到 mall-frontend-pc/dist/ 和 mall-frontend-h5/dist/。

### 免费 AI (可选)
安装 Ollama 本地模型，API 费用永久为零：
\\\ash
# 安装 Ollama → https://ollama.com
ollama pull qwen2.5:7b
ollama pull deepseek-r1:7b
\\\
路由器自动检测 Ollama 在线状态，在线则优先使用免费模型。

### .env 必填项
\\\ash
cp .env.example .env
# 必须修改以下项：
#   AGENT_TOKEN          — AI Agent 认证令牌
#   MYSQL_ROOT_PASSWORD  — 数据库密码
#   EBAY_SANDBOX_APP_ID  — eBay 采集密钥(可选)
#   EBAY_SANDBOX_CERT_ID — eBay 采集密钥(可选)
\\\

### 首次启动顺序
\\\ash
# 1. 先启动数据库(等待30秒初始化)
docker-compose -f docker-compose.unified.yml up -d mysql redis

# 2. 再启动全部服务
docker-compose -f docker-compose.unified.yml up -d

# 3. 查看日志确认无报错
docker-compose -f docker-compose.unified.yml logs -f ai-agent
\\\

### Electron 桌面版
\\\ash
cd frontend
npm install
npm run electron:build  # 打包 .exe (Windows) / .dmg (macOS)
\\\
输出在 rontend/release/ 目录。

### PWA 移动端
手机浏览器访问 http://你的IP/ai/ → 添加到桌面 → 独立运行。

### 已知限制
- eBay Sandbox 返回测试数据，生产环境需切换 Production 密钥
- Ollama 7B 模型回复速度约 5-20 秒(纯CPU)，有 GPU 可秒出
- 采集系统除 eBay 外均为 HTML 爬虫，目标网站改版需更新 CSS 选择器
- 速率限制默认内存模式，重启丢失计数(有 Redis 则自动切换持久化)

---

*Friday AI OS v4.0 · 超级AI数字生命体*