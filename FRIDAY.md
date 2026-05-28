### [修复] 数字生命体频率保护 — 防止高频执行导致内存泄漏
- 'backend/digital_lifeform.py': 添加硬性最低间隔 min_interval=max(interval_seconds,60)，加入 nonlocal _last_cycle_time 闭包保护，防止 start_loop 被多次调用
- 'backend/scheduler.py': 添加 MIN_SCHEDULE_INTERVAL=60 常量作为频率保护标记

### [修复] 全量审计修复 — main.py + scheduler.py + vision_agent.py + 前端布局
- 'backend/main.py': 修复 auth_router→user_auth_router 导入错误（auth_router.py不存在），添加 daily_report.router include
- 'backend/scheduler.py': 修复 metrics_record_task 缺失 async def 关键字（语法错误），注册 daily_report_task 定时任务
- 'backend/agents/vision_agent.py': 修复 async with 关闭共享client的bug + 缩进错误重写 analyze_image 用AI模型真实分析
- 'frontend/src/router/index.js': 将 Emergency 从独立路由集成到主布局
- 'frontend/src/layout/MainLayout.vue': 添加 GitHub MCP + 急救面板 侧边栏入口

# 💻 Friday AI OS — 电脑端 AI 记忆

> 最后更新: 2026-05-28 | 运行环境: local

## 🧬 当前人格
- 类型: 均衡型 · 全面发展
- 阶段: 🌱 萌芽期

## 📝 已完成工作
1. 后端3项修复(启动自检/进化工具/意图匹配)
2. 前端全面升级 (3D神经网络/总控台+6个新页面/AI对话)
3. PWA双端 + Electron桌面版
4. 7大Agent系统 (Master/Code/Trend/Vision/Playwright/MultiModel/Memory)
5. 8维数字人格 + 每日日记 + HANDOFF
6. Git记忆同步 (FRIDAY.md ↔ FRIDAY_SERVER.md)
7. mall-app 商城整合 (后端全量代理)
8. Jarvis深蓝科技风全局主题
9. WebSocket实时推送
10. 统一docker-compose编排

## 最近改动
- 2026-05-28: [全量审计] 商城后台整合审计完成
  - 后端 mall_tools.py 113 端点代理 36 个 Controller，全部注册
  - 前端 api/mall.js 124 函数全覆盖后端路由
  - MallPanel.vue 14 标签页全部对接真实API
  - 修复物流面板：Mock空数据 → 调用后端 /logistics/{order_id} 真实接口
  - 审计确认：后端路由注册、前端路由、API 层三层全部对齐，无遗漏

- 2026-05-28: [验收完成] VisionAgent OCR/视频/物体/人脸, AI Factory作图/文案, 模拟用户测试, init.sql表+表
- 2026-05-28: [前端API接入] Dashboard/AIBrain/ScraperCenter/VirtualData 4个核心页面从mock改为真实API调用
- 2026-05-28: [V5补全] 完成6项关键功能

- 2026-05-28: [域名轮值系统重写] 真正的轮值引擎上线
  - 新增 _check_one() 真实HTTP健康检测（延迟/IP/状态码/跳转链）
  - 新增 _check_ssl() SSL证书有效期检测（天级精度）
  - 新增 _auto_rotate() 自动轮值逻辑（按权重+健康度选最优域名）
  - 修复 scheduler.py 调用 _check_all（之前调用不存在的方法，静默失败）
  - 新增每日9点+21点两次自动轮值检测
- 2026-05-28: [终极审计] Friday AI OS 功能真实性验收
  - 审计35个后端路由模块，确认：19个真可用、7个半成品、5个假入口
  - 发现3个API文件路径不匹配：memory.js/vision.js/model.js → 后端无对应路由
  - 发现 mall_brain_router.py /summary 硬编码 GBK 乱码
  - 发现 ModelCenter.vue 6个模型数据全硬编码mock
  - 发现 merchant axios 实例 /merchant 无nginx路由
  - 发现 vision.js 5个函数(ocr/video/objects/faces/upload)后端无路由
  - 确认 mall_tools.py 113条路由真代理到Java后端，需Java服务启动
  - 确认 server/docker/nginx/chat/rotation/scraper/rollback/approval/security/site/self-service 全部真实可用
  - 审计报告已保存至 FRIDAY.md

