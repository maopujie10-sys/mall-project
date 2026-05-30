<template>
  <div class="floating-nav-container">
    <!-- 4\u4E2A\u5206\u7C7B\u5149\u7403 -->
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

    <!-- \u5F39\u51FA\u83DC\u5355\u9762\u677F -->
    <transition name="panel-fade">
      <div v-if="activeCat" class="category-panel" :style="panelStyle">
        <div class="panel-header">
          <span class="panel-icon">{{ activeCategory?.icon }}</span>
          <span class="panel-title">{{ activeCategory?.label }}</span>
          <button class="panel-close" @click="activeCat = null">\u00D7</button>
        </div>
        <div class="panel-body">
          <router-link
            v-for="item in activeCategory?.items"
            :key="item.to + item.label"
            :to="item.to ? { name: item.to } : ''"
            class="panel-item"
            @click="item.action ? handleAction(item.action) : (activeCat = null)"
          >
            <span class="item-icon">{{ item.icon }}</span>
            <span class="item-label">{{ item.label }}</span>
          </router-link>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeCat = ref(null)

const categories = reactive([
  {
    id: 'core', icon: '\u{1F9E0}', label: 'AI\u6838\u5FC3', x: 0, y: 0, dragging: false,
    items: [
      { to: 'friday', icon: '\u{1F9E0}', label: 'Friday \u5927\u8111' },
      { to: '', icon: '\u{1F4AC}', label: 'AI \u5BF9\u8BDD', action: 'openChat' },
      { to: 'ai-brain', icon: '\u{1F9E0}', label: 'AI \u5927\u8111' },
      { to: 'agents', icon: '\u{1F916}', label: 'Agent \u5217\u8868' },
      { to: 'models', icon: '\u{1F52C}', label: '\u6A21\u578B\u4E2D\u5FC3' },
      { to: 'memory', icon: '\u{1F4BE}', label: '\u8BB0\u5FC6\u4E2D\u5FC3' },
      { to: 'evolution', icon: '\u{1F331}', label: '\u8FDB\u5316\u62A5\u544A' },
      { to: 'knowledge', icon: '\u{1F4DA}', label: '\u77E5\u8BC6\u4E2D\u5FC3' },
      { to: 'memory-sync', icon: '\u{1F504}', label: '\u8DE8\u5E73\u53F0\u8BB0\u5FC6' },
      { to: 'voice-chat', icon: '\u{1F399}', label: '\u8BED\u97F3\u5BF9\u8BDD' },
      { to: 'video', icon: '\u{1F3AC}', label: '\u89C6\u9891\u5206\u6790' },
      { to: 'ocr', icon: '\u{1F50D}', label: 'OCR \u8BC6\u522B' },
      { to: 'agent-collab', icon: '\u{1F91D}', label: 'Agent \u534F\u4F5C' },
      { to: 'skill-market', icon: '\u{1F9E9}', label: '\u6280\u80FD\u5E02\u573A' },
      { to: 'capabilities', icon: '\u{1F527}', label: 'AI\u80FD\u529B\u72B6\u6001' },
      { to: 'advanced-ai', icon: '\u{1F680}', label: '\u9AD8\u7EA7AI' },
      { to: 'ai-tools', icon: '\u{1F527}', label: 'AI\u5DE5\u5177\u7BB1' },
      { to: 'workflow', icon: '\u{1F3AF}', label: '\u5DE5\u4F5C\u6D41\u7F16\u8F91\u5668' },
    ]
  },
  {
    id: 'data', icon: '\u{1F4CA}', label: '\u6570\u636E\u76D1\u63A7', x: 0, y: 0, dragging: false,
    items: [
      { to: 'dashboard', icon: '\u{1F4CA}', label: '\u6570\u636E\u603B\u89C8' },
      { to: 'trends', icon: '\u{1F4C8}', label: '\u8D8B\u52BF\u76D1\u63A7' },
      { to: 'scraper', icon: '\u{1F577}', label: '\u91C7\u96C6\u4E2D\u5FC3' },
      { to: 'database', icon: '\u{1F5C4}', label: '\u6570\u636E\u5E93' },
      { to: 'log-viewer', icon: '\u{1F4CB}', label: '\u65E5\u5FD7\u4E2D\u5FC3' },
      { to: 'weekly-report', icon: '\u{1F4CA}', label: '\u8FD0\u8425\u5468\u62A5' },
      { to: 'text2sql', icon: '\u{1F5C4}', label: '\u81EA\u7136\u8BED\u8A00\u67E5\u5E93' },
      { to: 'competitor', icon: '\u{1F575}', label: '\u7ADE\u54C1\u76D1\u63A7' },
      { to: 'customer-profile', icon: '\u{1F465}', label: '\u5BA2\u6237\u753B\u50CF' },
      { to: 'predict', icon: '\u{1F4C8}', label: '\u9884\u6D4B\u5206\u6790' },
      { to: 'recommend', icon: '\u{1F3AF}', label: '\u63A8\u8350\u5F15\u64CE' },
      { to: 'ab-test', icon: '\u{1F9EA}', label: 'A/B\u6D4B\u8BD5' },
      { to: 'virtual', icon: '\u{1F3AE}', label: '\u865A\u62DF\u6570\u636E' },
    ]
  },
  {
    id: 'ops', icon: '\u{1F6E1}', label: '\u5B89\u5168\u8FD0\u7EF4', x: 0, y: 0, dragging: false,
    items: [
      { to: 'server', icon: '\u{1F5A5}', label: '\u670D\u52A1\u5668' },
      { to: 'docker', icon: '\u{1F433}', label: 'Docker' },
      { to: 'nginx', icon: '\u{1F527}', label: 'Nginx' },
      { to: 'network', icon: '\u{1F310}', label: '\u7F51\u7EDC\u5DE5\u5177' },
      { to: 'github', icon: '\u{1F419}', label: 'GitHub MCP' },
      { to: 'rotation', icon: '\u{1F504}', label: '\u57DF\u540D\u8F6E\u503C' },
      { to: 'site', icon: '\u{1F310}', label: '\u7AD9\u70B9\u68C0\u6D4B' },
      { to: 'rollback', icon: '\u23EA', label: '\u5907\u4EFD\u56DE\u6EDA' },
      { to: 'security', icon: '\u{1F512}', label: '\u5B89\u5168\u4E2D\u5FC3' },
      { to: 'alert', icon: '\u{1F514}', label: '\u544A\u8B66\u4E2D\u5FC3' },
      { to: 'self-healing', icon: '\u{1FA7A}', label: '\u5F02\u5E38\u81EA\u6108' },
      { to: 'emergency', icon: '\u{1F6A8}', label: '\u6025\u6551\u9762\u677F' },
      { to: 'security-scan', icon: '\u{1F6E1}', label: '\u5B89\u5168\u626B\u63CF' },
      { to: 'approval', icon: '\u2705', label: '\u5BA1\u6279\u4E2D\u5FC3' },
      { to: 'audit', icon: '\u{1F4CB}', label: '\u5BA1\u8BA1\u65E5\u5FD7' },
      { to: 'key-manager', icon: '\u{1F511}', label: 'API Key\u7BA1\u7406' },
      { to: 'user-manager', icon: '\u{1F465}', label: '\u7528\u6237\u7BA1\u7406' },
      { to: 'phone', icon: '\u{1F4DE}', label: 'AI\u7535\u8BDD\u52A9\u7406' },
      { to: 'wechat-config', icon: '\u{1F4F1}', label: '\u5FAE\u4FE1\u7BA1\u7406' },
      { to: 'tasks', icon: '\u{1F4CB}', label: '\u4EFB\u52A1\u4E2D\u5FC3' },
      { to: 'self-service', icon: '\u{1F527}', label: '\u81EA\u52A9\u670D\u52A1' },
    ]
  },
  {
    id: 'mall', icon: '\u{1F3EC}', label: '\u5546\u57CE\u8FD0\u8425', x: 0, y: 0, dragging: false,
    items: [
      { to: 'mall', icon: '\u{1F3EC}', label: '\u5546\u57CE\u7BA1\u7406' },
      { to: 'customer', icon: '\u{1F4AC}', label: '\u5BA2\u670D\u7CFB\u7EDF' },
      { to: 'ecommerce-ai', icon: '\u{1F916}', label: 'AI\u7535\u5546\u5F15\u64CE' },
      { to: 'image-process', icon: '\u{1F5BC}', label: '\u5546\u54C1\u56FE\u5904\u7406' },
      { to: 'multilang', icon: '\u{1F30D}', label: '\u591A\u8BED\u8A00\u53D1\u5E03' },
      { to: 'batch-upload', icon: '\u{1F4CB}', label: '\u6279\u91CF\u4E0A\u67B6' },
      { to: 'auto-reply', icon: '\u{1F916}', label: '\u81EA\u52A8\u56DE\u590D' },
      { to: 'order-alert', icon: '\u{1F514}', label: '\u8BA2\u5355\u9884\u8B66' },
      { to: 'content-factory', icon: '\u{1F3ED}', label: 'AI\u5185\u5BB9\u5DE5\u5382' },
      { to: 'code-deploy', icon: '\u26A1', label: 'AI\u4EE3\u7801\u90E8\u7F72' },
      { to: 'files', icon: '\u{1F4C1}', label: '\u6587\u4EF6\u7BA1\u7406' },
      { to: 'plugins', icon: '\u{1F9E9}', label: '\u63D2\u4EF6\u7CFB\u7EDF' },
    ]
  }
])

// 初始化位置 — 垂直排列在右侧
function initPositions() {
  const isMobile = window.innerWidth <= 768
  if (isMobile) {
    // 移动端：顶部水平排列
    const orbSize = 52
    const gap = 10
    const totalWidth = 4 * orbSize + 3 * gap
    const startX = Math.max(8, (window.innerWidth - totalWidth) / 2)
    categories.forEach((cat, i) => {
      cat.x = startX + i * (orbSize + gap)
      cat.y = 16
    })
  } else {
    // PC端：右侧垂直排列
    const spacing = 100
    const startY = Math.max(80, (window.innerHeight - spacing * 3) / 2)
    categories.forEach((cat, i) => {
      cat.x = window.innerWidth - 80
      cat.y = startY + i * spacing
    })
  }
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
  if (Math.abs(cx - dragStartX) > 8 || Math.abs(cy - dragStartY) > 3) isDragging = true
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