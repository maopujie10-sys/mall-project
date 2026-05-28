<template>
  <div class="friday-brain" ref="container">
    <canvas ref="canvas" class="brain-canvas"></canvas>
    
    <!-- 覆盖层：信息面板 -->
    <div class="fallback-ui" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:5;background:radial-gradient(ellipse at center,#0d1025,#080b1a)">
    <h2 style="color:#fff;font-size:22px;margin:16px 0 4px;font-weight:600">Friday AI OS v3.0</h2>
    <p style="color:rgba(255,255,255,0.45);font-size:13px;margin-bottom:24px">神经网络在线 &middot; 所有系统正常</p>
</div>
<div class="brain-overlay">
      <div class="brain-status">
        <span class="pulse-dot active"></span>
        <span>Friday AI OS v3.0</span>
        <span class="status-text">神经网络在线</span>
      </div>
      <div class="agent-counts">
        <span>{{ activeAgents }} / {{ totalAgents }} Agent 活跃</span>
      </div>
    </div>

    <!-- 选中Agent详情弹窗 -->
    <transition name="fade">
      <div v-if="selectedAgent" class="agent-detail" :style="detailStyle">
        <div class="ad-header">
          <span class="ad-icon">{{ selectedAgent.icon }}</span>
          <span class="ad-name">{{ selectedAgent.name }}</span>
          <span class="ad-status" :class="selectedAgent.status">{{ selectedAgent.statusText }}</span>
        </div>
        <div class="ad-info">
          <div class="ad-row"><span>任务</span><span>{{ selectedAgent.tasks }}</span></div>
          <div class="ad-row"><span>成功率</span><span style="color:#52c41a">{{ selectedAgent.successRate }}%</span></div>
        </div>
        <div class="ad-actions">
          <button class="ad-btn" @click="activateAgent(selectedAgent.id)">激活</button>
          <button class="ad-btn secondary" @click="viewAgentDetail(selectedAgent.id)">详情</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'

const container = ref(null)
const canvas = ref(null)
const selectedAgent = ref(null)
const detailStyle = ref({})
const totalAgents = 7
const activeAgents = ref(7)
const totalAgents = 7
const activeAgents = ref(7)
const fallbackMode = ref(false)
let animFrameId
let mouseX = 0, mouseY = 0
let raycaster, mouse

// Agent定义
const agentDefs = [
  { id: 'master', name: 'Master Agent', icon: '🧠', color: 0x667eea, radius: 2.8, status: 'active', statusText: '运行中', tasks: 156, successRate: 98.2 },
  { id: 'code', name: 'Code Agent', icon: '💻', color: 0x52c41a, radius: 2.2, status: 'active', statusText: '开发中', tasks: 89, successRate: 94.5 },
  { id: 'devops', name: 'DevOps Agent', icon: '⚙️', color: 0x1890ff, radius: 2.5, status: 'active', statusText: '监控中', tasks: 234, successRate: 99.1 },
  { id: 'vision', name: 'Vision Agent', icon: '👁️', color: 0xfaad14, radius: 2.0, status: 'idle', statusText: '待命中', tasks: 45, successRate: 91.3 },
  { id: 'trend', name: 'Trend Agent', icon: '📡', color: 0xff4d4f, radius: 2.3, status: 'active', statusText: '采集热点', tasks: 312, successRate: 96.7 },
  { id: 'memory', name: 'Memory Agent', icon: '💾', color: 0x764ba2, radius: 2.6, status: 'active', statusText: '记忆中', tasks: 567, successRate: 99.8 },
  { id: 'heal', name: 'Self-Healing', icon: '🛡️', color: 0x13c2c2, radius: 2.4, status: 'idle', statusText: '待命中', tasks: 23, successRate: 100 },
]

async function loadThreeJS() {
  return new Promise((resolve, reject) => {
    if (window.THREE) { resolve(window.THREE); return }
    const script = document.createElement('script')
    script.src = 'https://unpkg.com/three@0.170.0/build/three.min.js'
    script.onload = () => resolve(window.THREE)
    script.onerror = () => reject(new Error('Three.js 加载失败'))
    document.head.appendChild(script)
  })
}

async function initScene() {
  try { THREE = await loadThreeJS() } catch (e) { console.error(e); fallbackMode.value = true; return }
  if (!container.value) return

  const w = container.value.clientWidth
  const h = container.value.clientHeight

  // 场景
  scene = new THREE.Scene()
  
  // 相机
  camera = new THREE.PerspectiveCamera(60, w / h, 0.1, 100)
  camera.position.set(0, 3, 14)
  camera.lookAt(0, 0, 0)

  // 渲染器
  renderer = new THREE.WebGLRenderer({ canvas: canvas.value, antialias: true, alpha: true })
  renderer.setSize(w, h)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.2

  // 时钟
  clock = new THREE.Clock()

  // 射线检测
  raycaster = new THREE.Raycaster()
  mouse = new THREE.Vector2()

  // 灯光
  const ambientLight = new THREE.AmbientLight(0x334466, 1.5)
  scene.add(ambientLight)
  const pointLight = new THREE.PointLight(0x667eea, 30, 30)
  pointLight.position.set(0, 5, 10)
  scene.add(pointLight)

  // 粒子星场背景
  createStarfield()
  
  // 圆环网格
  createGridRing()
  
  // 中央大脑球体
  createBrainCore()
  
  // 7个Agent节点
  createAgentNodes()
  
  // 连接线
  createConnections()

  // 事件
  canvas.value.addEventListener('mousemove', onMouseMove)
  canvas.value.addEventListener('click', onClick)
  window.addEventListener('resize', onResize)

  // 开始渲染循环
  animate()
}

function createStarfield() {
  const geo = new THREE.BufferGeometry()
  const count = 2000
  const positions = new Float32Array(count * 3)
  const colors = new Float32Array(count * 3)
  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 40
    positions[i * 3 + 1] = (Math.random() - 0.5) * 25
    positions[i * 3 + 2] = (Math.random() - 0.5) * 20 - 5
    const c = new THREE.Color().setHSL(0.6 + Math.random() * 0.3, 0.8, 0.4 + Math.random() * 0.4)
    colors[i * 3] = c.r
    colors[i * 3 + 1] = c.g
    colors[i * 3 + 2] = c.b
  }
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  const mat = new THREE.PointsMaterial({ size: 0.04, vertexColors: true, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.8 })
  particles = new THREE.Points(geo, mat)
  scene.add(particles)
}

