<template>
  <div ref="container" class="nn3d-container">
    <div class="nn-overlay">
      <div class="nn-status">🧬 数字生命体 · 运行中</div>
      <div class="nn-info" v-if="hoveredNode">节点: {{ hoveredNode }} | 活跃连接: {{ connectionCount }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue"
import * as THREE from "three"
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js"
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js"
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js"
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js"

const container = ref(null)
const hoveredNode = ref("")
const connectionCount = ref(0)

let scene, camera, renderer, controls, composer, animFrameId
let core, coreGlow, nodes = [], connections = [], energyParticles = []
let brainWaves = [], dataStreams = []
let raycaster, mouse, selectedNode = null
let clock = new THREE.Clock()

// 生成有机神经网络（非固定层结构）
function generateOrganicNetwork() {
  const nodeCount = 180
  const nodes = []
  // 核心集群
  for (let i = 0; i < 30; i++) {
    const theta = Math.random() * Math.PI * 2
    const phi = Math.acos(2 * Math.random() - 1)
    const r = 1.5 + Math.random() * 1.5
    nodes.push({
      x: r * Math.sin(phi) * Math.cos(theta),
      y: r * Math.sin(phi) * Math.sin(theta) * 0.6,
      z: r * Math.cos(phi),
      size: 0.12 + Math.random() * 0.1,
      type: "core", active: true, phase: Math.random() * Math.PI * 2, speed: 0.3 + Math.random() * 0.5
    })
  }
  // 中间层
  for (let i = 0; i < 60; i++) {
    const theta = Math.random() * Math.PI * 2
    const r = 3 + Math.random() * 2.5
    nodes.push({
      x: r * Math.cos(theta),
      y: (Math.random() - 0.5) * 4,
      z: r * Math.sin(theta) * 0.5,
      size: 0.08 + Math.random() * 0.12,
      type: "mid", active: Math.random() > 0.2, phase: Math.random() * Math.PI * 2, speed: 0.2 + Math.random() * 0.4
    })
  }
  // 外层
  for (let i = 0; i < 90; i++) {
    const theta = Math.random() * Math.PI * 2
    const r = 5.5 + Math.random() * 3
    nodes.push({
      x: r * Math.cos(theta),
      y: (Math.random() - 0.5) * 6,
      z: (Math.random() - 0.5) * 3,
      size: 0.05 + Math.random() * 0.1,
      type: "outer", active: Math.random() > 0.4, phase: Math.random() * Math.PI * 2, speed: 0.1 + Math.random() * 0.3
    })
  }
  // 连接
  const conns = []
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[i].x - nodes[j].x, dy = nodes[i].y - nodes[j].y, dz = nodes[i].z - nodes[j].z
      const dist = Math.sqrt(dx * dx + dy * dy + dz * dz)
      if (dist < 4 && Math.random() > 0.85) {
        conns.push({ from: nodes[i], to: nodes[j], dist, active: Math.random() > 0.3, phase: Math.random() * Math.PI * 2 })
      }
    }
  }
  return { nodes, conns }
}

