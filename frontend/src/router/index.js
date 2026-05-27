import { createRouter, createWebHistory } from "vue-router"

const routes = [
  {
    path: "/",
    component: () => import("@/layout/MainLayout.vue"),
    redirect: "/friday",
    children: [
      // ===== Friday AI OS 核心 =====
      {
        path: "friday",
        name: "FridayBrain",
        component: () => import("@/views/FridayBrain.vue"),
        meta: { title: "Friday AI OS" },
      },
      {
              {
        path: "agents",
        name: "AgentPanel",
        component: () => import("@/views/AgentPanel.vue"),
        meta: { title: "Agent面板" },
      },
      {
        path: "trends",
        name: "TrendMonitor",
        component: () => import("@/views/TrendMonitor.vue"),
        meta: { title: "热点监控" },
      },      {
        path: "dashboard",
        name: "Dashboard",
        component: () => import("@/views/Dashboard.vue"),
        meta: { title: "数据总览" },
      },
      {
        path: "chat",
        name: "AIChat",
        component: () => import("@/views/AIChat.vue"),
        meta: { title: "AI 对话" },
      },

      // ===== AI 大脑 =====
      {
        path: "ai-brain",
        name: "AIBrain",
        component: () => import("@/views/AIBrain.vue"),
        meta: { title: "AI 大脑" },
      },
      {
        path: "evolution",
        name: "EvolutionReport",
        component: () => import("@/views/EvolutionReport.vue"),
        meta: { title: "进化报告" },
      },
      {
        path: "scraper",
        name: "ScraperCenter",
        component: () => import("@/views/ScraperCenter.vue"),
        meta: { title: "采集中心" },
      },
      {
        path: "virtual",
        name: "VirtualData",
        component: () => import("@/views/VirtualData.vue"),
        meta: { title: "虚拟数据" },
      },

      // ===== 基础设施 =====
      {
        path: "server",
        name: "ServerPanel",
        component: () => import("@/views/ServerPanel.vue"),
        meta: { title: "服务器" },
      },
      {
        path: "docker",
        name: "DockerPanel",
        component: () => import("@/views/DockerPanel.vue"),
        meta: { title: "Docker" },
      },
      {
        path: "nginx",
        name: "NginxPanel",
        component: () => import("@/views/NginxPanel.vue"),
        meta: { title: "Nginx" },
      },

      // ===== 运营管理 =====
      {
        path: "mall",
        name: "MallPanel",
        component: () => import("@/views/MallPanel.vue"),
        meta: { title: "商城管理" },
      },
      {
        path: "site",
        name: "SiteCheck",
        component: () => import("@/views/SiteCheck.vue"),
        meta: { title: "网站检测" },
      },
      {
        path: "customer",
        name: "CustomerPanel",
        component: () => import("@/views/CustomerPanel.vue"),
        meta: { title: "客服" },
      },

      // ===== 系统 =====
      {
        path: "alert",
        name: "AlertCenter",
        component: () => import("@/views/AlertCenter.vue"),
        meta: { title: "告警中心" },
      },
      {
        path: "security",
        name: "SecurityPanel",
        component: () => import("@/views/SecurityPanel.vue"),
        meta: { title: "安全中心" },
      },
      {
        path: "rollback",
        name: "RollbackCenter",
        component: () => import("@/views/RollbackCenter.vue"),
        meta: { title: "备份回滚" },
      },
      {
        path: "rotation",
        name: "RotationPanel",
        component: () => import("@/views/RotationPanel.vue"),
        meta: { title: "轮值" },
      },
      {
        path: "approval",
        name: "ApprovalCenter",
        component: () => import("@/views/ApprovalCenter.vue"),
        meta: { title: "审批中心" },
      },
    ],
  },
  {
    path: "/emergency",
    name: "Emergency",
    component: () => import("@/views/EmergencyPanel.vue"),
    meta: { title: "急救面板" },
  },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: () => import("@/views/NotFound.vue"),
  },
]

const router = createRouter({
  history: createWebHistory("/ai/"),
  routes,
})

export default router