function createGridRing() {
  const ringGeo = new THREE.TorusGeometry(6, 0.03, 16, 128)
  const ringMat = new THREE.MeshBasicMaterial({ color: 0x667eea, transparent: true, opacity: 0.3 })
  const ring = new THREE.Mesh(ringGeo, ringMat)
  ring.rotation.x = Math.PI / 2
  ring.position.y = -1
  scene.add(ring)

  const ring2 = new THREE.Mesh(new THREE.TorusGeometry(4, 0.02, 16, 100), 
    new THREE.MeshBasicMaterial({ color: 0x764ba2, transparent: true, opacity: 0.2 }))
  ring2.rotation.x = Math.PI / 3
  ring2.position.y = 0.5
  scene.add(ring2)
}

function createBrainCore() {
  // 核心球体
  const geo = new THREE.IcosahedronGeometry(1.2, 3)
  const mat = new THREE.MeshPhongMaterial({ 
    color: 0x667eea, emissive: 0x223366, emissiveIntensity: 0.8,
    shininess: 80, transparent: true, opacity: 0.85, wireframe: false
  })
  brainSphere = new THREE.Mesh(geo, mat)
  scene.add(brainSphere)

  // 外层线框
  const wireGeo = new THREE.IcosahedronGeometry(1.35, 3)
  const wireMat = new THREE.MeshBasicMaterial({ color: 0x8899ff, wireframe: true, transparent: true, opacity: 0.2 })
  const wireframe = new THREE.Mesh(wireGeo, wireMat)
  brainSphere.add(wireframe)

  // 光环
  const glowGeo = new THREE.RingGeometry(1.5, 1.8, 64)
  const glowMat = new THREE.MeshBasicMaterial({ color: 0x667eea, side: THREE.DoubleSide, transparent: true, opacity: 0.4 })
  const glowRing = new THREE.Mesh(glowGeo, glowMat)
  glowRing.rotation.x = Math.PI / 2
  brainSphere.add(glowRing)
}

