<template>
  <div class="floating-nav-container">
    <!-- 4 个分类光球 -->
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
      <div class="orb-glow"></div>
      <div class="orb-ring ring-1"></div>
      <div class="orb-ring ring-2"></div>
      <div class="orb-core">
        <span class="orb-icon">{{ cat.icon }}</span>
        <span class="orb-label">{{ cat.label }}</span>
      </div>
      <div class="orb-particles">
        <span v-for="i in 6" :key="i" class="particle" :style="particleStyle(i)"></span>
      </div>
    </div>

    <!-- 弹出菜单面板 -->
    <transition name="panel-fade">
      <div v-if="activeCat" class="category-panel" :style="panelStyle">
        <div class="panel-header">
          <span class="panel-icon">{{ activeCategory?.icon }}</span>
          <span class="panel-title">{{ activeCategory?.label }}</span>
          <button class="panel-close" @click="activeCat = null">×</button>
        </div>
        <div class="panel-body">
          <router-link
            v-for="item in activeCategory?.items"
            :key="item.to"
            :to="item.to"
            class="panel-item"
            @click="activeCat = null"
          >
            <span class="item-icon">{{ item.icon }}</span>
            <span class="item-label">{{ item.label }}</span>
          </router-link>
        </div>
        <div class="panel-footer">
          <div class="footer-line"></div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

const activeCat = ref(null)

const categories = reactive([
  {
    id: 'ai', icon: '🧠', label: 'AI 智能', x: 0, y: 0, dragging: false,
    items: [
      { to: 'friday', icon: '🧠', label: 'Friday 大脑' },
      { to: '', icon: '💬', label: 'AI 对话', action: 'openChat' },
      { to: 'agents', icon: '🤖', label: 'Agent 调度' },
      { to: 'models', icon: '🔬', label: '模型中心' },
      { to: 'memory', icon: '💾', label: '记忆中心' },
      { to: 'trends', icon: '📈', label: 'AI 监控' },
      { to: 'video', icon: '🎬', label: '视觉分析' },
      { to: 'plugins', icon: '🧩', label: '技能市场' },
      { to: 'ai-brain', icon: '🧠', label: 'AI大脑' },
      { to: 'evolution', icon: '🌱', label: '进化报告' },
      { to: 'ocr', icon: '🔍', label: 'OCR识别' },
    ]
  },
  {
    id: 'mall', icon: '🏬', label: '商城运营', x: 0, y: 0, dragging: false,
    items: [
      { to: 'dashboard', icon: '📊', label: '运营总览' },
      { to: 'mall', icon: '🏬', label: '商城管理' },
      { to: 'customer', icon: '💬', label: '客服系统' },
      { to: 'image-process', icon: '🖼️', label: '商品图处理' },
      { to: 'multilang', icon: '🌍', label: '商品发布' },
      { to: 'order-alert', icon: '🔔', label: '订单预警' },
      { to: 'virtual', icon: '🎮', label: '虚拟数据' },
      { to: 'batch-upload', icon: '📋', label: '批量上架' },
      { to: 'auto-reply', icon: '🤖', label: '自动回复' },
    ]
  },
  {
    id: 'ops', icon: '🖥️', label: '运维监控', x: 0, y: 0, dragging: false,
    items: [
      { to: 'server', icon: '🖥️', label: '服务器' },
      { to: 'docker', icon: '🐳', label: 'Docker' },
      { to: 'network', icon: '🌐', label: '网络管理' },
      { to: 'github', icon: '🐙', label: 'GitHub MCP' },
      { to: 'rotation', icon: '🔄', label: '域名轮值' },
      { to: 'database', icon: '🗄️', label: '数据库' },
      { to: 'log-viewer', icon: '📋', label: '日志审计' },
      { to: 'scraper', icon: '🕷️', label: '采集中心' },
      { to: 'self-service', icon: '🔧', label: '自助服务' },
      { to: 'nginx', icon: '🔧', label: 'Nginx管理' },
      { to: 'tasks', icon: '📋', label: '任务中心' },
      { to: 'weekly-report', icon: '📊', label: '运营周报' },
      { to: 'files', icon: '📁', label: '文件管理' },
      { to: 'site', icon: '🌐', label: '站点检测' },
    ]
  },
  {
    id: 'security', icon: '🛡️', label: '安全告警', x: 0, y: 0, dragging: false,
    items: [
      { to: 'security', icon: '🔒', label: '安全中心' },
      { to: 'alert', icon: '🔔', label: '告警中心' },
      { to: 'self-healing', icon: '🩺', label: '异常自愈' },
      { to: 'emergency', icon: '🚨', label: '急救面板' },
      { to: 'phone', icon: '📞', label: 'AI 电话' },
      { to: 'rollback', icon: '⏪', label: '备份回滚' },
      { to: 'approval', icon: '✅', label: '审批中心' },
      { to: 'audit', icon: '📋', label: '审计日志' },
    ]
  }
])

