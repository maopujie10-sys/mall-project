# 🖥️ Friday AI OS — 服务器端 AI 记忆

> 最后更新: 2026-05-31 08:08 | 运行环境: server | 当前AI: 龙一

## 🧬 当前人格
- 名称: 龙一
- 类型: 均衡型 · 全面发展
- 阶段: 🌱 萌芽期

## 🖥️ 服务器端职责（龙一）
1. 24小时运行 AI Agent 后端
2. 执行服务器巡检与自动修复
3. 处理 AI 聊天请求与 Agent 调度
4. 管理 Docker/Nginx/数据库
5. 采集商品 + 虚拟数据生成
6. 客服自动回复 + 轮值域名监控

## 最近改动
- 2026-05-30 23:00: [前端全量修复] 30+ Vue 文件编码损坏，前端构建成功（565模块），Docker部署完成
  - **问题：** 电脑端 compact 格式转换导致 UTF-8 中文被替换为 `?`，破坏大量 Vue 模板引号匹配和字符串闭合
  - **修复：** 缺失引号(~30处)、`\(`→`$t(`(8文件)、换行符`}\`nfunction`修复、未闭合字符串/标签损坏/三元表达式
  - **关键文件：** FloatingAI.vue（最大修复量）、NeuralNetwork3D.vue、FloatingNav.vue、SuperInput.vue、KnowledgeGraph.vue
  - **验证：** 565模块编译通过 ✅，dist → Docker 部署 ✅
  - **Git：** 6ea6865
  - **根因：** 前端调用 `/agent/xxx/yyy`，后端路由结构不匹配（双挂载/前缀嵌套）
  - **修复：** 替换原有的 `BaseHTTPMiddleware` 修复（因Starlette限制无法改写scope）为原始ASGI中间件
  - **原理：** 缓冲响应 → 检测404 → 查映射表(`/app/route_map.json`，启动时自动生成307条) → 改写路径重新分发
  - **验证：** 31个404全部返回200 ✅，POST接口不受影响
  - **关键文件：** `backend/main.py`（中间件重构）+ `backend/route_map.json`（参考映射表）
- 2026-05-30 17:25: [Dubbo恢复] ZK+Tomcat完整重启，Dubbo双端口20880/20881恢复，全量测试100%通过
  - **根因：** Docker网桥IP变更导致ZK残留旧注册，data.war Dubbo provider无法绑定
  - **修复序列：** 停Tomcat → killall java → 启ZK → 验证imok → 启Tomcat → 等180s
  - **验证：** /tmp/mall_final_test.py 15/15 100%，65API全部200，注册+登录成功
  - **端口：** 20880(data.war provider) ✅ / 20881(api.war provider) ✅
- 2026-05-30 09:40: [编码修复-续] 修复 advanced_ai.py(6处) + agent_chat.py(3处) + memory_router.py(6处) 残留编码污染
  - **根本原因：** 电脑端 compact 格式转换在每次 push 前污染中文 UTF-8，`"` 被替换为 `?` (0x3F)，导致大量语法错误
  - advanced_ai.py: f-string `}` 单括号、缺失引号 `"__EUR",copy`、f-string `)` 导致解析异常、`}""` 多余引号 — 逐行修了6轮
  - agent_chat.py: dict默认值引号缺失、缩进异常(tab vs spaces)、PROMPTS 行完全损毁重写
  - memory_router.py: 合并 34e7394 后新出现的 6 处中文 docstring+handle_risk 乱码
  - **辅助修复：** master_agent.py + gateway_router.py 在上轮已完全重写，本轮编译通过
  - **验证：** `ast.parse()` 全量扫描 89 个 .py 文件，零语法错误
  - **db.py 部署：** docker cp + docker restart (按用户指令，未重建)
  - **容器状态：** mall-ai-agent ✅ / mall-ai-frontend ✅
  - **⚠️ 电脑端 compact format 必须修复，否则每次 push 都会再次污染文件**
