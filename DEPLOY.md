# Friday AI OS — 部署文档

> 版本：v2.0 | 更新：2026-05-28
>
> 一键启动 AI Agent 后台 + 商城系统 + Electron 桌面端

---

## 目录

1. [环境要求](#1-环境要求)
2. [快速部署（一键脚本）](#2-快速部署一键脚本)
3. [手动部署（Docker Compose）](#3-手动部署docker-compose)
4. [手动部署（裸机）](#4-手动部署裸机)
5. [Electron EXE 打包](#5-electron-exe-打包)
6. [配置说明](#6-配置说明)
7. [服务检查](#7-服务检查)
8. [运维命令](#8-运维命令)
9. [常见问题](#9-常见问题)

---

## 1. 环境要求

### 必需

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Docker | 24+ | 容器运行环境 |
| Docker Compose | v2.20+ | 多容器编排（`docker compose` 命令） |
| Git | 2.x | 拉取代码 |

### 可选

| 组件 | 用途 |
|------|------|
| Node.js 18+ | 裸机启动前端 / 打包 EXE |
| Python 3.10+ | 裸机启动后端 |
| Ollama | 本地 AI 模型（免费离线推理） |
| Playwright | 浏览器自动化截图 |

### 端口占用

| 端口 | 服务 | 说明 |
|------|------|------|
| 80 | Nginx | 统一入口，反向代理所有前端 |
| 9000 | AI Agent 后端 | FastAPI + WebSocket |
| 3306 | MySQL | 数据库 |
| 6379 | Redis | 缓存/队列 |
| 8080 | 商城 Java API | Spring Boot |
| 5173 | AI 前端 (dev) | Vite 开发服务器 |

---

## 2. 快速部署（一键脚本）

### 2.1 Linux / Mac

```bash
# 1. 克隆仓库
git clone https://github.com/maopujie10-sys/mall-project.git
cd mall-project

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，至少填写 X_AGENT_TOKEN 和一个 AI API Key

# 3. 一键部署
chmod +x deploy.sh
./deploy.sh
```

### 2.2 Windows

```powershell
# 1. 克隆仓库
git clone https://github.com/maopujie10-sys/mall-project.git
cd mall-project

# 2. 配置环境变量
copy .env.example .env
# 编辑 .env，至少填写 X_AGENT_TOKEN 和一个 AI API Key

# 3. 一键部署
.\deploy.bat
```

---

## 3. 手动部署（Docker Compose）

### 3.1 构建并启动

```bash
# 克隆并进入目录
git clone https://github.com/maopujie10-sys/mall-project.git
cd mall-project

# 配置环境
cp .env.example .env
# 编辑 .env，填入必要密钥

# 创建持久化目录
mkdir -p backups logs data/screenshots memory state

# 构建镜像并启动
docker compose -f docker-compose.unified.yml up -d --build
```

### 3.2 首次启动等待

启动后各服务需要 30–60 秒初始化：

```bash
# 检查所有容器状态
docker compose -f docker-compose.unified.yml ps

# 查看 AI 后端日志
docker logs mall-ai-agent --tail 50

# 查看 Nginx 日志
docker logs mall-nginx --tail 10
```

### 3.3 停止/重启

```bash
# 停止所有服务
docker compose -f docker-compose.unified.yml down

# 重启
docker compose -f docker-compose.unified.yml restart

# 查看实时日志
docker compose -f docker-compose.unified.yml logs -f
```

---

## 4. 手动部署（裸机）

> 裸机部署适合开发调试，**不推荐生产使用**。生产请用 Docker Compose。

### 4.1 后端（AI Agent）

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install playwright
playwright install chromium

# 启动
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

### 4.2 前端（AI 控制台）

```bash
cd frontend

# 安装依赖
npm install

# 开发模式启动
npm run dev
# 访问: http://localhost:5173

# 生产构建
npm run build
# 构建产物在 dist/
```

### 4.3 Nginx 配置（可选）

```bash
# 使用项目中的 nginx.conf
cp frontend/nginx.conf /etc/nginx/conf.d/friday-ai.conf
nginx -s reload
```

---

## 5. Electron EXE 打包

### 5.1 是否需要重新打包

**判断标准**：只要改过以下目录中的任何文件，就需要重新打包。

| 目录 | 文件类型 | 举例 |
|------|----------|------|
| `frontend/src/` | `.vue` `.js` `.css` | 页面、路由、API |
| `frontend/public/` | 静态资源 | favicon、图片 |
| `frontend/` | `package.json` `vue.config.js` | 依赖、配置 |

**当前状态**：上次打包后改了大量前端文件（见 FRIDAY.md），**需要重新打包**。

### 5.2 打包步骤

```bash
cd frontend

# 确保依赖完整
npm install

# 安装 Electron + 打包工具
npm install electron electron-builder --save-dev

# 构建前端
npm run build

# 打包为 Windows EXE
npx electron-builder --win --x64
```

### 5.3 打包产物

- 路径：`frontend/dist_electron/FridayAI-win32-x64/FridayAI.exe`
- 安装包：`frontend/dist_electron/FridayAI Setup x.x.x.exe`
- 如需分发给用户，建议打包为 Setup 安装包，用 `--win --x64` 参数

---

## 6. 配置说明

### 6.1 环境变量清单

复制 `.env.example` 为 `.env`，填写以下变量：

| 变量 | 必填 | 说明 |
|------|------|------|
| `X_AGENT_TOKEN` | **是** | Agent 认证 Token，生产环境必须改 |
| `CLAUDE_API_KEY` | 选一 | Anthropic Claude API Key |
| `DEEPSEEK_API_KEY` | 选一 | DeepSeek API Key（推荐，国内便宜） |
| `OPENAI_API_KEY` | 选一 | OpenAI API Key |
| `GITHUB_TOKEN` | 否 | GitHub MCP 功能需要 |
| `IMAGGA_API_KEY` | 否 | Vision/OCR 功能需要 |
| `MYSQL_ROOT_PASSWORD` | **是** | MySQL root 密码 |
| `JWT_SECRET` | 否 | 不填自动随机生成 |

### 6.2 API Key 推荐配置

- **国内用户**：DeepSeek API Key（价格低，速度快）
- **海外用户**：Claude API Key（能力最强）
- **免费用户**：Ollama 本地模型（`ollama pull qwen2.5:14b`）

### 6.3 持久化目录结构

```
project/
├── backups/        # 状态备份文件
├── logs/           # 日志文件
├── data/
│   └── screenshots/  # Playwright 截图
├── memory/         # AI 记忆文件
└── state/          # State 持久化
```

---

## 7. 服务检查

### 7.1 健康检查

```bash
# Nginx
curl http://localhost/health
# 期望: {"status":"ok","services":{"ai-agent":"healthy",...}}

# AI 后端 API
curl http://localhost:9000/health
# 期望: {"status":"ok"}

# 商城 API（Java）
curl http://localhost:8080/health
# 期望: {"status":"UP"}
```

### 7.2 功能检查

```bash
# AI 对话
curl -X POST http://localhost/ai/api/chat \
  -H "Content-Type: application/json" \
  -H "X-Agent-Token: your-token" \
  -d '{"message":"你好","stream":false}'

# 工具列表
curl http://localhost/ai/api/tools/list \
  -H "X-Agent-Token: your-token"

# 模型列表
curl http://localhost/ai/api/models \
  -H "X-Agent-Token: your-token"
```

---

## 8. 运维命令

### 8.1 日常运维

```bash
# 查看所有容器状态
docker ps -a

# 查看资源占用
docker stats --no-stream

# 实时日志（指定服务）
docker logs -f mall-ai-agent

# 进入容器
docker exec -it mall-ai-agent sh
```

### 8.2 备份与恢复

```bash
# 备份 state
docker exec mall-ai-agent sh -c "cp /app/data/state.json /app/backups/state_$(date +%Y%m%d_%H%M%S).json"

# 备份 MySQL
docker exec mall-mysql sh -c "mysqldump -u root -p mall_db > /backups/mall_$(date +%Y%m%d).sql"
```

### 8.3 清理

```bash
# 清理未使用镜像
docker image prune -a

# 清理日志（限制 100MB）
docker logs mall-ai-agent --tail 100 > /dev/null 2>&1

# 数据治理（自动清理 >7 天的截图和临时文件）
docker exec mall-ai-agent python -c "from tools.state import data_cleanup; data_cleanup()"
```

---

## 9. 常见问题

### AI 对话返回空 / 无响应

- 检查 `.env` 中 AI API Key 是否正确
- 检查 `docker logs mall-ai-agent` 有无错误
- 确认网络能访问 AI API 端点

### 商城面板 404

- 确认 `mall-api` 容器正常运行：`docker ps | grep mall-api`
- 检查 Nginx 日志：`docker logs mall-nginx`

### Docker 面板无数据

- 确认挂载了 docker.sock：`docker exec mall-ai-agent ls -la /var/run/docker.sock`
- Windows Docker Desktop 需在 Settings → Resources 开启文件共享

### Playwright 不可用

- 确认安装了浏览器：`docker exec mall-ai-agent playwright install chromium 2>&1`
- 检查 Dockerfile 中是否包含 `playwright install-deps`

### WebSocket 频繁断开

- 检查防火墙是否阻止了 9000 端口
- 查看客户端 Network 面板有无 4xx/5xx 错误
- 确认 `X-Agent-Token` 与 `.env` 中一致

### Token 认证失败

- 确认请求头 `X-Agent-Token` 设置正确
- 检查 `.env` 中 `X_AGENT_TOKEN` 的值

---