// 初始化位置 — 垂直排列在右侧
function initPositions() {
  const spacing = 100
  const startY = Math.max(80, (window.innerHeight - spacing * 3) / 2)
  categories.forEach((cat, i) => {
    cat.x = window.innerWidth - 80
    cat.y = startY + i * spacing
  })
}
initPositions()
startFloating()
if (typeof window !== 'undefined') {
  window.addEventListener('resize', () => { initPositions(); floatTimers.forEach(clearInterval); setTimeout(startFloating, 200) })
}

const activeCategory = computed(() => categories.find(c => c.id === activeCat.value))

const panelStyle = computed(() => {
  const cat = activeCategory.value
  if (!cat) return {}
  const panelW = 220, panelH = Math.min(cat.items.length * 44 + 80, 500)
  let left = cat.x - panelW - 20
  let top = cat.y - panelH / 2
  if (left < 10) left = cat.x + 80
  if (top < 10) top = 10
  if (top + panelH > window.innerHeight - 10) top = window.innerHeight - panelH - 10
  return { left: left + 'px', top: top + 'px' }
})

// 拖拽
let dragTarget = null, dragStartX = 0, dragStartY = 0, orbStartX = 0, orbStartY = 0, isDragging = false

function startDrag(e, cat) {
  if (e.target.closest('.panel-item')) return
  isDragging = false
  dragTarget = cat
  dragStartX = e.touches ? e.touches[0].clientX : e.clientX
  dragStartY = e.touches ? e.touches[0].clientY : e.clientY
  orbStartX = cat.x
  orbStartY = cat.y
  cat.dragging = true
  document.onmousemove = onDragMove
  document.onmouseup = onDragUp
  document.ontouchmove = onDragMove
  document.ontouchend = onDragUp
}
function onDragMove(ev) {
  if (!dragTarget) return
  const cx = ev.touches ? ev.touches[0].clientX : ev.clientX
  const cy = ev.touches ? ev.touches[0].clientY : ev.clientY
  if (Math.abs(cx - dragStartX) > 3 || Math.abs(cy - dragStartY) > 3) isDragging = true
  if (isDragging) {
    dragTarget.x = Math.max(40, Math.min(window.innerWidth - 80, orbStartX + cx - dragStartX))
    dragTarget.y = Math.max(40, Math.min(window.innerHeight - 80, orbStartY + cy - dragStartY))
  }
}
function onDragUp() {
  if (dragTarget) dragTarget.dragging = false
  dragTarget = null
  document.onmousemove = null
  document.onmouseup = null
  document.ontouchmove = null
  document.ontouchend = null
}


// ===== 自动漂浮动画 =====
let floatTimers = []
function startFloating() {
  floatTimers.forEach(clearInterval)
  floatTimers = []
  categories.forEach((cat, i) => {
    const baseX = cat.x, baseY = cat.y
    const phase = i * Math.PI / 2
    const speed = 0.3 + i * 0.1
    const range = 20 + i * 8
    floatTimers.push(setInterval(() => {
      if (cat.dragging) return
      const t = Date.now() / 1000
      cat.x = baseX + Math.sin(t * speed + phase) * range
      cat.y = baseY + Math.cos(t * speed * 0.7 + phase) * range * 0.6
    }, 50))
  })
}
startFloating()
window.addEventListener('resize', () => { initPositions(); startFloating() })

function handleAction(item) {
  if (item.action === 'openChat') {
    window.dispatchEvent(new CustomEvent('floating:openChat'))
  }
}
function toggleCat(cat) {
  if (isDragging) return
  activeCat.value = activeCat.value === cat.id ? null : cat.id
}

function particleStyle(i) {
  const angle = (i / 6) * 360
  return {
    '--angle': angle + 'deg',
    '--delay': (i * 0.3) + 's'
  }
}
</script>

