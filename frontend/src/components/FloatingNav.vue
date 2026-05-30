<template>
  <div class="floating-nav-container">
    <div
      v-for="cat in categories"
      :key="cat.id"
      class="nav-orb"
      :class="{ active: activeCat === cat.id, dragging: cat.dragging }"
      :style="{ left: cat.x + 'px', top: cat.y + 'px' }"
      @mousedown="startDrag($event, cat)"
      @touchstart="startDrag($event, cat)"
      @click="toggleCat(cat)"
    >
      <!-- 全息光晕 -->
      <div class="orb-glow"></div>
      <div class="orb-glow-inner"></div>
      <!-- 旋转环 -->
      <div class="orb-ring r1"></div>
      <div class="orb-ring r2"></div>
      <div class="orb-ring r3"></div>
      <!-- 核心 -->
      <div class="orb-core">
        <div class="orb-core-bg"></div>
        <span class="orb-icon">{{ cat.icon }}</span>
        <span class="orb-label">{{ cat.label }}</span>
      </div>
      <!-- 粒子 -->
      <div class="orb-particles">
        <span v-for="i in 8" :key="i" class="orb-particle" :style="particleStyle(i)"></span>
      </div>
      <!-- 扫描线 -->
      <div class="orb-scanline"></div>
    </div>

    <!-- 分类面板 -->
    <transition name="panel-fade">
      <div v-if="activeCat" class="category-panel" :style="panelStyle">
        <div class="panel-scanline"></div>
        <div class="panel-header">
          <div class="ph-icon-wrap">
            <div class="ph-icon-glow"></div>
            <span class="ph-icon">{{ activeCategory?.icon }}</span>
          </div>
          <span class="ph-title">{{ activeCategory?.label }}</span>
          <button class="ph-close" @click="activeCat = null">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="panel-body">
          <router-link
            v-for="item in activeCategory?.items"
            :key="item.to + item.label"
            :to="item.to ? { name: item.to } : ''"
            class="panel-item"
            @click="item.action ? handleAction(item.action) : (activeCat = null)"
          >
            <span class="pi-glow"></span>
            <span class="pi-icon">{{ item.icon }}</span>
            <span class="pi-label">{{ item.label }}</span>
            <span class="pi-arrow">→</span>
          </router-link>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'

const activeCat = ref(null)

