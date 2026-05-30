<template>
  <div ref="container" class="nn3d-container" @dblclick="openChat">
    <div class="nn-overlay">
      <div class="nn-status">   {{ statusText }}</div>
      <div class="nn-info" v-if="speaking">...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue"
import * as THREE from "three"
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js"
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js"
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js"

const container = ref(null)
const speaking = ref(false)
const statusText = computed(() => speaking.value ? '' : '')

let scene, camera, renderer, composer, animFrameId, clock
let headFrame, headGlow, leftEye, rightEye, leftPupil, rightPupil
let mouthGroup, mouthTop, mouthBottom
let haloRings = [], neuralLines = [], ambientParticles = []
let raycaster, mouse, mouseTarget = new THREE.Vector2()

function emit(event, detail) { window.dispatchEvent(new CustomEvent(event, { detail })) }
function sendBrainEvent(type, data) { window.dispatchEvent(new CustomEvent("brain:send", {detail: {type, ...data}})) }
function openChat() { emit('brain:openChat') }

// =====  =====
function createHolographicFace() {
  const group = new THREE.Group()

  // ---  ---
  const headGeo = new THREE.SphereGeometry(2.2, 64, 48)
  const headMat = new THREE.MeshBasicMaterial({
    color: 0x4488ff,
    transparent: true,
    opacity: 0.08,
    wireframe: true,
    depthWrite: false
  })
  headFrame = new THREE.Mesh(headGeo, headMat)
  group.add(headFrame)

  
  const glowGeo = new THREE.SphereGeometry(2.4, 64, 48)
  const glowMat = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uColor: { value: new THREE.Color(0x4488ff) }
    },
    vertexShader: `
      varying vec3 vNormal; varying vec3 vPosition;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vPosition = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }`,
    fragmentShader: `
      varying vec3 vNormal; varying vec3 vPosition;
      uniform float uTime; uniform vec3 uColor;
      void main() {
        float fresnel = pow(1.0 - abs(dot(vNormal, vec3(0.0, 0.0, 1.0))), 3.0);
        float scanline = sin(vPosition.y * 20.0 + uTime * 2.0) * 0.5 + 0.5;
        float alpha = fresnel * 0.25 + scanline * 0.05;
        gl_FragColor = vec4(uColor, alpha);
      }`,
    transparent: true,
    depthWrite: false
  })
  headGlow = new THREE.Mesh(glowGeo, glowMat)
  group.add(headGlow)

  // --- 3---
  for (let i = 0; i < 3; i++) {
    const ringGeo = new THREE.TorusGeometry(2.6 + i * 0.15, 0.015, 16, 80)
    const ringMat = new THREE.MeshBasicMaterial({
      color: new THREE.Color().setHSL(0.6 + i * 0.08, 0.9, 0.5 + i * 0.2),
      transparent: true,
      opacity: 0.6,
      depthWrite: false
    })
    const ring = new THREE.Mesh(ringGeo, ringMat)
    ring.rotation.x = Math.PI / 3 + i * 0.5
    ring.rotation.y = i * 0.7
    ring.userData = { speed: 0.3 + i * 0.15, axis: i % 2 === 0 ? 'y' : 'x', baseOpacity: 0.6 }
    group.add(ring)
    haloRings.push(ring)
  }

  // ---  ---
  const eyeGeo = new THREE.SphereGeometry(0.35, 32, 32)
  const eyeMat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.95,
    depthWrite: false
  })
  leftEye = new THREE.Mesh(eyeGeo, eyeMat)
  leftEye.position.set(-0.6, 0.3, 1.8)
  group.add(leftEye)

  
  const pupilGeo = new THREE.SphereGeometry(0.18, 16, 16)
  const pupilMat = new THREE.MeshBasicMaterial({ color: 0x112244 })
  leftPupil = new THREE.Mesh(pupilGeo, pupilMat)
  leftPupil.position.z = 0.22
  leftEye.add(leftPupil)

  
  const eyeRingGeo = new THREE.TorusGeometry(0.38, 0.02, 16, 32)
  const eyeRingMat = new THREE.MeshBasicMaterial({ color: 0x88bbff, transparent: true, opacity: 0.7, depthWrite: false })
  const leftEyeRing = new THREE.Mesh(eyeRingGeo, eyeRingMat)
  leftEye.add(leftEyeRing)

  // ---  ---
  rightEye = new THREE.Mesh(eyeGeo.clone(), eyeMat.clone())
  rightEye.position.set(0.6, 0.3, 1.8)
  group.add(rightEye)

  rightPupil = new THREE.Mesh(pupilGeo.clone(), pupilMat.clone())
  rightPupil.position.z = 0.22
  rightEye.add(rightPupil)

  const rightEyeRing = new THREE.Mesh(eyeRingGeo.clone(), eyeRingMat.clone())
  rightEye.add(rightEyeRing)

  // ---  ---
  mouthGroup = new THREE.Group()
  mouthGroup.position.set(0, -0.5, 2.0)

  
  const mouthTopGeo = new THREE.TorusGeometry(0.5, 0.03, 8, 32, Math.PI)
  const mouthMat = new THREE.MeshBasicMaterial({ color: 0x88ccff, transparent: true, opacity: 0.8, depthWrite: false })
  mouthTop = new THREE.Mesh(mouthTopGeo, mouthMat)
  mouthGroup.add(mouthTop)

  
  const mouthBottomGeo = new THREE.TorusGeometry(0.5, 0.03, 8, 32, Math.PI)
  mouthBottom = new THREE.Mesh(mouthBottomGeo, mouthMat.clone())
  mouthBottom.rotation.z = Math.PI
  mouthGroup.add(mouthBottom)

  group.add(mouthGroup)

  // ---  ---
  for (let i = 0; i < 12; i++) {
    const pts = []
    const segments = 30
    const startAngle = (i / 12) * Math.PI * 2
    const startR = 2.0
    const endR = 2.1
    for (let j = 0; j <= segments; j++) {
      const t = j / segments
      const angle = startAngle + t * 0.6
      const r = startR + Math.sin(t * Math.PI) * 0.3
      pts.push(new THREE.Vector3(
        Math.cos(angle) * r,
        -1.2 + t * 2.0,
        Math.sin(angle) * r * 0.6
      ))
    }
    const lineGeo = new THREE.BufferGeometry().setFromPoints(pts)
    const lineMat = new THREE.LineBasicMaterial({
      color: new THREE.Color().setHSL(0.6 + i * 0.03, 0.8, 0.5),
      transparent: true,
      opacity: 0.3,
      depthWrite: false
    })
    const line = new THREE.Line(lineGeo, lineMat)
    line.userData = { phase: i * 0.5, speed: 0.3 + Math.random() * 0.4 }
    group.add(line)
    neuralLines.push(line)
  }

  return group
}

