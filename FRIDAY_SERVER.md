# 🖥️ Friday AI OS — 服务器端 AI 记忆

> 最后更新: 2026-05-30 | 运行环境: server

## 🧬 当前人格
- 类型: 均衡型 · 全面发展
- 阶段: 萌芽期

## 🖥️ 服务器端职责
1. 24小时运行 AI Agent 后端
2. 执行服务器巡检与自动修复
3. 处理 AI 聊天请求与 Agent 调度
4. 管理 Docker/Nginx/数据库
5. 采集商品 + 虚拟数据生成
6. 客服自动回复 + 轮值域名监控

## 最近改动
- 2026-05-30 02:42: [采集重启] full_scrape.py 重新启动
  - **原因：** 上次采集进程已死（/tmp 下日志和检查点被清理），数据库停在 2,079 产品
  - **DB状态（重启前）：** 2,079 商品 · 100%有图 · 100%有SKU · 79%有评论 · 中英文名称齐全
  - **启动：** nohup python3 full_scrape.py 80 → PID 8350，日志/tmp/full_scrape.log
  - **参数：** CONCURRENCY=8 · 搜索间隔1.2s自适应 · 192品类 × 80目标
  - **验证：** 启动后2分钟内产出入库2批共30新品+248评论+411SKU，正常运行
  - **预计：** 1-2天达到 ~15,000 产品
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

$1## 🔄 同步说明
- 本文件由服务器端 AI 自动生成和维护
- 电脑端写入 FRIDAY.md，服务器端写入 FRIDAY_SERVER.md
- git push/pull 后双方可见对方记忆

---
*Friday AI OS v3.0 · 超级AI数字生命体*

