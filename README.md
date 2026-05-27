# TikTokMall AI Agent 总控系统

## 🏗 项目结构

```
mall-project/
├── backend/              # AI Agent 后台 (Python FastAPI :9000)
│   ├── routers/          # 30+ API路由模块
│   ├── tools/            # 核心引擎：采集/虚拟数据/AI大脑/进化
│   ├── main.py           # 入口，启动自检+记忆预热
│   └── startup.py        # 启动自检模块
├── frontend/             # AI 控制台前端 (Vue3 + Element Plus)
│   └── src/views/        # 总控台/AI大脑/进化报告/采集中心/虚拟数据
├── mall-source/          # 🔗 整合的商城源码 (Java Spring + Vue)
│   ├── 源码/后端/         # Java Spring MVC 商城API
│   └── 源码/前端/         # Vue 商城前端 (PC/H5/商家/招商)
├── docker-compose.unified.yml  # 🚀 统一编排：AI + 商城 + MySQL + Redis + Nginx
├── nginx.conf            # 统一入口 Nginx 配置
├── backups/              # 备份目录
└── logs/                 # 日志目录
```

## 🚀 一键启动

```bash
docker-compose -f docker-compose.unified.yml up -d
```

启动后：
- AI 控制台: `http://服务器IP/ai/`
- 商城前台: `http://服务器IP/`
- AI API: `http://服务器IP/ai/api/`
- 商城 API: `http://服务器IP/api/`

## 🧠 AI 能力

| 引擎 | 说明 |
|------|------|
| 🛒 超级采集 | eBay/AliExpress/Amazon/1688 → COS |
| 👥 虚拟数据 | 一键生成真实感数据，4档规模 |
| 🧠 AI大脑 | 扫描健康度/品类缺口/自动运维 |
| 🧬 自我进化 | 长期记忆/成功率/纠正学习/进化报告 |
| ☁️ 云存储 | 腾讯云COS，自动上传 |
| 🔄 启动自检 | 启动即检查记忆/成功率/待学习纠正 |

## 🔗 商城整合

- 商城源码位于 `mall-source/`，原样保留
- 数据库同MySQL实例，AI可直接管理商城数据
- AI通过 `mall_tools`/`autopilot_mall` 等模块运维商城