<style scoped>
.floating-nav-container {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 1000;
}
.nav-orb {
  position: fixed;
  width: 64px; height: 64px;
  border-radius: 50%;
  cursor: pointer;
  pointer-events: all;
  transition: transform 0.3s, box-shadow 0.3s;
  z-index: 1001;
}
.nav-orb:hover { transform: scale(1.15); }
.nav-orb.dragging { transition: none; cursor: grabbing; }
.orb-glow {
  position: absolute; inset: -8px; border-radius: 50%;
  background: radial-gradient(circle, rgba(102,126,234,0.4) 0%, transparent 70%);
  animation: glowPulse 2s ease-in-out infinite;
}
.orb-ring {
  position: absolute; inset: -4px; border-radius: 50%;
  border: 2px solid rgba(102,126,234,0.3);
  animation: ringSpin 8s linear infinite;
}
.ring-2 { inset: -8px; border-color: rgba(118,75,162,0.2); animation-duration: 12s; animation-direction: reverse; }
.orb-core {
  position: absolute; inset: 4px; border-radius: 50%;
  background: linear-gradient(135deg, rgba(15,15,30,0.95), rgba(20,20,50,0.9));
  backdrop-filter: blur(10px);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  border: 1px solid rgba(102,126,234,0.5);
  overflow: hidden;
}
.orb-icon { font-size: 22px; line-height: 1; }
.orb-label { font-size: 9px; color: rgba(255,255,255,0.7); margin-top: 1px; letter-spacing: 1px; }
.orb-particles { position: absolute; inset: -12px; pointer-events: none; }
.particle {
  position: absolute; width: 3px; height: 3px; border-radius: 50%;
  background: rgba(102,126,234,0.6);
  top: 50%; left: 50%;
  animation: particleOrbit 3s linear infinite;
  animation-delay: var(--delay);
  transform: rotate(var(--angle)) translateY(-36px);
}

/* 弹出面板 */
.category-panel {
  position: fixed;
  width: 220px;
  background: rgba(15,15,35,0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(102,126,234,0.3);
  border-radius: 16px;
  overflow: hidden;
  pointer-events: all;
  box-shadow: 0 0 40px rgba(102,126,234,0.2), 0 8px 32px rgba(0,0,0,0.5);
  z-index: 1002;
}
.panel-header {
  display: flex; align-items: center; gap: 8px;
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2));
  border-bottom: 1px solid rgba(102,126,234,0.2);
}
.panel-icon { font-size: 20px; }
.panel-title { font-size: 15px; font-weight: 600; color: #e0e0ff; flex: 1; }
.panel-close {
  width: 28px; height: 28px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.2);
  background: transparent; color: rgba(255,255,255,0.6); cursor: pointer; font-size: 16px;
  display: flex; align-items: center; justify-content: center;
}
.panel-close:hover { background: rgba(255,255,255,0.1); color: #fff; }
.panel-body { padding: 8px; max-height: 420px; overflow-y: auto; }
.panel-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 10px; text-decoration: none;
  color: rgba(255,255,255,0.8); transition: all 0.2s;
  font-size: 13px;
}
.panel-item:hover { background: rgba(102,126,234,0.2); color: #fff; }
.panel-item.router-link-active { background: rgba(102,126,234,0.3); color: #fff; }
.item-icon { font-size: 16px; width: 24px; text-align: center; }
.item-label { flex: 1; }
.panel-footer { padding: 8px 16px; }
.footer-line { height: 1px; background: linear-gradient(90deg, transparent, rgba(102,126,234,0.3), transparent); }

/* 动画 */
.panel-fade-enter-active { transition: all 0.25s ease-out; }
.panel-fade-leave-active { transition: all 0.15s ease-in; }
.panel-fade-enter-from { opacity: 0; transform: scale(0.9) translateX(10px); }
.panel-fade-leave-to { opacity: 0; transform: scale(0.9) translateX(10px); }

@keyframes glowPulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.7; }
}
@keyframes ringSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes particleOrbit {
  from { transform: rotate(var(--angle)) translateY(-36px) scale(1); }
  50% { transform: rotate(var(--angle)) translateY(-36px) scale(0.3); opacity: 0.3; }
  to { transform: rotate(calc(var(--angle) + 360deg)) translateY(-36px) scale(1); opacity: 1; }
}

@media (max-width: 768px) {
  .nav-orb { width: 52px; height: 52px; }
  .orb-icon { font-size: 18px; }
  .orb-label { font-size: 8px; }
  .category-panel {
    position: fixed;
    left: 50% !important; transform: translateX(-50%);
    top: 70px !important; right: auto !important; bottom: auto !important;
    width: 92vw; max-width: 340px;
  }
}

.panel-action {
  width: 100%; border: none; background: transparent; cursor: pointer;
  font-family: inherit; text-align: left;
}</style>