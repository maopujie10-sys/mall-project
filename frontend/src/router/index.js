import { createRouter, createWebHistory } from "vue-router"

const routes = [
  {
    path: "/",
    component: () => import("@/layout/MainLayout.vue"),
    redirect: "/friday",
    children: [
      { path: "friday", name: "FridayBrain", component: () => import("@/views/FridayBrain.vue"), meta: { title: "Friday AI OS" } },
      { path: "dashboard", name: "Dashboard", component: () => import("@/views/Dashboard.vue"), meta: { title: "数据总览" } },

      { path: "ai-brain", name: "AIBrain", component: () => import("@/views/AIBrain.vue"), meta: { title: "AI 大脑" } },
      { path: "agents", name: "AgentPanel", component: () => import("@/views/AgentPanel.vue"), meta: { title: "Agent面板" } },
      { path: "evolution", name: "EvolutionReport", component: () => import("@/views/EvolutionReport.vue"), meta: { title: "进化报告" } },
      { path: "models", name: "ModelCenter", component: () => import("@/views/ModelCenter.vue"), meta: { title: "模型中心" } },
      { path: "memory", name: "MemoryCenter", component: () => import("@/views/MemoryCenter.vue"), meta: { title: "记忆中心" } },

      { path: "server", name: "ServerPanel", component: () => import("@/views/ServerPanel.vue"), meta: { title: "服务器" } },
      { path: "docker", name: "DockerPanel", component: () => import("@/views/DockerPanel.vue"), meta: { title: "Docker" } },
      { path: "nginx", name: "NginxPanel", component: () => import("@/views/NginxPanel.vue"), meta: { title: "Nginx" } },
      { path: "database", name: "DatabasePanel", component: () => import("@/views/DatabasePanel.vue"), meta: { title: "数据库" } },

      { path: "mall", name: "MallPanel", component: () => import("@/views/MallPanel.vue"), meta: { title: "商城管理" } },
      { path: "site", name: "SiteCheck", component: () => import("@/views/SiteCheck.vue"), meta: { title: "网站检测" } },
      { path: "customer", name: "CustomerPanel", component: () => import("@/views/CustomerPanel.vue"), meta: { title: "客服" } },

      { path: "trends", name: "TrendMonitor", component: () => import("@/views/TrendMonitor.vue"), meta: { title: "热点监控" } },
      { path: "scraper", name: "ScraperCenter", component: () => import("@/views/ScraperCenter.vue"), meta: { title: "采集中心" } },
      { path: "virtual", name: "VirtualData", component: () => import("@/views/VirtualData.vue"), meta: { title: "虚拟数据" } },

      { path: "video", name: "VideoPanel", component: () => import("@/views/VideoPanel.vue"), meta: { title: "视频分析" } },
      { path: "ocr", name: "OcrPanel", component: () => import("@/views/OcrPanel.vue"), meta: { title: "OCR识别" } },
      { path: "plugins", name: "PluginCenter", component: () => import("@/views/PluginCenter.vue"), meta: { title: "插件系统" } },
      { path: "tasks", name: "TaskCenter", component: () => import("@/views/TaskCenter.vue"), meta: { title: "自动任务" } },
      { path: "self-healing", name: "SelfHealing", component: () => import("@/views/SelfHealing.vue"), meta: { title: "异常自愈" } },
      { path: "weekly-report", name: "WeeklyReport", component: () => import("@/views/WeeklyReport.vue"), meta: { title: "运营周报" } },
      { path: "log-viewer", name: "LogViewer", component: () => import("@/views/LogViewer.vue"), meta: { title: "日志中心" } },
      { path: "self-service", name: "SelfService", component: () => import("@/views/SelfService.vue"), meta: { title: "自助服务" } },
      { path: "workflow", name: "WorkflowEditor", component: () => import("@/views/WorkflowEditor.vue"), meta: { title: "工作流编辑器" } },

      { path: "alert", name: "AlertCenter", component: () => import("@/views/AlertCenter.vue"), meta: { title: "告警中心" } },
      { path: "security", name: "SecurityPanel", component: () => import("@/views/SecurityPanel.vue"), meta: { title: "安全中心" } },
      { path: "rollback", name: "RollbackCenter", component: () => import("@/views/RollbackCenter.vue"), meta: { title: "备份回滚" } },
      { path: "rotation", name: "RotationPanel", component: () => import("@/views/RotationPanel.vue"), meta: { title: "轮值" } },
      { path: "approval", name: "ApprovalCenter", component: () => import("@/views/ApprovalCenter.vue"), meta: { title: "审批中心" } },
      { path: "audit", name: "AuditLog", component: () => import("@/views/AuditLog.vue"), meta: { title: "审计日志" } },
      { path: "files", name: "FileManager", component: () => import("@/views/FileManager.vue"), meta: { title: "文件管理" } },
      { path: "network", name: "NetworkTools", component: () => import("@/views/NetworkTools.vue"), meta: { title: "网络工具" } },
      { path: "github", name: "GitHubPanel", component: () => import("@/views/GitHubPanel.vue"), meta: { title: "GitHub" } },
      { path: "emergency", name: "Emergency", component: () => import("@/views/EmergencyPanel.vue"), meta: { title: "急救面板" } },
      { path: "phone", name: "PhoneAssistant", component: () => import("@/views/PhoneAssistant.vue"), meta: { title: "AI电话助理" } },
      { path: "image-process", name: "ImageProcessor", component: () => import("@/views/ImageProcessor.vue"), meta: { title: "AI商品图" } },
      { path: "multilang", name: "MultiLangPublish", component: () => import("@/views/MultiLangPublish.vue"), meta: { title: "多语言发布" } },
      { path: "batch-upload", name: "BatchUpload", component: () => import("@/views/BatchUpload.vue"), meta: { title: "批量上架" } },
      { path: "auto-reply", name: "AutoReply", component: () => import("@/views/AutoReply.vue"), meta: { title: "自动回复" } },
      { path: "order-alert", name: "OrderAlert", component: () => import("@/views/OrderAlert.vue"), meta: { title: "订单预警" } },

      // === 全能AI升级 v5 ===
      { path: "voice-chat", name: "VoiceChat", component: () => import("@/views/VoiceChat.vue"), meta: { title: "语音对话" } },
      { path: "agent-collab", name: "AgentCollab", component: () => import("@/views/AgentCollab.vue"), meta: { title: "Agent协作" } },
      { path: "knowledge", name: "KnowledgeHub", component: () => import("@/views/KnowledgeHub.vue"), meta: { title: "知识中心" } },
      { path: "code-deploy", name: "CodeDeploy", component: () => import("@/views/CodeDeploy.vue"), meta: { title: "AI代码部署" } },
      { path: "predict", name: "PredictDashboard", component: () => import("@/views/PredictDashboard.vue"), meta: { title: "预测分析" } },
      { path: "recommend", name: "RecommendPanel", component: () => import("@/views/RecommendPanel.vue"), meta: { title: "推荐引擎" } },
      { path: "competitor", name: "CompetitorMonitor", component: () => import("@/views/CompetitorMonitor.vue"), meta: { title: "竞品监控" } },
      { path: "customer-profile", name: "CustomerProfile", component: () => import("@/views/CustomerProfile.vue"), meta: { title: "客户画像" } },
      { path: "text2sql", name: "Text2SQLPanel", component: () => import("@/views/Text2SQLPanel.vue"), meta: { title: "自然语言查库" } },
      { path: "content-factory", name: "ContentFactory", component: () => import("@/views/ContentFactory.vue"), meta: { title: "AI内容工厂" } },
      { path: "skill-market", name: "SkillMarket", component: () => import("@/views/SkillMarket.vue"), meta: { title: "技能市场" } },
      { path: "memory-sync", name: "MemorySync", component: () => import("@/views/MemorySync.vue"), meta: { title: "跨平台记忆" } },
      { path: "ab-test", name: "ABTestPanel", component: () => import("@/views/ABTestPanel.vue"), meta: { title: "A/B测试" } },
      { path: "security-scan", name: "SecurityScan", component: () => import("@/views/SecurityScan.vue"), meta: { title: "安全扫描" } },
      { path: 'capabilities', name: 'Capabilities', component: () => import('@/views/Capabilities.vue'), meta: { title: 'AI能力状态' } },
      { path: 'key-manager', name: 'KeyManager', component: () => import('@/views/KeyManager.vue'), meta: { title: 'API Key管理' } },
      { path: 'user-manager', name: 'UserManager', component: () => import('@/views/UserManager.vue'), meta: { title: '用户管理' } },
      { path: 'advanced-ai', name: 'AdvancedAI', component: () => import('@/views/AdvancedAI.vue'), meta: { title: '高级AI' } },
      { path: 'ai-tools', name: 'AITools', component: () => import('@/views/AITools.vue'), meta: { title: 'AI工具箱' } },
      { path: 'ecommerce-ai', name: 'EcommerceAI', component: () => import('@/views/EcommerceAI.vue'), meta: { title: 'AI电商引擎' } },
      { path: '/:pathMatch(.*)*', redirect: '/friday' },
    ],
  },
]

const router = createRouter({ history: createWebHistory("/ai/"), routes })
export default router