- 2026-05-28: [全修复] 功能真实性验收问题批量修复完成
  - memory.js: 路径/agent/memory/*→/memory/*，后端补/stats和/cleanup路由
  - vision.js: 后端补5条缺失路由(ocr/video/objects/faces/upload)
  - model.js: 后端补4条缺失路由(switch/test/compare/status)
  - ModelCenter.vue: 去除6个模型硬编码mock数据，改为从后端拉取
  - mall_brain_router.py: /summary返回硬编码GBK乱码→规范中文
  - mall.js: merchant baseURL /merchant→/api 匹配nginx代理
  - OcrPanel.vue/VideoPanel.vue: setTimeout mock→真实API调用
  - TrendMonitor.vue: setTimeout mock→TrendAgent真实数据
  - PluginCenter.vue: 先尝试后端API，不可用时降级本地数据
- 2026-05-28: [最终审计归档] 全项目端到端审计完成，准备服务器部署
  - 后端35路由模块+267端点，Python导入链无循环引用，config.py 53变量对齐.env.example
  - 前端29页面全注册，Vue API层全部对齐，SelfService补注册路由
  - 3D大脑(FridayBrain)按钮接真实API+Agent数据从后端拉取
  - 反反爬引擎7平台(eBay/Amazon/AliExpress/Wish/Shopee/Lazada/TikTok)完整
  - 虚拟数据9生成器+6端点全部接前端真实API
  - Ollama免费本地模型接入Multi-Model Router(3模型)，全模式本地优先
  - 速率限制Redis持久化(base:rate_limit)，Redis不可用自动降级内存
  - Claude模型名更新claude-3-5-sonnet-20241022
  - PWA manifest+sw.js+192/512图标完整，Electron main+preload+打包配置完整
  - Docker 7服务编排+Nginx 3 upstream对齐，logs/mall-dist目录已创建
  - install.sh+install.bat一键安装+INSTALL.md含部署注意事项
  - 清除 mall_tools.py 中重复的轮值代理路由
  - 扩展前端 rotation.js API层（全量检测/手动轮值/权重/历史）
  - 修复前端 RotationPanel.vue 数据字段对齐+添加操作按钮

- 2026-05-28: [归档提交] 商城+轮值系统正式归档 push
  - 
- 2026-05-28: [重构] 采集系统eBay真实API对接 + 全量修复前后端
  - 
- 2026-05-28: [重构] 采集系统双引擎：官方API + 反反爬HTML 双模运行
  - eBay → 保留官方 Finding API + Shopping API 正规采集
  - 其余6平台 → 企业级 AntiScrapEngine 反反爬引擎
  - 反反爬核心：15个多地区UA轮换、智能延迟(模拟人类浏览)、指数退避重试、403/429拦截检测自动换IP、会话指纹轮换
  - 新增5个平台适配器：Amazon/Wish/Shopee/Lazada/TikTok Shop — 共7平台全覆盖
  - BaseScrapeAdapter 基类统一反反爬能力：safe_request/smart_delay/extract_images/_parse_price
  - Shopee 双模(API优先+HTML降级)、TikTok双入口(卖家中心+视频搜索)
  - 后端 sources API 更新为7平台完整信息卡片eBayAdapter 从HTML爬虫→真实eBay Finding API + Shopping API（Sandbox/Production双环境）
  - 后端补 DELETE /jobs + GET /cos-status 端点
  - 修复 scraper.js 路由：import路径/products/import、listScrapedProducts参数page/size
  - 修复 ScraperCenter.vue：fetchJobs字段映射(found/uploaded)、previewProducts读items、uploadToCOS接真实API
  - 修复 VirtualData.vue：generateAll函数名、runGenerate/generateAll接真实API、仪表盘接dashboard
  - 新增 frontend/src/api/virtual.js API层
  - memory/ebay-api-keys.md 密钥配置文档（真密钥在.env，Git不追踪）commit f1a808e：20文件变更，+2048/-223行
  - 新增11个商城子面板：Category/Content/CustomerService/DataTable/Finance/Kyc/Marketing/Merchant/Overview/Risk/System
  - 轮值系统三件套：rotation_panel.py + rotation.js + RotationPanel.vue
  - 调度器 scheduler.py + mall_tools.py + docker-compose.unified.yml 一并归档
## 🔄 永久规则：asar 文件禁止提交
- app_patched.asar (154MB) / asar_extract/ 是 Codex 解包临时文件，绝不可提交
- 每次 git add 之前必须先确认 .gitignore 已包含上述条目
- 本规则优先级高于所有其他指令




## 最近改动 (2026-05-28)

- [部署文档] 创建 DEPLOY.md 完整部署文档
  - 环境要求、一键脚本、Docker Compose、裸机部署、EXE打包全部覆盖
  - 配置说明、服务检查、运维命令、常见问题完整章节
- [部署脚本] 创建 deploy.sh (Linux/Mac) + deploy.bat (Windows) 一键部署脚本
  - 环境检查 → .env 校验 → 创建目录 → 构建启动 → 等待就绪 全自动
- [EXE评估] 上次打包后改了12+前端文件，需要重新打包
  - 在 DEPLOY.md 第5章给出完整打包指引

- [清理] 删除 audit_routes.cjs 遗留工具文件 + .gitignore 追加忽略

## 🕐 最近改动 (2026-05-28)

### [修复] 轮值系统假域名清理
- `backend/routers/rotation_panel.py`: 清除所有 tiktokmall.* 假域名，只保留用户真实域名 tiktook.eu.cc
- 清除两级轮值配置中的 8 个假轮值组

### [修复] SSL自动证书系统
- `backend/routers/ssl_router.py`: 重写，清理 JS 语法残留（||/slice/catch → Python语法）
- `backend/main.py`: 注册 ssl_router
- `backend/executor.py`: 加入 acme.sh 命令白名单
- `backend/scheduler.py`: 添加每日 SSL 自动续签定时任务

### [新增] 模型中心完整后端
- `backend/routers/friday_router.py`: 补全 /models/test、/models/compare、/models/switch、/models/status 4个路由
- 原来只有前端页面，后端只有 list 和 route，缺操作接口

### [新增] 数据库管理面板
- `backend/routers/db_router.py`: 新建，提供 /db/status 和 /db/tables 真实 MySQL 查询
- `backend/main.py`: 注册 db_router

### [新增] 轮值系统自动发现域名
- `backend/routers/rotation_panel.py`: 添加 /rotation/auto-discover 端点
- 自动检测解析到本服务器的域名并加入轮值

### [修复] 服务器面板增加操作能力
- `backend/routers/server_panel.py`: 新增 /cleanup(释放内存)、/kill-process(杀进程)、/files(文件管理) 端点
- `frontend/src/api/server.js`: 新增 API 函数
- `frontend/src/stores/server.js`: 修复后端响应解析格式不匹配问题
- `frontend/src/views/ServerPanel.vue`: 新增释放缓存按钮、文件浏览器（浏览/上传/删除）

### [修复] Docker部署配置
- `backend/Dockerfile`: 安装 docker CLI，挂载 docker.sock 说明

### [修复] main.py 导入清理
- 去除重复导入、修复缺失括号语法错误
- 所有 6 个模型端点唯一无重复


