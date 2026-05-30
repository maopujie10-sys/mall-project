<template>
  <div class="floating-nav-container">
    <!-- 5 -->
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
      <div class="orb-glow">{{ $t('floatingNav.title') }}</div>
      <div class="orb-ring ring-1">{{ $t('floatingNav.title') }}</div>
      <div class="orb-ring ring-2">{{ $t('floatingNav.title') }}</div>
      <div class="orb-core">
        <span class="orb-icon">{{ cat.icon }}</span>
        <span class="orb-label">{{ cat.label }}</span>
      </div>
      <div class="orb-particles">
        -
      </div>
    </div>

    
    <transition name="panel-fade">
      <div v-if="activeCat" class="category-panel" :style="panelStyle">
        <div class="panel-header">
          <span class="panel-icon">{{ activeCategory?.icon }}</span>
          <span class="panel-title">{{ activeCategory?.label }}</span>
          <button class="panel-close" @click="activeCat = null">x</button>
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
      { to: '', icon: '\u{1F4AC}', label: 'AI \u5BF9\u8BDD', action: 'openChat' },      { to: 'agents', icon: '\u{1F916}', label: 'Agent \u5217\u8868' },
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
    ]
  },
  {
    id: 'mall', icon: '\u{1F3EC}', label: '\u5546\u57CE\u8FD0\u8425', x: 0, y: 0, dragging: false,
    items: [
      { to: 'ai-brain', icon: '\u{1F9E0}', label: '\u5546\u57CE\u5927\u8111' },
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
  },
  {
    id: 'admin', icon: '\u{1F6E0}', label: '\u5E73\u53F0\u7BA1\u7406', x: 0, y: 0, dragging: false,
    items: [
      { to: 'approval', icon: '\u2705', label: '\u5BA1\u6279\u4E2D\u5FC3' },
      { to: 'audit', icon: '\u{1F4CB}', label: '\u5BA1\u8BA1\u65E5\u5FD7' },
      { to: 'key-manager', icon: '\u{1F511}', label: 'API Key\u7BA1\u7406' },
      { to: 'user-manager', icon: '\u{1F465}', label: '\u7528\u6237\u7BA1\u7406' },
      { to: 'phone', icon: '\u{1F4DE}', label: 'AI\u7535\u8BDD\u52A9\u7406' },
      { to: 'wechat-config', icon: '\u{1F4F1}', label: '\u5FAE\u4FE1\u7BA1\u7406' },
      { to: 'tasks', icon: '\u{1F4CB}', label: '\u4EFB\u52A1\u4E2D\u5FC3' },
      { to: 'self-service', icon: '\u{1F527}', label: '\u81EA\u52A9\u670D\u52A1' },
    ]
  }
])

let isDragging = false
let dragStartX = 0, dragStartY = 0, btnStartX = 0, btnStartY = 0
let floatTimers = []

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
    // PC5
    const spacing = 88
    const startY = Math.max(60, (window.innerHeight - spacing * 4) / 2)
    categories.forEach((cat, i) => {
      cat.x = window.innerWidth - 76
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
  if (left < 10) left = cat.x + 80
  let top = cat.y
  if (top + panelH > window.innerHeight - 20) top = window.innerHeight - panelH - 20
  return { left: left + 'px', top: top + 'px' }
})