function initScene() {
  const el = container.value
  const w = el.clientWidth, h = el.clientHeight
  
  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 100)
  camera.position.set(16, 8, 18)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" })
  renderer.setSize(w, h)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.2
  el.appendChild(renderer.domElement)

  // Bloom 后期
  composer = new EffectComposer(renderer)
  composer.addPass(new RenderPass(scene, camera))
  const bloomPass = new UnrealBloomPass(new THREE.Vector2(w, h), 0.6, 0.2, 0.1)
  composer.addPass(bloomPass)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.06
  controls.autoRotate = true
  controls.autoRotateSpeed = 0.8
  controls.minDistance = 5
  controls.maxDistance = 35
  controls.target.set(0, 0, 0)

  // 灯光
  const ambient = new THREE.AmbientLight(0x222244, 0.8)
  scene.add(ambient)
  const dirLight = new THREE.DirectionalLight(0x8888ff, 1.5)
  dirLight.position.set(8, 15, 10)
  scene.add(dirLight)
  const rimLight = new THREE.DirectionalLight(0x13c2c2, 0.8)
  rimLight.position.set(-10, -5, -8)
  scene.add(rimLight)

  // 粒子背景星系
  const starsGeo = new THREE.BufferGeometry()
  const starCount = 4000
  const positions = new Float32Array(starCount * 3)
  const starColors = new Float32Array(starCount * 3)
  const starSizes = new Float32Array(starCount)
  for (let i = 0; i < starCount; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 100
    positions[i * 3 + 1] = (Math.random() - 0.5) * 100
    positions[i * 3 + 2] = (Math.random() - 0.5) * 100
    const c = new THREE.Color().setHSL(0.65 + Math.random() * 0.15, 0.6, 0.3 + Math.random() * 0.4)
    starColors[i * 3] = c.r; starColors[i * 3 + 1] = c.g; starColors[i * 3 + 2] = c.b
    starSizes[i] = 0.02 + Math.random() * 0.08
  }
  starsGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3))
  starsGeo.setAttribute("color", new THREE.BufferAttribute(starColors, 3))
  starsGeo.setAttribute("size", new THREE.BufferAttribute(starSizes, 1))
  const starsMat = new THREE.PointsMaterial({ size: 0.06, vertexColors: true, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending, depthWrite: false })
  scene.add(new THREE.Points(starsGeo, starsMat))

  // ===== 中央核心 =====
  const coreGeo = new THREE.IcosahedronGeometry(0.8, 3)
  const coreMat = new THREE.MeshPhongMaterial({
    color: 0x667eea, emissive: 0x3344aa, emissiveIntensity: 0.5,
    shininess: 100, transparent: true, opacity: 0.95
  })
  core = new THREE.Mesh(coreGeo, coreMat)
  scene.add(core)

  // 核心光晕
  const glowGeo = new THREE.IcosahedronGeometry(1.2, 2)
  const glowMat = new THREE.MeshBasicMaterial({
    color: 0x667eea, transparent: true, opacity: 0.12, wireframe: true
  })
  coreGlow = new THREE.Mesh(glowGeo, glowMat)
  scene.add(coreGlow)

  // 核心光环环
  for (let i = 0; i < 3; i++) {
    const ringGeo = new THREE.TorusGeometry(1.8 + i * 0.6, 0.02, 16, 48)
    const ringMat = new THREE.MeshBasicMaterial({
      color: i === 0 ? 0x667eea : i === 1 ? 0x13c2c2 : 0x7c3aed,
      transparent: true, opacity: 0.25 - i * 0.05
    })
    const ring = new THREE.Mesh(ringGeo, ringMat)
    ring.rotation.x = Math.PI / 3 + i * 0.4
    ring.rotation.y = i * 0.8
    scene.add(ring)
    dataStreams.push({ mesh: ring, speed: 0.2 + i * 0.1, axis: i % 2 === 0 ? "y" : "x" })
  }

  // 脑波线条（环绕核心的波浪线）
  for (let i = 0; i < 4; i++) {
    const pts = []
    const segments = 40
    const radius = 2.8 + i * 0.5
    for (let j = 0; j <= segments; j++) {
      const t = j / segments * Math.PI * 2
      pts.push(new THREE.Vector3(
        Math.cos(t) * radius,
        Math.sin(t * 3 + i) * 0.6,
        Math.sin(t) * radius
      ))
    }
    const geo = new THREE.BufferGeometry().setFromPoints(pts)
    const mat = new THREE.LineBasicMaterial({
      color: i % 2 === 0 ? 0x667eea : 0x13c2c2,
      transparent: true, opacity: 0.08 + i * 0.02
    })
    const line = new THREE.Line(geo, mat)
    scene.add(line)
    brainWaves.push({ mesh: line, speed: 0.3 + i * 0.1, phase: i * 0.8, amplitude: 0.6 + i * 0.2 })
  }

  // ===== 构建神经网络 =====
  raycaster = new THREE.Raycaster()
  mouse = new THREE.Vector2()
  const net = generateOrganicNetwork()

  const nodeColors = { core: 0x667eea, mid: 0x13c2c2, outer: 0x7c3aed }
  const nodeEmissive = { core: 0x3344aa, mid: 0x0d9488, outer: 0x5b21b6 }

  net.nodes.forEach((n, idx) => {
    const color = n.active ? nodeColors[n.type] : 0x222244
    const size = n.active ? n.size : n.size * 0.5
    const geo = new THREE.SphereGeometry(size, 12, 12)
    const mat = new THREE.MeshPhongMaterial({
      color, emissive: n.active ? nodeEmissive[n.type] : 0x000000,
      emissiveIntensity: n.active ? 0.3 : 0,
      transparent: true, opacity: n.active ? 0.9 : 0.2,
      shininess: 60
    })
    const mesh = new THREE.Mesh(geo, mat)
    mesh.position.set(n.x, n.y, n.z)
    mesh.userData = { index: idx, type: n.type, name: `神经元 #${idx + 1}`, typeName: n.type === "core" ? "核心" : n.type === "mid" ? "处理层" : "感知层" }
    scene.add(mesh)
    nodes.push(mesh)
  })

  // 连接线 + 能量粒子
  connectionCount.value = net.conns.length
  net.conns.forEach((c) => {
    if (!c.active) return
    const from = new THREE.Vector3(c.from.x, c.from.y, c.from.z)
    const to = new THREE.Vector3(c.to.x, c.to.y, c.to.z)
    const mid = new THREE.Vector3(
      (from.x + to.x) / 2 + (Math.random() - 0.5) * 0.5,
      (from.y + to.y) / 2 + (Math.random() - 0.5) * 0.5,
      (from.z + to.z) / 2 + (Math.random() - 0.5) * 0.5
    )
    const curve = new THREE.QuadraticBezierCurve3(from, mid, to)
    const pts = curve.getPoints(16)
    const geo = new THREE.BufferGeometry().setFromPoints(pts)
    const mat = new THREE.LineBasicMaterial({
      color: 0x667eea, transparent: true, opacity: 0.04 + Math.random() * 0.06
    })
    const line = new THREE.Line(geo, mat)
    scene.add(line)
    connections.push(line)

    // 能量粒子（沿连接线运动）
    if (Math.random() > 0.6) {
      const pGeo = new THREE.SphereGeometry(0.03, 6, 6)
      const pMat = new THREE.MeshBasicMaterial({ color: 0x88ccff, transparent: true, opacity: 0.6 })
      const particle = new THREE.Mesh(pGeo, pMat)
      particle.userData = { curve, progress: Math.random(), speed: 0.2 + Math.random() * 0.4 }
      scene.add(particle)
      energyParticles.push(particle)
    }
  })
}

