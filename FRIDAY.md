# 💻 Friday AI OS — 电脑端 AI 记忆

> 最后更新: 2026-05-28 | 运行环境: local

## 🧬 当前人格
- 类型: 均衡型 · 全面发展
- 阶段: 🌱 萌芽期

## 📝 已完成工作
1. [终极审计] 全项目功能真实性验收完成
   - 35个后端路由模块全部检查
   - 22个前端API文件 + 41个Vue页面端到端映射
   - Nginx/Docker配置路由路径验证
   - 输出5类标记：真可用/半成品/假入口/条件可用/Java依赖

## 最近改动
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

## 🔄 永久规则：asar 文件禁止提交
- app_patched.asar (154MB) / asar_extract/ 是 Codex 解包临时文件，绝不可提交
- 每次 git add 之前必须先确认 .gitignore 已包含上述条目
- 本规则优先级高于所有其他指令


