import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: 'AI 总控台', icon: 'Monitor' },
      },
      {
        path: 'chat',
        name: 'AIChat',
        component: () => import('@/views/AIChat.vue'),
        meta: { title: 'AI 对话', icon: 'ChatDotRound' },
      },
      {
        path: 'server',
        name: 'ServerPanel',
        component: () => import('@/views/ServerPanel.vue'),
        meta: { title: '服务器', icon: 'Monitor' },
      },
      {
        path: 'mall',
        name: 'MallPanel',
        component: () => import('@/views/MallPanel.vue'),
        meta: { title: '商城', icon: 'ShoppingCart' },
      },
      {
        path: 'customer',
        name: 'CustomerPanel',
        component: () => import('@/views/CustomerPanel.vue'),
        meta: { title: '客服', icon: 'Service' },
      },
      {
        path: 'rotation',
        name: 'RotationPanel',
        component: () => import('@/views/RotationPanel.vue'),
        meta: { title: '轮值', icon: 'Connection' },
      },
      {
        path: 'approval',
        name: 'ApprovalCenter',
        component: () => import('@/views/ApprovalCenter.vue'),
        meta: { title: '审批中心', icon: 'Checked' },
      },
      {
        path: 'rollback',
        name: 'RollbackCenter',
        component: () => import('@/views/RollbackCenter.vue'),
        meta: { title: '回滚中心', icon: 'RefreshRight' },
      },
      {
        path: 'security',
        name: 'SecurityPanel',
        component: () => import('@/views/SecurityPanel.vue'),
        meta: { title: '安全设置', icon: 'Lock' },
      },
      {
        path: 'attrs',
        name: 'AttrPanel',
        component: () => import('@/views/AttrPanel.vue'),
        meta: { title: '商品属性', icon: 'SetUp' },
      },
    ],
  },
  {
    path: '/emergency',
    name: 'Emergency',
    component: () => import('@/views/EmergencyPanel.vue'),
    meta: { title: '急救面板' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory('/ai/'),
  routes,
})

export default router
