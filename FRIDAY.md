# 💻 Friday AI OS — 电脑端 AI 记忆

> 最后更新: 2026-05-28 | 运行环境: local

## 🧬 当前人格
- 类型: 均衡型 · 全面发展
- 阶段: 🌱 萌芽期

## 📋 已完成工作
1. 后端3项修复 (启动自检/进化工具/意图匹配)
2. 前端全面升级 (3D神经网络/总控台/6个新页面/AI对话)
3. PWA双端 + Electron桌面版
4. 7大Agent系统 (Master/Code/Trend/Vision/Playwright/MultiModel/Memory)
5. 8维数字人格 + 每日日记 + HANDOFF
6. Git记忆同步 (FRIDAY.md ↔ FRIDAY_SERVER.md)
7. mall-app 商城整合 (后端未改)
8. Jarvis深蓝科技风全局主题
9. WebSocket实时推送
10. 统一docker-compose编排

## 最近改动
- 2026-05-28: [验收完成] VisionAgent OCR/视频/物体/人脸, AI Factory作图/文案, 模拟用户测试, init.sql补2表
- 2026-05-28: [前端API接入] Dashboard/AIBrain/ScraperCenter/VirtualData 4个核心页面从mock改为真实API调用
- 2026-05-28: [V5补全] 完成6项关键功能：
  1. SuperInput.vue — 修复脚本乱码，新增浏览器语音识别(Web Speech API)+摄像头拍照(getUserMedia)
  2. mask.py — 新建数据脱敏模块(手机/邮箱/密码/支付/身份证/地址)，接入customer_panel/mall_tools/sql_executor
  3. FRIDAY_SERVER.md — 创建服务器端AI记忆档案，实现双向记忆同步
  4. state.py — 接入MySQL+SQLite双层持久化，重启不丢数据
  5. diff_utils.py — 变更预览diff，审批中心展示修改前后对比
  6. scheduler.py — APScheduler定时任务(30分钟巡检/每日备份/轮值检测/商城扫描)，接入main.py启动
- 2026-05-28: AGENTS.md — 新增防Git冲突铁律：改前pull+读FRIDAY，改后写FRIDAY+push
