# 🖥️ Friday AI OS — 服务器端 AI 记忆

> 最后更新: 2026-05-29 | 运行环境: server

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

