<template>
  <div ref="container" class="kg-container">
    <div class="kg-overlay">
      <span class="kg-info">🕸️ {{ nodeCount }} 个记忆节点 · {{ edgeCount }} 条关联</span>
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

const props = defineProps({ memories: { type: Array, default: () => [] } })
const container = ref(null)
const nodeCount = ref(0)
const edgeCount = ref(0)
let scene, camera, renderer, composer, controls, animFrameId, nodes = [], edges = []
const colors = { "通用":0x667eea, "服务器":0xff6b6b, "Docker":0x13c2c2, "Nginx":0x52c41a, "部署":0xfaad14, "商城":0xff4d4f, "安全":0x7c3aed, "代码":0x0ea5e9, "AI":0x8b5cf6, "采集":0xf59e0b, "数据库":0x06b6d4, "趋势":0xec4899 }

function buildGraph() {
  const mems = props.memories?.length ? props.memories : Array.from({length:20}, (_,i)=>({category:["通用","服务器","Docker","Nginx","AI"][i%5],content:`记忆${i+1}`,importance:0.5+Math.random()*0.5}))
  nodeCount.value = mems.length
  const groupMap = {}
  mems.forEach((m,i) => {
    const cat = m.category || "通用"
    if (!groupMap[cat]) groupMap[cat] = []
    groupMap[cat].push({...m, idx: i})
  })
  const categories = Object.keys(groupMap)
  const angleStep = (Math.PI*2) / categories.length
  const positions = []
  categories.forEach((cat, ci) => {
    const angle = ci * angleStep
    const cx = Math.cos(angle) * 5, cz = Math.sin(angle) * 5
    groupMap[cat].forEach((m, mi) => {
      const spread = 1.5
      const x = cx + (Math.random()-0.5)*spread*2
      const y = (Math.random()-0.5)*spread*1.5
      const z = cz + (Math.random()-0.5)*spread*2
      positions.push({x,y,z,cat,size:0.12+m.importance*0.2,color:colors[cat]||0x667eea,idx:m.idx,importance:m.importance,content:m.content})
    })
  })
  positions.forEach((p) => {
    const geo = new THREE.SphereGeometry(p.size, 12, 12)
    const mat = new THREE.MeshPhongMaterial({color:p.color,emissive:p.color,emissiveIntensity:p.importance*0.3,transparent:true,opacity:0.85})
    const mesh = new THREE.Mesh(geo, mat)
    mesh.position.set(p.x, p.y, p.z)
    mesh.userData = p
    scene.add(mesh)
    nodes.push(mesh)
  })
  // 同类节点连接
  categories.forEach((cat) => {
    const g = groupMap[cat]
    for (let i = 0; i < g.length; i++) {
      for (let j = i+1; j < g.length; j++) {
        if (Math.random() > 0.4) {
          const p1 = positions[g[i].idx], p2 = positions[g[j].idx]
          if (!p1 || !p2) continue
          const geo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(p1.x,p1.y,p1.z), new THREE.Vector3(p2.x,p2.y,p2.z)])
          const mat = new THREE.LineBasicMaterial({color:p1.color,transparent:true,opacity:0.12})
          scene.add(new THREE.Line(geo, mat))
          edges.push(geo)
        }
      }
    }
  })
  edgeCount.value = edges.length
}

function init() {
  const el = container.value, w=el.clientWidth, h=el.clientHeight
  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(50,w/h,0.1,50)
  camera.position.set(10,6,10)
  renderer = new THREE.WebGLRenderer({antialias:true,alpha:true})
  renderer.setSize(w,h); renderer.setPixelRatio(Math.min(window.devicePixelRatio,2))
  el.appendChild(renderer.domElement)
  composer = new EffectComposer(renderer)
  composer.addPass(new RenderPass(scene,camera))
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(w,h),0.3,0.1,0.05))
  controls = new OrbitControls(camera,renderer.domElement)
  controls.enableDamping=true; controls.autoRotate=true; controls.autoRotateSpeed=0.6
  controls.minDistance=4; controls.maxDistance=20
  scene.add(new THREE.AmbientLight(0x404060,0.6))
  const dl = new THREE.DirectionalLight(0xffffff,1); dl.position.set(5,10,5); scene.add(dl)
  buildGraph()
}

function animate() {
  animFrameId=requestAnimationFrame(animate)
  const t=Date.now()*0.001
  nodes.forEach((n,i)=>{const b=1+0.04*Math.sin(t*0.5+i*0.1);n.scale.set(b,b,b)})
  controls.update(); composer.render()
}
function resize(){if(!container.value)return;const w=container.value.clientWidth,h=container.value.clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h);composer.setSize(w,h)}
onMounted(()=>{init();animate();window.addEventListener("resize",resize)})
onBeforeUnmount(()=>{cancelAnimationFrame(animFrameId);renderer?.dispose();composer?.dispose();window.removeEventListener("resize",resize)})
</script>
<style scoped>
.kg-container{width:100%;height:400px;border-radius:12px;overflow:hidden;background:transparent;position:relative}
.kg-overlay{position:absolute;top:0;left:0;right:0;z-index:10;display:flex;justify-content:center}
.kg-info{font-size:11px;padding:4px 12px;margin:8px;border-radius:12px;background:rgba(0,0,0,0.3);color:rgba(255,255,255,0.6)}
</style>