// =====  =====
function initScene() {
  const isMobile = window.innerWidth < 768
  const el = container.value
  const w = el.clientWidth
  const h = el.clientHeight

  scene = new THREE.Scene()

  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100)
  camera.position.set(0, 0, 8)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" })
  renderer.setSize(w, h)
  renderer.setPixelRatio(isMobile ? 1 : Math.min(window.devicePixelRatio, 2))
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.3
  el.appendChild(renderer.domElement)

  
  composer = new EffectComposer(renderer)
  composer.addPass(new RenderPass(scene, camera))
  const bloomPass = new UnrealBloomPass(new THREE.Vector2(w, h), 0.5, 0.3, 0.2)
  composer.addPass(bloomPass)

  
  const starsGeo = new THREE.BufferGeometry()
  const starCount = 3000
  const positions = new Float32Array(starCount * 3)
  const starColors = new Float32Array(starCount * 3)
  for (let i = 0; i < starCount; i++) {
    const theta = Math.random() * Math.PI * 2
    const phi = Math.acos(2 * Math.random() - 1)
    const r = 12 + Math.random() * 20
    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta)
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
    positions[i * 3 + 2] = r * Math.cos(phi)
    const c = new THREE.Color().setHSL(0.6 + Math.random() * 0.15, 0.4, 0.2 + Math.random() * 0.5)
    starColors[i * 3] = c.r
    starColors[i * 3 + 1] = c.g
    starColors[i * 3 + 2] = c.b
  }
  starsGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  starsGeo.setAttribute('color', new THREE.BufferAttribute(starColors, 3))
  const starsMat = new THREE.PointsMaterial({
    size: 0.05,
    vertexColors: true,
    transparent: true,
    opacity: 0.9,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })
  scene.add(new THREE.Points(starsGeo, starsMat))

  
  scene.add(new THREE.AmbientLight(0x222244, 0.5))

  
  const face = createHolographicFace()
  scene.add(face)

  
  const pGeo = new THREE.SphereGeometry(0.04, 4, 4)
  for (let i = 0; i < 60; i++) {
    const pMat = new THREE.MeshBasicMaterial({
      color: new THREE.Color().setHSL(0.55 + Math.random() * 0.2, 0.9, 0.6),
      transparent: true,
      opacity: 0,
      depthWrite: false
    })
    const p = new THREE.Mesh(pGeo, pMat)
    p.position.set(
      (Math.random() - 0.5) * 10,
      (Math.random() - 0.5) * 10,
      (Math.random() - 0.5) * 6
    )
    p.userData = {
      life: Math.random(),
      speed: 0.2 + Math.random() * 0.5,
      baseX: p.position.x,
      baseY: p.position.y,
      baseZ: p.position.z,
      amplitude: 0.3 + Math.random() * 0.8
    }
    scene.add(p)
    ambientParticles.push(p)
  }

  
  raycaster = new THREE.Raycaster()
  mouse = new THREE.Vector2()
}

