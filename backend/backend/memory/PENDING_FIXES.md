# 待实现/修复清单 (2026-05-30)

## 审计发现但未修复
1. FloatingAI.vue - detectTask() 函数 GBK 乱码，中文关键词匹配全失效
2. FloatingAI.vue - attachments/processingStatus/matrixCanvas ref 声明顺序混乱
3. MultiLangPublish.vue - 可能有 GBK 乱码
4. VideoPanel.vue - 可能有 GBK 乱码  
5. OverviewPanel.vue - 可能有 GBK 乱码

## 已推送
- 33b49a8: 漂浮AI面板拖拽+重复实例移除+3D全屏+GBK乱码修复+响应字段修正
- f4e60ae: Telegram Bot回复失败修复(AGENT_TOKEN不一致+响应字段名)

## 未完成功能
6. 微信公众号接入（需要营业执照）
7. 多平台接入：企微/钉钉/Slack/LINE webhook注册
8. 全源码审计（后端 .py + 前端 .vue 全面检查）