const categories = reactive([
  {
    id: 'core', icon: '\u{1F9E0}', label: 'AI核心', x: 0, y: 0, dragging: false,
    items: [
      { to: 'friday', icon: '\u{1F9E0}', label: 'Friday 大脑' },
      { to: '', icon: '\u{1F4AC}', label: 'AI 对话', action: 'openChat' },
      { to: 'agents', icon: '\u{1F916}', label: 'Agent 列表' },
      { to: 'models', icon: '\u{1F52C}', label: '模型中心' },
      { to: 'memory', icon: '\u{1F4BE}', label: '记忆中心' },
      { to: 'evolution', icon: '\u{1F331}', label: '进化报告' },
      { to: 'knowledge', icon: '\u{1F4DA}', label: '知识中心' },
      { to: 'memory-sync', icon: '\u{1F504}', label: '跨平台记忆' },
      { to: 'voice-chat', icon: '\u{1F399}', label: '语音对话' },
      { to: 'video', icon: '\u{1F3AC}', label: '视频分析' },
      { to: 'ocr', icon: '\u{1F50D}', label: 'OCR 识别' },
      { to: 'agent-collab', icon: '\u{1F91D}', label: 'Agent 协作' },
      { to: 'skill-market', icon: '\u{1F9E9}', label: '技能市场' },
      { to: 'capabilities', icon: '\u{1F527}', label: 'AI能力状态' },
      { to: 'advanced-ai', icon: '\u{1F680}', label: '高级AI' },
      { to: 'ai-tools', icon: '\u{1F527}', label: 'AI工具箱' },
      { to: 'workflow', icon: '\u{1F3AF}', label: '工作流编辑器' },
    ]
  },
  {
    id: 'data', icon: '\u{1F4CA}', label: '数据监控', x: 0, y: 0, dragging: false,
    items: [
      { to: 'dashboard', icon: '\u{1F4CA}', label: '数据总览' },
      { to: 'trends', icon: '\u{1F4C8}', label: '趋势监控' },
      { to: 'scraper', icon: '\u{1F577}', label: '采集中心' },
      { to: 'database', icon: '\u{1F5C4}', label: '数据库' },
      { to: 'log-viewer', icon: '\u{1F4CB}', label: '日志中心' },
      { to: 'weekly-report', icon: '\u{1F4CA}', label: '运营周报' },
      { to: 'text2sql', icon: '\u{1F5C4}', label: '自然语言查库' },
      { to: 'competitor', icon: '\u{1F575}', label: '竞品监控' },
      { to: 'customer-profile', icon: '\u{1F465}', label: '客户画像' },
      { to: 'predict', icon: '\u{1F4C8}', label: '预测分析' },
      { to: 'recommend', icon: '\u{1F3AF}', label: '推荐引擎' },
      { to: 'ab-test', icon: '\u{1F9EA}', label: 'A/B测试' },
      { to: 'virtual', icon: '\u{1F3AE}', label: '虚拟数据' },
    ]
  },
  {
    id: 'ops', icon: '\u{1F6E1}', label: '安全运维', x: 0, y: 0, dragging: false,
    items: [
      { to: 'server', icon: '\u{1F5A5}', label: '服务器' },
      { to: 'docker', icon: '\u{1F433}', label: 'Docker' },
      { to: 'nginx', icon: '\u{1F527}', label: 'Nginx' },
      { to: 'network', icon: '\u{1F310}', label: '网络工具' },
      { to: 'github', icon: '\u{1F419}', label: 'GitHub MCP' },
      { to: 'rotation', icon: '\u{1F504}', label: '域名轮值' },
      { to: 'site', icon: '\u{1F310}', label: '站点检测' },
      { to: 'rollback', icon: '⏪', label: '备份回滚' },
      { to: 'security', icon: '\u{1F512}', label: '安全中心' },
      { to: 'alert', icon: '\u{1F514}', label: '告警中心' },
      { to: 'self-healing', icon: '\u{1FA7A}', label: '异常自愈' },
      { to: 'emergency', icon: '\u{1F6A8}', label: '急救面板' },
      { to: 'security-scan', icon: '\u{1F6E1}', label: '安全扫描' },
    ]
  },
  {
    id: 'mall', icon: '\u{1F3EC}', label: '商城运营', x: 0, y: 0, dragging: false,
    items: [
      { to: 'ai-brain', icon: '\u{1F9E0}', label: '商城大脑' },
      { to: 'mall', icon: '\u{1F3EC}', label: '商城管理' },
      { to: 'customer', icon: '\u{1F4AC}', label: '客服系统' },
      { to: 'ecommerce-ai', icon: '\u{1F916}', label: 'AI电商引擎' },
      { to: 'image-process', icon: '\u{1F5BC}', label: '商品图处理' },
      { to: 'multilang', icon: '\u{1F30D}', label: '多语言发布' },
      { to: 'batch-upload', icon: '\u{1F4CB}', label: '批量上架' },
      { to: 'auto-reply', icon: '\u{1F916}', label: '自动回复' },
      { to: 'order-alert', icon: '\u{1F514}', label: '订单预警' },
      { to: 'content-factory', icon: '\u{1F3ED}', label: 'AI内容工厂' },
      { to: 'code-deploy', icon: '\u{26A1}', label: 'AI代码部署' },
      { to: 'files', icon: '\u{1F4C1}', label: '文件管理' },
      { to: 'plugins', icon: '\u{1F9E9}', label: '插件系统' },
    ]
  },
  {
    id: 'admin', icon: '\u{1F6E0}', label: '平台管理', x: 0, y: 0, dragging: false,
    items: [
      { to: 'approval', icon: '\u{2705}', label: '审批中心' },
      { to: 'audit', icon: '\u{1F4CB}', label: '审计日志' },
      { to: 'key-manager', icon: '\u{1F511}', label: 'API Key管理' },
      { to: 'user-manager', icon: '\u{1F465}', label: '用户管理' },
      { to: 'phone', icon: '\u{1F4DE}', label: 'AI电话助理' },
      { to: 'wechat-config', icon: '\u{1F4F1}', label: '微信管理' },
      { to: 'tasks', icon: '\u{1F4CB}', label: '任务中心' },
      { to: 'self-service', icon: '\u{1F527}', label: '自助服务' },
    ]
  }
])