function animate() {
  animFrameId = requestAnimationFrame(animate)
  const t = clock.getElapsedTime()
  const delta = clock.getDelta()

  // 核心旋转+脉冲
  core.rotation.x += 0.003
  core.rotation.y += 0.005
  const heartbeat = 1 + 0.08 * Math.sin(t * 1.5)
  core.scale.set(heartbeat, heartbeat, heartbeat)
  core.material.emissiveIntensity = 0.3 + 0.3 * Math.sin(t * 1.5)

  // 核心光晕旋转
  coreGlow.rotation.x += 0.002
  coreGlow.rotation.z += 0.003
  coreGlow.material.opacity = 0.08 + 0.06 * Math.sin(t * 1.2)

  // 光环旋转
  dataStreams.forEach((s, i) => {
    if (s.axis === "y") s.mesh.rotation.y += s.speed * 0.01
    else s.mesh.rotation.x += s.speed * 0.01
    s.mesh.material.opacity = 0.15 + 0.1 * Math.sin(t * s.speed + i)
  })

  // 脑波动画
  brainWaves.forEach((bw) => {
    const positions = bw.mesh.geometry.attributes.position
    if (!positions) return
    const array = positions.array
    const count = positions.count
    const radius = 2.8 + brainWaves.indexOf(bw) * 0.5
    for (let i = 0; i < count; i++) {
      const progress = i / count * Math.PI * 2
      const wave = Math.sin(progress * 3 + t * bw.speed + bw.phase) * bw.amplitude
      const angle = progress + t * bw.speed * 0.1
      array[i * 3] = Math.cos(angle) * (radius + wave * 0.3)
      array[i * 3 + 1] = Math.sin(progress * 3 + t * bw.speed + bw.phase) * bw.amplitude
      array[i * 3 + 2] = Math.sin(angle) * (radius + wave * 0.3)
    }
    positions.needsUpdate = true
  })

  // 节点呼吸+脉冲
  nodes.forEach((n, i) => {
    const breathe = 1 + 0.06 * Math.sin(t * 0.6 + i * 0.2)
    n.scale.set(breathe, breathe, breathe)
    if (n === selectedNode) {
      n.material.emissiveIntensity = 0.6 + 0.4 * Math.sin(t * 2)
    }
  })

  // 能量粒子沿连接线流动
  energyParticles.forEach((p) => {
    p.userData.progress += 0.005 * p.userData.speed
    if (p.userData.progress > 1) p.userData.progress = 0
    const pt = p.userData.curve.getPoint(p.userData.progress)
    p.position.copy(pt)
    p.material.opacity = 0.3 + 0.5 * Math.sin(p.userData.progress * Math.PI)
    const s = 1 + 0.5 * Math.sin(p.userData.progress * Math.PI)
    p.scale.set(s, s, s)
  })

  controls.update()
  composer.render()
}

