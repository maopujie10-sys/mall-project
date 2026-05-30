import { createRouter, createWebHistory } from "vue-router"

const routes = [
  {
    path: "/",
    component: () => import("@/layout/MainLayout.vue"),
    redirect: "/friday",
    children: [
      { path: "friday", name: "FridayBrain", component: () => import("@/views/FridayBrain.vue"), meta: { title: "Friday AI OS" } },
      { path: "dashboard", name: "Dashboard", component: () => import("@/views/Dashboard.vue"), meta: { title: '' } },

      { path: "ai-brain", name: "AIBrain", component: () => import("@/views/AIBrain.vue"), meta: { title: "AI " } },
      { path: "agents", name: "AgentPanel", component: () => import("@/views/AgentPanel.vue"), meta: { title: "Agent" } },
      { path: "evolution", name: "EvolutionReport", component: () => import("@/views/EvolutionReport.vue"), meta: { title: '' } },
      { path: "models", name: "ModelCenter", component: () => import("@/views/ModelCenter.vue"), meta: { title: '' } },
      { path: "memory", name: "MemoryCenter", component: () => import("@/views/MemoryCenter.vue"), meta: { title: '' } },

      { path: "server", name: "ServerPanel", component: () => import("@/views/ServerPanel.vue"), meta: { title: '' } },
      { path: "docker", name: "DockerPanel", component: () => import("@/views/DockerPanel.vue"), meta: { title: "Docker" } },
      { path: "nginx", name: "NginxPanel", component: () => import("@/views/NginxPanel.vue"), meta: { title: "Nginx" } },
      { path: "database", name: "DatabasePanel", component: () => import("@/views/DatabasePanel.vue"), meta: { title: '' } },

      { path: "mall", name: "MallPanel", component: () => import("@/views/MallPanel.vue"), meta: { title: '' } },
      { path: "site", name: "SiteCheck", component: () => import("@/views/SiteCheck.vue"), meta: { title: '' } },
      { path: "customer", name: "CustomerPanel", component: () => import("@/views/CustomerPanel.vue"), meta: { title: '' } },

      { path: "trends", name: "TrendMonitor", component: () => import("@/views/TrendMonitor.vue"), meta: { title: '' } },
      { path: "scraper", name: "ScraperCenter", component: () => import("@/views/ScraperCenter.vue"), meta: { title: '' } },
      { path: "virtual", name: "VirtualData", component: () => import("@/views/VirtualData.vue"), meta: { title: '' } },

      { path: "video", name: "VideoPanel", component: () => import("@/views/VideoPanel.vue"), meta: { title: '' } },
      { path: "ocr", name: "OcrPanel", component: () => import("@/views/OcrPanel.vue"), meta: { title: "OCR" } },
      { path: "plugins", name: "PluginCenter", component: () => import("@/views/PluginCenter.vue"), meta: { title: '' } },
      { path: "tasks", name: "TaskCenter", component: () => import("@/views/TaskCenter.vue"), meta: { title: '' } },
      { path: "self-healing", name: "SelfHealing", component: () => import("@/views/SelfHealing.vue"), meta: { title: '' } },
      { path: "weekly-report", name: "WeeklyReport", component: () => import("@/views/WeeklyReport.vue"), meta: { title: '' } },
      { path: "log-viewer", name: "LogViewer", component: () => import("@/views/LogViewer.vue"), meta: { title: '' } },
      { path: "self-service", name: "SelfService", component: () => import("@/views/SelfService.vue"), meta: { title: '' } },
      { path: "workflow", name: "WorkflowEditor", component: () => import("@/views/WorkflowEditor.vue"), meta: { title: '' } },

      { path: "alert", name: "AlertCenter", component: () => import("@/views/AlertCenter.vue"), meta: { title: '' } },
      { path: "security", name: "SecurityPanel", component: () => import("@/views/SecurityPanel.vue"), meta: { title: '' } },
      { path: "rollback", name: "RollbackCenter", component: () => import("@/views/RollbackCenter.vue"), meta: { title: '' } },
      { path: "rotation", name: "RotationPanel", component: () => import("@/views/RotationPanel.vue"), meta: { title: '' } },
      { path: "approval", name: "ApprovalCenter", component: () => import("@/views/ApprovalCenter.vue"), meta: { title: '' } },
      { path: "audit", name: "AuditLog", component: () => import("@/views/AuditLog.vue"), meta: { title: '' } },
      { path: "files", name: "FileManager", component: () => import("@/views/FileManager.vue"), meta: { title: '' } },
      { path: "network", name: "NetworkTools", component: () => import("@/views/NetworkTools.vue"), meta: { title: '' } },
      { path: "github", name: "GitHubPanel", component: () => import("@/views/GitHubPanel.vue"), meta: { title: "GitHub" } },
      { path: "emergency", name: "Emergency", component: () => import("@/views/EmergencyPanel.vue"), meta: { title: '' } },
      { path: "phone", name: "PhoneAssistant", component: () => import("@/views/PhoneAssistant.vue"), meta: { title: "AI" } },
      { path: "image-process", name: "ImageProcessor", component: () => import("@/views/ImageProcessor.vue"), meta: { title: "AI" } },
      { path: "multilang", name: "MultiLangPublish", component: () => import("@/views/MultiLangPublish.vue"), meta: { title: '' } },
      { path: "batch-upload", name: "BatchUpload", component: () => import("@/views/BatchUpload.vue"), meta: { title: '' } },
      { path: "auto-reply", name: "AutoReply", component: () => import("@/views/AutoReply.vue"), meta: { title: '' } },
      { path: "order-alert", name: "OrderAlert", component: () => import("@/views/OrderAlert.vue"), meta: { title: '' } },

      // === AI v5 ===
      { path: "voice-chat", name: "VoiceChat", component: () => import("@/views/VoiceChat.vue"), meta: { title: '' } },
      { path: "agent-collab", name: "AgentCollab", component: () => import("@/views/AgentCollab.vue"), meta: { title: "Agent" } },
      { path: "knowledge", name: "KnowledgeHub", component: () => import("@/views/KnowledgeHub.vue"), meta: { title: '' } },
      { path: "code-deploy", name: "CodeDeploy", component: () => import("@/views/CodeDeploy.vue"), meta: { title: "AI" } },
      { path: "predict", name: "PredictDashboard", component: () => import("@/views/PredictDashboard.vue"), meta: { title: '' } },
      { path: "recommend", name: "RecommendPanel", component: () => import("@/views/RecommendPanel.vue"), meta: { title: '' } },
      { path: "competitor", name: "CompetitorMonitor", component: () => import("@/views/CompetitorMonitor.vue"), meta: { title: '' } },
      { path: "customer-profile", name: "CustomerProfile", component: () => import("@/views/CustomerProfile.vue"), meta: { title: '' } },
      { path: "text2sql", name: "Text2SQLPanel", component: () => import("@/views/Text2SQLPanel.vue"), meta: { title: '' } },
      { path: "content-factory", name: "ContentFactory", component: () => import("@/views/ContentFactory.vue"), meta: { title: "AI" } },
      { path: "skill-market", name: "SkillMarket", component: () => import("@/views/SkillMarket.vue"), meta: { title: '' } },
      { path: "memory-sync", name: "MemorySync", component: () => import("@/views/MemorySync.vue"), meta: { title: '' } },
      { path: "ab-test", name: "ABTestPanel", component: () => import("@/views/ABTestPanel.vue"), meta: { title: "A/B" } },
      { path: "security-scan", name: "SecurityScan", component: () => import("@/views/SecurityScan.vue"), meta: { title: '' } },
      { path: 'capabilities', name: 'Capabilities', component: () => import('@/views/Capabilities.vue'), meta: { title: 'AI' } },
      { path: 'key-manager', name: 'KeyManager', component: () => import('@/views/KeyManager.vue'), meta: { title: 'API Key' } },
      { path: 'user-manager', name: 'UserManager', component: () => import('@/views/UserManager.vue'), meta: { title: '' } },
      { path: 'advanced-ai', name: 'AdvancedAI', component: () => import('@/views/AdvancedAI.vue'), meta: { title: 'AI' } },
      { path: 'ai-tools', name: 'AITools', component: () => import('@/views/AITools.vue'), meta: { title: 'AI' } },
      { path: 'wechat-config', name: 'WechatConfig', component: () => import('@/views/WechatConfig.vue'), meta: { title: '' } },
      { path: 'ecommerce-ai', name: 'EcommerceAI', component: () => import('@/views/EcommerceAI.vue'), meta: { title: 'AI' } },    ],
  },
]

const router = createRouter({ history: createWebHistory("/ai/"), routes })
export default router