function initPositions() {
  const isMobile = window.innerWidth <= 768
  if (isMobile) {
    const orbSize = 48
    const gap = 6
    const totalWidth = 5 * orbSize + 4 * gap
    const startX = Math.max(4, (window.innerWidth - totalWidth) / 2)
    categories.forEach((cat, i) => {
      cat.x = startX + i * (orbSize + gap)
      cat.y = 12
    })
  } else {
    const spacing = 90
    const startY = Math.max(80, (window.innerHeight - spacing * 4) / 2)
    categories.forEach((cat, i) => {
      cat.x = window.innerWidth - 76
      cat.y = startY + i * spacing
    })
  }
}
initPositions()

let floatTimers = []

function startFloat() {
  const amp = 14, period = 6000
  categories.forEach((cat, i) => {
    cat._baseX = cat.x
    cat._baseY = cat.y
    const tid = setInterval(() => {
      if (cat.dragging || activeCat.value === cat.id) return
      const t = Date.now() / period + i * 1.5
      cat.x = cat._baseX + Math.sin(t) * amp * 0.5
      cat.y = cat._baseY + Math.cos(t * 1.3) * amp * 0.6
    }, 50)
    floatTimers.push(tid)
  })
}
function startFloating() {
  floatTimers.forEach(clearInterval)
  floatTimers = []
  categories.forEach(c => { c._baseX = c.x; c._baseY = c.y })
  startFloat()
}
startFloating()

if (typeof window !== 'undefined') {
  window.addEventListener('resize', () => {
    initPositions()
    floatTimers.forEach(clearInterval)
    setTimeout(startFloating, 200)
  })
}

const activeCategory = computed(() => categories.find(c => c.id === activeCat.value))

const panelStyle = computed(() => {
  const cat = activeCategory.value
  if (!cat) return {}
  const panelW = 220, panelH = Math.min(cat.items.length * 46 + 80, 500)
  let left = cat.x - panelW - 24
  if (left < 10) left = cat.x + 80
  let top = cat.y
  if (top + panelH > window.innerHeight - 20) top = window.innerHeight - panelH - 20
  return { left: left + 'px', top: top + 'px' }
})

let isDragging = false
let dragStartX = 0, dragStartY = 0, btnStartX = 0, btnStartY = 0

function startDrag(e, cat) {
  if (e.target.closest('.panel-item') || e.target.closest('.panel-close')) return
  e.preventDefault()
  isDragging = false
  cat.dragging = true
  btnStartX = cat.x
  btnStartY = cat.y
  dragStartX = e.touches ? e.touches[0].clientX : e.clientX
  dragStartY = e.touches ? e.touches[0].clientY : e.clientY
  const onMove = (ev) => {
    const cx = ev.touches ? ev.touches[0].clientX : ev.clientX
    const cy = ev.touches ? ev.touches[0].clientY : ev.clientY
    const dx = cx - dragStartX, dy = cy - dragStartY
    if (Math.abs(dx) > 4 || Math.abs(dy) > 4) isDragging = true
    if (isDragging) {
      cat.x = Math.max(10, Math.min(window.innerWidth - 70, btnStartX + dx))
      cat.y = Math.max(10, Math.min(window.innerHeight - 70, btnStartY + dy))
      cat._baseX = cat.x; cat._baseY = cat.y
    }
  }
  const onEnd = () => {
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onEnd)
    document.removeEventListener('touchmove', onMove)
    document.removeEventListener('touchend', onEnd)
    setTimeout(() => { cat.dragging = false; isDragging = false }, 100)
  }
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onEnd)
  document.addEventListener('touchmove', onMove, { passive: true })
  document.addEventListener('touchend', onEnd)
}

function toggleCat(cat) {
  if (isDragging) return
  activeCat.value = activeCat.value === cat.id ? null : cat.id
}

function handleAction(action) {
  activeCat.value = null
  if (action === 'openChat') {
    window.dispatchEvent(new CustomEvent('floating:openChat'))
  }
}

function particleStyle(i) {
  const angle = (i / 8) * Math.PI * 2
  return { '--angle': angle + 'rad', '--delay': (i * 0.15) + 's' }
}
</script>

<style scoped>
.floating-nav-container {
  position: fixed;
  inset: 0;
  z-index: 9998;
  pointer-events: none;
}