// =====  =====
function animate() {
  animFrameId = requestAnimationFrame(animate)

  const t = clock.getElapsedTime()
  const speakingBoost = speaking.value ? 2.5 : 1

  
  if (headGlow?.material?.uniforms) {
    headGlow.material.uniforms.uTime.value = t
  }

  
  headFrame.rotation.y += 0.002
  headFrame.rotation.x = Math.sin(t * 0.3) * 0.05

  
  headGlow.rotation.y = headFrame.rotation.y
  headGlow.rotation.x = headFrame.rotation.x

  
  haloRings.forEach(ring => {
    const s = ring.userData.speed * speakingBoost
    if (ring.userData.axis === 'y') ring.rotation.y += s * 0.01
    else ring.rotation.x += s * 0.01
    ring.material.opacity = ring.userData.baseOpacity + Math.sin(t * s) * 0.15
  })

  
  const eyeTargetX = mouseTarget.x * 0.15
  const eyeTargetY = mouseTarget.y * 0.1
  leftPupil.position.x += (eyeTargetX - leftPupil.position.x) * 0.1
  leftPupil.position.y += (eyeTargetY - leftPupil.position.y) * 0.1
  rightPupil.position.x += (eyeTargetX - rightPupil.position.x) * 0.1
  rightPupil.position.y += (eyeTargetY - rightPupil.position.y) * 0.1

  
  const blinkCycle = Math.sin(t * 0.3)
  const blink = blinkCycle > 0.95 ? (blinkCycle - 0.95) * 20 : 1
  leftEye.scale.y = blink
  rightEye.scale.y = blink

  
  if (speaking.value) {
    const mouthOpen = 0.1 + Math.abs(Math.sin(t * 8)) * 0.25 + Math.abs(Math.sin(t * 13)) * 0.15
    mouthTop.position.y = mouthOpen
    mouthBottom.position.y = -mouthOpen
    mouthGroup.children.forEach(m => {
      m.material.opacity = 0.6 + Math.abs(Math.sin(t * 8)) * 0.4
    })
  } else {
    const breathe = Math.sin(t * 0.8) * 0.02
    mouthTop.position.y += (breathe - mouthTop.position.y) * 0.1
    mouthBottom.position.y += (-breathe - mouthBottom.position.y) * 0.1
  }

  
  neuralLines.forEach((line, i) => {
    line.material.opacity = 0.15 + Math.sin(t * line.userData.speed + line.userData.phase) * 0.15 + (speaking.value ? 0.2 : 0)
  })

  
  ambientParticles.forEach(p => {
    p.userData.life += p.userData.speed * 0.005
    if (p.userData.life > 1) p.userData.life = 0
    const l = p.userData.life
    p.material.opacity = Math.sin(l * Math.PI) * 0.6
    p.position.x = p.userData.baseX + Math.sin(t * 0.5 + l * 4) * p.userData.amplitude
    p.position.y = p.userData.baseY + Math.cos(t * 0.7 + l * 3) * p.userData.amplitude
    p.position.z = p.userData.baseZ + Math.sin(t * 0.6 + l * 2) * p.userData.amplitude * 0.5
  })

  
  camera.position.x = Math.sin(t * 0.15) * 0.3 + mouseTarget.x * 0.4
  camera.position.y = Math.cos(t * 0.2) * 0.2 - mouseTarget.y * 0.3
  camera.lookAt(0, 0, 0)

  composer.render()
}

// =====  =====
function onMouseMove(e) {
  const rect = container.value.getBoundingClientRect()
  mouseTarget.x = ((e.clientX - rect.left) / rect.width) * 2 - 1
  mouseTarget.y = -((e.clientY - rect.top) / rect.height) * 2 + 1
}

// =====  =====
function resize() {
  if (!container.value) return
  const w = container.value.clientWidth
  const h = container.value.clientHeight
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  renderer.setSize(w, h)
  composer.setSize(w, h)
}

// =====  =====
function onBrainSpeaking() { speaking.value = true; setTimeout(() => { speaking.value = false }, 2500) }

onMounted(() => {
  window.addEventListener("brain:active", (e) => { speaking.value = e.detail !== false })
  window.addEventListener("brain:thinking", (e) => { speaking.value = e.detail !== false })
  window.addEventListener("brain:speaking", () => { speaking.value = true; setTimeout(() => { speaking.value = false }, 2000) })
  window.addEventListener("brain:pulse", () => { speaking.value = true; setTimeout(() => { speaking.value = false }, 600) })
  window.addEventListener("brain:agent_call", () => { speaking.value = true; setTimeout(() => { speaking.value = false }, 3000) })
  clock = new THREE.Clock()
  initScene()
  animate()

  container.value.addEventListener('mousemove', onMouseMove)
  window.addEventListener('resize', resize)
  window.addEventListener('brain:speaking', onBrainSpeaking)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animFrameId)
  container.value?.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('resize', resize)
  window.removeEventListener('brain:speaking', onBrainSpeaking)
  renderer?.dispose()
  composer?.dispose()
})
</script>

<style scoped>
.nn3d-container {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: radial-gradient(ellipse at center, #0a0d2a 0%, #050816 100%);
  cursor: pointer;
}
.nn3d-container canvas {
  display: block;
}
.nn-overlay {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  pointer-events: none;
}
.nn-status {
  font-size: 13px;
  color: rgba(150, 200, 255, 0.8);
  text-shadow: 0 0 12px rgba(100, 150, 255, 0.5);
  letter-spacing: 3px;
}
.nn-info {
  font-size: 11px;
  color: rgba(100, 200, 255, 0.6);
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
</style>