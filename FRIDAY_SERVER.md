# 🖥️ Friday AI OS — 服务器端 AI 记忆

> 最后更新: 2026-05-28 | 运行环境: server

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
- 2026-05-28: [403修复] AI面板全部API返回403 — 前端agentApi(src/api/index.js)请求拦截器未注入X-Agent-Token头，后端verify_token拦截所有/ai/api/*请求。修复：agentApi.interceptors.request中添加X-Agent-Token头。前端镜像已重新构建并重启。
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