function createAgentNodes() {
  agentNodes = agentDefs.map((def, i) => {
    const angle = (i / agentDefs.length) * Math.PI * 2
    const x = Math.cos(angle) * def.radius
    const z = Math.sin(angle) * def.radius
    const y = Math.sin(i * 1.5) * 1.5

    // 节点球
    const geo = new THREE.SphereGeometry(0.25, 32, 32)
    const mat = new THREE.MeshPhongMaterial({ color: def.color, emissive: def.color, emissiveIntensity: 0.6, shininess: 100 })
    const node = new THREE.Mesh(geo, mat)
    node.position.set(x, y, z)
    node.userData = { ...def, baseX: x, baseY: y, baseZ: z, angle }
    scene.add(node)

    // 光环
    const ringGeo = new THREE.RingGeometry(0.32, 0.4, 32)
    const ringMat = new THREE.MeshBasicMaterial({ color: def.color, side: THREE.DoubleSide, transparent: true, opacity: 0.5 })
    const glow = new THREE.Mesh(ringGeo, ringMat)
    node.add(glow)

    return node
  })
}

function createConnections() {
  connections = []
  agentNodes.forEach((node, i) => {
    // 每个Agent连接到大脑
    const lineGeo = new THREE.BufferGeometry()
    const midX = node.position.x * 0.5
    const midY = node.position.y * 0.5 + 0.3
    const midZ = node.position.z * 0.5
    lineGeo.setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(midX, midY, midZ),
      node.position.clone()
    ])
    const lineMat = new THREE.LineBasicMaterial({ color: node.userData.color, transparent: true, opacity: 0.3 })
    const line = new THREE.Line(lineGeo, lineMat)
    scene.add(line)
    connections.push({ line, target: node, color: node.userData.color })
  })

  // Agent之间连接
  for (let i = 0; i < agentNodes.length; i++) {
    for (let j = i + 1; j < agentNodes.length; j++) {
      const lineGeo = new THREE.BufferGeometry().setFromPoints([
        agentNodes[i].position, agentNodes[j].position
      ])
      const lineMat = new THREE.LineBasicMaterial({ color: 0x334466, transparent: true, opacity: 0.1 })
      const line = new THREE.Line(lineGeo, lineMat)
      scene.add(line)
      connections.push({ line, targetA: agentNodes[i], targetB: agentNodes[j] })
    }
  }
}

function onMouseMove(e) {
  const rect = canvas.value.getBoundingClientRect()
  mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1
  mouseY = -((e.clientY - rect.top) / rect.height) * 2 + 1
  mouse.x = mouseX
  mouse.y = mouseY
}

function onClick(e) {
  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(agentNodes)
  if (intersects.length > 0) {
    const node = intersects[0].object
    selectedAgent.value = node.userData
    const rect = canvas.value.getBoundingClientRect()
    detailStyle.value = {
      left: (e.clientX - rect.left + 20) + 'px',
      top: (e.clientY - rect.top - 60) + 'px',
    }
  } else {
    selectedAgent.value = null
  }
}

function onResize() {
  if (!container.value || !camera || !renderer) return
  const w = container.value.clientWidth
  const h = container.value.clientHeight
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  renderer.setSize(w, h)
}