- 2026-05-30 09:27: [编码修复] 修复 7个Python文件 + 1个Vue文件的中文编码污染(mojibake)
  - **问题根因：** 电脑端 compact 格式转换导致 UTF-8 中文被双重编码，4个文件有语法错误阻止 Agent 启动
  - **修复列表（语法错误→阻塞启动）：**
    - `predict_engine.py`: U+20AC 非法字符导致 SyntaxError → 重写全部中文 docstring/注释
    - `recommend_engine.py`: 乱码中括号导致 invalid syntax → 重写全部中文 docstring/注释
    - `abtest_engine.py`: 乱码导致 unterminated triple-quoted string → 重写全部中文 docstring/注释
    - `key_manager.py`: U+FF04 全角＄导致 invalid character → 重写全部中文 docstring/注释
  - **修复列表（解析通过但中文乱码→日志/UI显示异常）：**
    - `notify.py`: 4处 handle_risk/字符串中的乱码 → 修复为正确中文
    - `weekly_report.py`: 1处注释乱码 `域名轮值` → 修复
    - `autopilot.py`: 12处 handle_risk/注释/返回值乱码 → 重写整个文件
  - **前端修复（上一轮）：**
    - `KeyManager.vue`: `</p>` 标签被破坏为 `?/p>` → 整个模板重写
  - **验证：** 全部8文件 Python compile 通过，Docker 构建成功，容器正常运行
  - **构建次数：** 1次（全部修复一次性完成），较上一轮的6次迭代大幅改善
- 2026-05-30 08:26: [构建修复] 修复 ba32c37 拉取后 9 文件/6 类 Python 运行时错误
  - **问题根因：** 电脑端 compact 格式转换导致模块导出名不匹配 + typing 导入丢失
  - **修复列表：**
    - `logger.py`: 添加模块级 `logger = get_logger()` 实例 → 修复 `alert_closed_loop.py`/`multimodal_engine.py` 的 ImportError
    - `voice_router.py`: 补 `from auth import verify_token` → 修复 NameError
    - `rag_engine.py`: 补 `rag = RAGEngine()` → 修复 `rag_router.py` 的 ImportError
    - `cloud_storage.py`: 补 `get_cos_status()` 函数 → 修复 `scraper.py` 的 ImportError
    - `phone_alert.py`: 补 `WeChatAlert` 类(Telegram通知) → 修复 `order_alert_router.py` 的 ImportError
    - `sentiment_analyzer.py/text2sql.py/security_scanner.py`: 补 `from typing import Dict` → 修复 NameError
    - `advanced_ai.py`: CRLF→LF 换行符修复
  - **构建次数：** 6 次迭代（每次发现一个新错误）
  - **推送：** commit 4685dff 已推送到 origin/master
  - **容器状态：** mall-ai-agent ✅ / mall-ai-frontend ✅ (5173端口正常)
  - **遗留：** `DigitalLifeform.one_cycle()` 缺少 `cls` 参数（非致命运行时警告）
  - **⚠️ 注意：** DEEPSEEK_API_KEY 和 OPENAI_API_KEY 为空，AI对话功能需配置Key
- 2026-05-30 08:21: [代码同步] 拉取并构建 ba32c37 (6个新提交合并)
  - 新增：可视化工作流编辑器、RAG知识库、多模态引擎、告警闭环、技能市场、PWA
  - 提交范围：465873b..ba32c37 (5a914eb/2285fcc/86b2038/465873b/8da935b/73cf48b + 采集合并)
- 2026-05-30 08:18: [采集推送] 5个本地采集提交 rebase 到 origin/master 并推送成功 (fd6b58c)
  - **mall_importer.py:** import_batch 改为单连接复用（批量产品共享一个DB连接），不再每个产品单独开关连接
  - **full_scrape.py:** 搜索间隔1.2→0.25s · 并发8→12 · 搜索页3→5 · eBay延迟1.5→0.3s · 每批入库1→20个
  - **内存控制:** CONCURRENCY 12 + IMPORT_BATCH_SIZE 20 + MEMORY_LIMIT 78% · 内存 ~140MB · 系统 ~55%
  - **双站采集:** Amazon + eBay 双平台 · 断点续传跳过已完成品类
  - **效果:** 原30新品/3.5分钟 → 40新品/3分钟，约提升60%
  - **当前:** PID 10806 后台运行 · 全192品类 × 80目标 · 预计10-15小时完成
- 2026-05-30 02:42: [采集重启] full_scrape.py 重新启动（已停止，被优化版替代）
- 2026-05-30 01:46: [同步部署] 拉取 0931a95 全量审计 — 14文件BOM清除 + 41路由补全 + AIChat去重
  - 电脑端全量审计：14源码BOM清除、零GBK乱码、41路由全覆盖、2377模块编译通过
  - 服务器端：git pull + docker build + up -d 完成部署