/* ===== 全息导航球 ===== */
.nav-orb {
  position: absolute;
  pointer-events: all;
  width: 64px;
  height: 64px;
  cursor: pointer;
  z-index: 9998;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.nav-orb:hover { transform: scale(1.12); z-index: 9999; }
.nav-orb.active { z-index: 9999; }

/* 光晕 */
.orb-glow {
  position: absolute;
  inset: -12px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(102,126,234,0.2), transparent 70%);
  opacity: 0;
  transition: opacity 0.4s;
}
.nav-orb:hover .orb-glow { opacity: 1; }
.nav-orb.active .orb-glow {
  opacity: 1;
  background: radial-gradient(circle, rgba(102,126,234,0.4), transparent 70%);
  animation: glowPulse 2s ease-in-out infinite;
}

.orb-glow-inner {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(102,126,234,0.1), transparent 60%);
  opacity: 0;
  transition: opacity 0.3s;
}
.nav-orb.active .orb-glow-inner { opacity: 1; }

@keyframes glowPulse {
  0%, 100% { transform: scale(1); opacity: 0.4; }
  50% { transform: scale(1.15); opacity: 0.8; }
}

/* 旋转环 */
.orb-ring {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid rgba(102,126,234,0.2);
  animation: ringSpin 6s linear infinite;
}
.orb-ring.r1 { inset: -4px; }
.orb-ring.r2 { inset: -10px; border-color: rgba(118,75,162,0.15); animation-duration: 10s; animation-direction: reverse; }
.orb-ring.r3 { inset: -16px; border-color: rgba(102,126,234,0.1); animation-duration: 14s; }
.nav-orb.active .orb-ring { border-color: rgba(102,126,234,0.4); }
.nav-orb.active .orb-ring.r2 { border-color: rgba(118,75,162,0.3); }
.nav-orb.active .orb-ring.r3 { border-color: rgba(102,126,234,0.2); }
.nav-orb:hover .orb-ring { border-color: rgba(102,126,234,0.5); animation-duration: 3s; }

@keyframes ringSpin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 核心 */
.orb-core {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(10, 12, 30, 0.92);
  border: 1px solid rgba(102,126,234,0.3);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
  z-index: 1;
  overflow: hidden;
  transition: all 0.3s;
}
.nav-orb.active .orb-core {
  border-color: rgba(102,126,234,0.7);
  box-shadow: 0 0 30px rgba(102,126,234,0.3), inset 0 0 20px rgba(102,126,234,0.05);
}
.nav-orb:hover .orb-core {
  border-color: rgba(102,126,234,0.6);
}

.orb-core-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 35% 35%, rgba(102,126,234,0.1), transparent);
  animation: coreRotate 4s linear infinite;
  pointer-events: none;
}
@keyframes coreRotate {
  0% { transform: rotate(0deg) scale(1.5); }
  100% { transform: rotate(360deg) scale(1.5); }
}

.orb-icon { font-size: 20px; line-height: 1; position: relative; z-index: 1; }
.orb-label { font-size: 8px; color: rgba(255,255,255,0.5); margin-top: 2px; letter-spacing: 1.5px; max-width: 54px; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; position: relative; z-index: 1; }
.nav-orb.active .orb-label { color: rgba(255,255,255,0.8); }

/* 粒子 */
.orb-particles {
  position: absolute;
  inset: -18px;
  pointer-events: none;
  z-index: 0;
}
.orb-particle {
  position: absolute;
  width: 2px;
  height: 2px;
  background: #667eea;
  border-radius: 50%;
  left: 50%;
  top: 50%;
  animation: particleOrbit 4s linear infinite;
  animation-delay: var(--delay);
  transform: rotate(var(--angle)) translateX(42px);
  opacity: 0.5;
}
.nav-orb.active .orb-particle {
  animation-duration: 2s;
  opacity: 0.8;
}
@keyframes particleOrbit {
  from { transform: rotate(var(--angle)) translateX(42px); }
  to { transform: rotate(calc(var(--angle) + 6.283rad)) translateX(42px); }
}