function startFloat() {
  const amp = 12, period = 8000
  categories.forEach((cat, i) => {
    const phase = i * 1.2
    cat._baseX = cat.x; cat._baseY = cat.y
    const tid = setInterval(() => {
      if (cat.dragging || activeCat.value === cat.id) return
      const t = Date.now() / period + phase
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

function startDrag(e, cat) {
  if (e.target.closest('.panel-item') || e.target.closest('.panel-close')) return
  e.preventDefault()
  isDragging = false; cat.dragging = true
  btnStartX = cat.x; btnStartY = cat.y
  dragStartX = e.touches ? e.touches[0].clientX : e.clientX
  dragStartY = e.touches ? e.touches[0].clientY : e.clientY
  document.onmousemove = (ev) => {
    const cx = ev.clientX, cy = ev.clientY
    const dx = cx - dragStartX, dy = cy - dragStartY
    if (Math.abs(dx) > 4 || Math.abs(dy) > 4) isDragging = true
    if (isDragging) {
      cat.x = Math.max(10, Math.min(window.innerWidth - 70, btnStartX + dx))
      cat.y = Math.max(10, Math.min(window.innerHeight - 70, btnStartY + dy))
      cat._baseX = cat.x; cat._baseY = cat.y
    }
  }
  document.onmouseup = () => {
    document.onmousemove = null; document.onmouseup = null
    setTimeout(() => { cat.dragging = false; isDragging = false }, 100)
  }
  document.ontouchmove = (ev) => {
    const cx = ev.touches[0].clientX, cy = ev.touches[0].clientY
    const dx = cx - dragStartX, dy = cy - dragStartY
    if (Math.abs(dx) > 4 || Math.abs(dy) > 4) isDragging = true
    if (isDragging) {
      cat.x = Math.max(10, Math.min(window.innerWidth - 70, btnStartX + dx))
      cat.y = Math.max(10, Math.min(window.innerHeight - 70, btnStartY + dy))
      cat._baseX = cat.x; cat._baseY = cat.y
    }
  }
  document.ontouchend = () => {
    document.ontouchmove = null; document.ontouchend = null
    setTimeout(() => { cat.dragging = false; isDragging = false }, 100)
  }
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
  const angle = (i / 6) * Math.PI * 2
  return { '--angle': angle + 'rad', '--delay': (i * 0.3) + 's' }
}
</script>

<style scoped>
.floating-nav-container { position: fixed; inset: 0; z-index: 9998; pointer-events: none; }
.nav-orb { position: absolute; pointer-events: all; width: 62px; height: 62px; cursor: pointer; z-index: 9998; }
.orb-glow { position: absolute; inset: -8px; border-radius: 50%; background: radial-gradient(circle, rgba(102,126,234,0.3), transparent 70%); opacity: 0; transition: opacity 0.3s; }
.nav-orb:hover .orb-glow { opacity: 1; }
.nav-orb.active .orb-glow { opacity: 1; background: radial-gradient(circle, rgba(102,126,234,0.5), transparent 70%); }
.orb-ring { position: absolute; inset: -4px; border-radius: 50%; border: 1.5px solid rgba(102,126,234,0.25); animation: ringRotate 8s linear infinite; }
.ring-2 { inset: -10px; border-color: rgba(118,75,162,0.2); animation-duration: 12s; animation-direction: reverse; }
.orb-core { position: absolute; inset: 0; border-radius: 50%; background: rgba(13,16,37,0.9); border: 1px solid rgba(102,126,234,0.4); display: flex; flex-direction: column; align-items: center; justify-content: center; backdrop-filter: blur(8px); }
.nav-orb.active .orb-core { border-color: rgba(102,126,234,0.8); box-shadow: 0 0 24px rgba(102,126,234,0.4); }
.orb-icon { font-size: 20px; line-height: 1; }
.orb-label { font-size: 9px; color: rgba(255,255,255,0.6); margin-top: 1px; letter-spacing: 1px; max-width: 50px; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.orb-particles { position: absolute; inset: -14px; pointer-events: none; }
.particle { position: absolute; width: 3px; height: 3px; background: #667eea; border-radius: 50%; left: 50%; top: 50%; animation: particleOrbit 3s linear infinite; animation-delay: var(--delay); transform: rotate(var(--angle)) translateX(36px); opacity: 0.4; }
.nav-orb.dragging { cursor: grabbing; }
.nav-orb.dragging .orb-core { border-color: rgba(102,126,234,1); }

.category-panel { position: fixed; width: 220px; max-height: 500px; background: rgba(10,10,26,0.96); border: 1px solid rgba(102,126,234,0.35); border-radius: 12px; backdrop-filter: blur(20px); z-index: 9999; overflow: hidden; pointer-events: all; }
.panel-header { display: flex; align-items: center; gap: 8px; padding: 12px 14px; border-bottom: 1px solid rgba(102,126,234,0.2); }
.panel-icon { font-size: 18px; }
.panel-title { font-size: 14px; font-weight: 600; color: #e0e0ff; flex: 1; }
.panel-close { background: none; border: none; color: rgba(255,255,255,0.4); font-size: 18px; cursor: pointer; padding: 2px 6px; }
.panel-body { padding: 8px; overflow-y: auto; max-height: 430px; }
.panel-item { display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-radius: 8px; color: rgba(255,255,255,0.7); text-decoration: none; font-size: 12px; transition: all 0.15s; cursor: pointer; }
.panel-item:hover { background: rgba(102,126,234,0.12); color: #fff; }
.item-icon { font-size: 14px; width: 20px; text-align: center; }
.item-label { flex: 1; }

.panel-fade-enter-active { transition: opacity 0.2s, transform 0.2s; }
.panel-fade-leave-active { transition: opacity 0.1s, transform 0.1s; }
.panel-fade-enter-from { opacity: 0; transform: scale(0.9); }
.panel-fade-leave-to { opacity: 0; transform: scale(0.9); }

@keyframes ringRotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes particleOrbit { from { transform: rotate(var(--angle)) translateX(36px); } to { transform: rotate(calc(var(--angle) + 6.283rad)) translateX(36px); } }

@media (max-width: 768px) {
  .nav-orb { width: 48px; height: 48px; }
  .orb-icon { font-size: 16px; }
  .orb-label { font-size: 7px; max-width: 42px; }
  .category-panel { width: 200px; left: 10px !important; right: 10px !important; }
}
</style>