function animate() {
  animFrameId = requestAnimationFrame(animate)
  const time = clock.getElapsedTime()

  // 相机随鼠标微动
  camera.position.x += (mouseX * 2 - camera.position.x) * 0.02
  camera.position.y += (-mouseY * 1.5 + 3 - camera.position.y) * 0.02
  camera.lookAt(0, 0, 0)

  // 大脑旋转+脉冲
  brainSphere.rotation.y += 0.003
  brainSphere.rotation.x += 0.001
  const pulse = 1 + Math.sin(time * 2) * 0.05
  brainSphere.scale.setScalar(pulse)

  // Agent节点浮动
  agentNodes.forEach((node) => {
    const d = node.userData
    const floatY = Math.sin(time * 1.5 + d.angle) * 0.3
    node.position.y = d.baseY + floatY
    node.rotation.y += 0.01
    node.rotation.x += 0.005
  })

  // 更新Agent-大脑连接线
  connections.forEach((conn) => {
    if (conn.target && conn.line.geometry) {
      const pos = conn.target.position
      const midX = pos.x * 0.5
      const midY = pos.y * 0.5 + 0.3
      const midZ = pos.z * 0.5
      conn.line.geometry.setFromPoints([
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(midX, midY, midZ),
        pos.clone()
      ])
    }
    if (conn.targetA && conn.targetB && conn.line.geometry) {
      conn.line.geometry.setFromPoints([
        conn.targetA.position.clone(),
        conn.targetB.position.clone()
      ])
    }
  })

  // 粒子旋转
  if (particles) particles.rotation.y += 0.0003

  renderer.render(scene, camera)
}

function activateAgent(id) {
  selectedAgent.value = null
}

function viewAgentDetail(id) {
  selectedAgent.value = null
}

onMounted(async () => {
  await nextTick()
  initScene()
})

onUnmounted(() => {
  if (animFrameId) cancelAnimationFrame(animFrameId)
  window.removeEventListener('resize', onResize)
  if (canvas.value) {
    canvas.value.removeEventListener('mousemove', onMouseMove)
    canvas.value.removeEventListener('click', onClick)
  }
})
</script>

<style scoped>
.friday-brain {
  position: relative;
  width: 100%;
  height: calc(100vh - 52px);
  background: radial-gradient(ellipse at center, #0d1025 0%, #080b1a 60%, #050812 100%);
  overflow: hidden;
  cursor: grab;
}
.friday-brain:active { cursor: grabbing; }

.brain-canvas {
  position: absolute;
  inset: 0;
}

.brain-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  pointer-events: none;
  z-index: 10;
}

.brain-status {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(255,255,255,0.8);
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.5px;
}
.pulse-dot {
  width: 8px; height: 8px; border-radius: 50%;
  animation: brainPulse 2s ease-in-out infinite;
}
.pulse-dot.active { background: #52c41a; box-shadow: 0 0 10px rgba(82,196,26,0.6); }
.status-text { color: rgba(255,255,255,0.4); font-size: 11px; }

.agent-counts {
  color: rgba(255,255,255,0.5);
  font-size: 12px;
}

@keyframes brainPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.3); }
}

/* Agent详情弹窗 */
.agent-detail {
  position: absolute;
  background: rgba(12, 16, 30, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  padding: 16px;
  min-width: 200px;
  z-index: 20;
  box-shadow: 0 8px 32px rgba(0,0,0,0.6), 0 0 20px rgba(102,126,234,0.1);
}
.ad-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.ad-icon { font-size: 24px; }
.ad-name { font-size: 14px; font-weight: 600; color: #fff; }
.ad-status {
  margin-left: auto;
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 8px;
}
.ad-status.active { background: rgba(82,196,26,0.15); color: #52c41a; }
.ad-status.idle { background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.5); }
.ad-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: rgba(255,255,255,0.6);
  padding: 4px 0;
}
.ad-actions { display: flex; gap: 8px; margin-top: 12px; }
.ad-btn {
  flex: 1;
  padding: 6px 0;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  background: rgba(102,126,234,0.2);
  color: #667eea;
  transition: all 0.15s;
}
.ad-btn:hover { background: rgba(102,126,234,0.35); }
.ad-btn.secondary { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.5); }
.ad-btn.secondary:hover { background: rgba(255,255,255,0.1); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