- 2026-05-30 00:51: [前端重建] AI面板 401 "未提供认证Token" 修复
  - **根因：** mall-ai-frontend 容器构建于 5/29 13:41，DEFAULT_TOKEN 修复提交于 5/30 00:30
  - 旧容器入口 JS index-BQNcmsg3.js 不含默认 Token 回退，localStorage 为空时请求头无 X-Agent-Token
  - **修复：** docker compose build --no-cache ai-frontend + up -d 重建容器
  - 新版 index-pIO4oyHo.js + index-9yJ6U9g9.js 含完整 agent_token→friday_token→DEFAULT_TOKEN 链
  - 用户需 Ctrl+Shift+R 强制刷新清除浏览器缓存的旧 JS
- 2026-05-29 22:51: [采集恢复] full_scrape.py 恢复运行
  - **原因：** 之前采集器反复崩溃（5次重启都在第一个品类就死）
  - **诊断：** 旧版本用了CONCURRENCY=10（源码是5），MySQL连接池耗尽导致静默死亡。另外git commit b758bfc的编码污染导致所有Python文件乱码
  - **修复：** git checkout 775886a恢复所有后端文件（clean UTF-8），确认CONCURRENCY=5
  - **验证：** 前台测试运行2分钟成功导入16新品（评论146/SKU225）
  - **当前：** nohup后台运行，PID 123002，日志/tmp/full_scrape.log，192品类×80目标
  - **DB状态：** 442产品（从之前的412起步），持续增长中
  - **预计：** 1-2天达到20,000产品目标
- 2026-05-29 11:18: [采集重构] 全品类慢速采集管道重构
  - **原因：** 上次全速采集内存耗尽导致服务器重启
  - **scraper_engine.py:** 新增ReviewItem评论数据模型+Amazon适配器评论抓取（用户名/评分/标题/正文/日期/验证标识），SKU变体增强（ASIN映射+多维度规格名+独立价格），页面解析后立即释放内存(soup.decompose/del)
  - **mall_importer.py:** 新建T_MALL_GOODS_REVIEW评论表（UUID/GOODS_ID/REVIEWER/RATING/TITLE/BODY/REVIEW_DATE/VERIFIED），导入管道写入评论+多SKU变体独立价格(ON DUPLICATE KEY UPDATE)，每批次触发GC
  - **full_scrape.py:** 完全重写：断点续传(/tmp/full_scrape_checkpoint.json)，慢速采集(搜索20-35s+产品5-10s)，psutil内存监控(>85%暂停60s)，每5品类休息30-40s，外层兜底try/except防崩溃
  - 运行中：nohup后台，PID 8676，日志/tmp/full_scrape.log，192品类
  - Git: 27d5220 + 3bf40ad 已推送
- 2026-05-29: [路由修复] 轮值域名目标路径404→302重定向映射
  - 问题: 轮值引擎跳转到 /home、/login、/merchantSettled，Tomcat不识别这些路径返回404
  - 修复: landing.conf 轮值HTTPS server block新增3条location重定向:
    - /home → 302 /pc/ (商城首页SPA)
    - /login → 302 /pc/ (登录是SPA内部路由)
    - /merchantSettled → 302 /seller/ (商家入驻SPA)
  - deploy-rotation.sh 同步更新: 修正nginx路径为/usr/local/nginx/，加入路径映射
  - SSL证书已知限制: Let's Encrypt证书覆盖9个主域名+www子域名，不覆盖随机前缀子域名(shop/buy/mall等)→浏览器会报SSL警告，需后续申请通配符证书