/* 扫描线 */
.orb-scanline {
  position: absolute;
  inset: -2px;
  border-radius: 50%;
  background: linear-gradient(180deg, transparent, rgba(102,126,234,0.1), transparent);
  animation: scanRotate 3s linear infinite;
  pointer-events: none;
  opacity: 0;
  z-index: 0;
}
.nav-orb.active .orb-scanline { opacity: 1; }
@keyframes scanRotate {
  0% { transform: rotate(0deg); opacity: 0; }
  20% { opacity: 0.6; }
  80% { opacity: 0.6; }
  100% { transform: rotate(360deg); opacity: 0; }
}

.nav-orb.dragging { cursor: grabbing; }
.nav-orb.dragging .orb-core { border-color: rgba(102,126,234,1); box-shadow: 0 0 40px rgba(102,126,234,0.5); }

/* ===== 全息分类面板 ===== */
.category-panel {
  position: fixed;
  width: 220px;
  max-height: 500px;
  background: rgba(8, 10, 26, 0.96);
  border: 1px solid rgba(102,126,234,0.3);
  border-radius: 14px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 8px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(102,126,234,0.05);
  z-index: 9999;
  overflow: hidden;
  pointer-events: all;
}
.category-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 14px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(102,126,234,0.3), transparent 50%, rgba(102,126,234,0.15));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.panel-scanline {
  position: absolute;
  left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(102,126,234,0.15), transparent);
  animation: panelScan 3s linear infinite;
  pointer-events: none;
  z-index: 1;
}
@keyframes panelScan {
  0% { top: 0; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(102,126,234,0.15);
  position: relative;
}

.ph-icon-wrap {
  width: 28px; height: 28px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  position: relative;
  background: rgba(102,126,234,0.1);
}
.ph-icon-glow {
  position: absolute; inset: -4px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(102,126,234,0.2), transparent 70%);
  animation: phGlow 2s ease-in-out infinite;
}
@keyframes phGlow {
  0%, 100% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.3); opacity: 0.6; }
}
.ph-icon { font-size: 14px; position: relative; z-index: 1; }
.ph-title { font-size: 14px; font-weight: 600; color: #e0e0ff; flex: 1; letter-spacing: 1px; }
.ph-close {
  width: 24px; height: 24px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: rgba(255,255,255,0.3);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.ph-close:hover { background: rgba(255,77,79,0.15); color: #ff4d4f; }

.panel-body {
  padding: 6px;
  overflow-y: auto;
  max-height: 410px;
}
.panel-body::-webkit-scrollbar { width: 3px; }
.panel-body::-webkit-scrollbar-track { background: transparent; }
.panel-body::-webkit-scrollbar-thumb { background: rgba(102,126,234,0.2); border-radius: 2px; }

.panel-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  color: rgba(255,255,255,0.6);
  text-decoration: none;
  font-size: 12px;
  transition: all 0.2s;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
.panel-item:hover {
  background: rgba(102,126,234,0.1);
  color: #fff;
  padding-left: 16px;
}
.panel-item:active { transform: scale(0.98); }

.pi-glow {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, #667eea, #764ba2);
  transform: scaleY(0);
  transition: transform 0.2s;
  border-radius: 0 2px 2px 0;
}
.panel-item:hover .pi-glow { transform: scaleY(1); }

.pi-icon { font-size: 14px; width: 20px; text-align: center; flex-shrink: 0; }
.pi-label { flex: 1; }
.pi-arrow {
  font-size: 10px;
  opacity: 0;
  transform: translateX(-5px);
  transition: all 0.2s;
}
.panel-item:hover .pi-arrow { opacity: 0.5; transform: translateX(0); }

/* ===== 面板动画 ===== */
.panel-fade-enter-active { transition: opacity 0.25s, transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1); }
.panel-fade-leave-active { transition: opacity 0.15s, transform 0.15s; }
.panel-fade-enter-from { opacity: 0; transform: scale(0.85) translateY(5px); }
.panel-fade-leave-to { opacity: 0; transform: scale(0.85); }

/* ===== 移动端 ===== */
@media (max-width: 768px) {
  .nav-orb { width: 48px; height: 48px; }
  .orb-icon { font-size: 16px; }
  .orb-label { font-size: 7px; max-width: 44px; letter-spacing: 1px; }
  .orb-ring.r2 { inset: -8px; }
  .orb-ring.r3 { inset: -12px; }
  .orb-particle { transform: rotate(var(--angle)) translateX(30px); }
  .category-panel { width: 200px; max-height: 60vh; }
}
</style>