function onMouseMove(e) {
  const rect = container.value.getBoundingClientRect()
  mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1
  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(nodes)
  if (intersects.length > 0) {
    const obj = intersects[0].object
    hoveredNode.value = `${obj.userData.name} (${obj.userData.typeName})`
    container.value.style.cursor = "pointer"
    obj.material.emissiveIntensity = 0.8
  } else {
    hoveredNode.value = ""
    container.value.style.cursor = "default"
    nodes.forEach(n => { if (n !== selectedNode) n.material.emissiveIntensity = 0.3 })
  }
}

function onClick(e) {
  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(nodes)
  if (intersects.length > 0) {
    const obj = intersects[0].object
    selectedNode = selectedNode === obj ? null : obj
  } else {
    selectedNode = null
  }
}

function resize() {
  if (!container.value) return
  const w = container.value.clientWidth, h = container.value.clientHeight
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  renderer.setSize(w, h)
  composer.setSize(w, h)
}

onMounted(() => {
  initScene()
  animate()
  window.addEventListener("resize", resize)
  container.value.addEventListener("mousemove", onMouseMove)
  container.value.addEventListener("click", onClick)
})
onBeforeUnmount(() => {
  cancelAnimationFrame(animFrameId)
  renderer?.dispose()
  composer?.dispose()
  window.removeEventListener("resize", resize)
  if (container.value) {
    container.value.removeEventListener("mousemove", onMouseMove)
    container.value.removeEventListener("click", onClick)
  }
})
</script>

<style scoped>
.nn3d-container {
  width: 100%; height: 520px; border-radius: 16px; overflow: hidden;
  background: radial-gradient(ellipse at center, #0a0d2a 0%, #050816 100%);
  position: relative; cursor: default;
}
.nn-overlay {
  position: absolute; top: 0; left: 0; right: 0; z-index: 10;
  display: flex; justify-content: space-between; align-items: flex-start;
}
.nn-status {
  font-size: 11px; padding: 6px 14px; margin: 12px; border-radius: 20px;
  background: rgba(102,126,234,0.15); backdrop-filter: blur(8px);
  color: rgba(255,255,255,0.8); border: 1px solid rgba(102,126,234,0.2);
  letter-spacing: 0.5px;
}
.nn-info {
  font-size: 11px; padding: 6px 14px; margin: 12px; border-radius: 20px;
  background: rgba(0,0,0,0.4); backdrop-filter: blur(8px);
  color: rgba(255,255,255,0.6);
}
</style>