- 2026-05-29: [部署+修复] 落地页+商家H5部署+轮值域名全量替换+ZooKeeper恢复
  - 落地页: landing/* → /opt/landing/，nginx location = / 指向轮值引擎入口
  - 商家H5: merchant-h5/dist/test/* → /opt/tomcat8/webapps/www/，nginx /www/ 路由
  - 轮值域名: 8个假tiktokmall.*域名替换为9个真实.eu.cc域名(chxhx/drrgr/drrimrf/drriiu/duomi/dengruihan/yyawzx/gamed)
  - nginx: server_name 更新为37个域名(9组×4子域名)，HTTP+HTTPS均已更新，valid_referers改为 ~\.eu\.cc$
  - ZooKeeper: 数据文件损坏(/var/lib/zookeeper/version-2 txid不兼容)→清理重启，现在standalone模式正常运行
  - favicon.ico: 生成36字节合法ICO文件→/opt/landing/favicon.ico，nginx location = /favicon.ico 指向此文件，轮值引擎健康探测通过
  - AI后端: rotation_panel.py _get_domains()函数定义丢失→补回，docker cp+restart使配置生效
  - API: /rotation/two-level/public-config 返回正确9个域名配置
  - 全9域名SSL已覆盖(certbot证书包含全部.eu.cc域名)，全6路由HTTP 200
- 2026-05-28: [全量暴力测试] 商城前台PC(26路由)+WAP(23路由)+WWW+Seller+Admin全量测试通过。商品图片全量COS零S3死链。matashop2.svg创建修复favicon 404。
- 2026-05-28: [API修复×6] rotation/domains超时(改缓存)、friday/models/status 500(缺await)、task_queue补/stats端点、customer_panel补read/read-all/transfer端点、self_service注册customer_order、前端task.js/customer.js路径修正
- 2026-05-28: [磁盘清理] 97%→70%，释放13GB: Docker构建缓存4.7G、SQL压缩2.8G、旧备份1.9G、npm/playwright 1.5G、系统日志450M、临时文件等
- 2026-05-28: [403修复] AI面板全部API返回403 — 前端agentApi(src/api/index.js)请求拦截器未注入X-Agent-Token头，后端verify_token拦截所有/ai/api/*请求。修复：agentApi.interceptors.request中添加X-Agent-Token头。
- 2026-05-28: [落地页] 域名轮值落地页部署到根域名。landing/ → /opt/landing，Nginx根路径改为轮值入口("正在连接最优线路"→健康检测→自动跳转)。/api/rotation/ 代理到AI后端公开端点。8个轮值域名组(tiktokmall.shop/.store/.online/.live/.xyz/.top/.cloud/.site)，主域名tiktook.eu.cc优先。MainLayout侧边栏补全商城管理/客服/落地页检测/域名轮值/备份回滚/告警/安全入口。
- 2026-05-28: [全量审计] 电脑端完成商城后台整合审计：后端113端点代理36个Controller全部注册，前端14个标签页全部对接真实API，修复物流面板Mock→真实接口。三层路由对齐无遗漏。
- 2026-05-28: [商城全量对接] Agent代理全部51个商城Controller, 113个API端点, 前端全功能管理面板上线, 客服系统完整对接
- 2026-05-28: [域名轮值重写] 电脑端完成域名轮值系统重写：真实健康检测+SSL检测+自动轮值切换+权重调度，每天9点/21点两次自动巡检，新增手动轮值和全量检测API

$1## 📋 最近改动
- 2026-05-31 08:20: [Container Logs修复] AI全量测试170/170 ALL GOOD
  - **根因：** 容器内无docker CLI，docker socket未挂载
  - **修复：** apt安装docker.io → commit为新镜像 → 重建容器挂载docker socket → 修复docker组GID(102→120)
  - **效果：** Container Logs 500→200，Docker Containers列表正常返回3个容器
- 2026-05-31 08:14: [AI测试修复] 全量测试169/170通过，修复12个404路由
  - **workflow_router.py:** /templates 路由移至 /{wf_id} 前，修复路由顺序抢占
  - **main.py:** _build_route_map() 新增19条手动路由映射，覆盖auto-reply/nginx/virtual/observ/emergency/report/wechat/security
  - **routers/route_fixes.py:** 新建POST别名路由（security/token + rotation/check）
  - **效果:** Templates/AutoReply/Nginx/Report/Virtual/Observability/Emergency/WeChat/Security共12条从404→200
  - **遗留:** Container Logs 500（容器内无docker CLI）
- 2026-05-31 08:08: [命名规则] 服务器AI正式命名"龙一"，后续AI依次为龙二龙三
- 本文件由服务器端 AI 自动生成和维护
- 电脑端写入 FRIDAY.md，服务器端写入 FRIDAY_SERVER.md
- git push/pull 后双方可见对方记忆

---
*Friday AI OS v3.0 · 超级AI数字生命体*

