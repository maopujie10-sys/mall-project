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
$1## 🔄 永久规则：asar 文件禁止提交
- app_patched.asar (154MB) / asar_extract/ 是 Codex 解包临时文件，绝不可提交
- 每次 git add 之前必须先确认 .gitignore 已包含上述条目
- 本规则优先级高于所有其他指令

