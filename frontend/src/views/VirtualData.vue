<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1>馃懃 铏氭嫙鏁版嵁寮曟搸</h1>
        <p>涓€閿敓鎴愮湡瀹炴劅鏁版嵁 路 瀹炴椂娲诲姩妯℃嫙 路 璁╁晢鍩庢椿璧锋潵</p>
      </div>
    </div>

    <!-- 鏁版嵁瑙勬ā閫夋嫨 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="scale in scales" :key="scale.key">
        <el-card shadow="never" class="scale-card" :class="{ selected: selectedScale === scale.key }" @click="selectedScale = scale.key">
          <div class="scale-icon">{{ scale.icon }}</div>
          <div class="scale-name">{{ scale.name }}</div>
          <div class="scale-desc">{{ scale.desc }}</div>
          <div class="scale-meta">鐢ㄦ埛:{{ scale.users }} 鍟嗗搧:{{ scale.products }} 璁㈠崟:{{ scale.orders }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 鐢熸垚鎺у埗 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header><span>馃幃 鏁版嵁鐢熸垚鎺у埗鍙?/span></template>
          <el-row :gutter="16">
            <el-col :span="8" v-for="gen in generators" :key="gen.key">
              <div class="gen-card" @click="runGenerate(gen.key)">
                <div class="gen-icon">{{ gen.icon }}</div>
                <div class="gen-name">{{ gen.name }}</div>
                <div class="gen-count">{{ gen.count }}</div>
                <el-button type="primary" size="small" :loading="gen.running" @click.stop="runGenerate(gen.key)">
                  {{ gen.running ? '鐢熸垚涓?..' : '涓€閿敓鎴? }}
                </el-button>
              </div>
            </el-col>
          </el-row>
          <el-divider/>
          <div style="text-align:center;">
            <el-button type="success" size="large" @click="generateAll" :loading="allRunning">
              <el-icon><MagicStick /></el-icon> 馃殌 涓€閿叏閲忕敓鎴?            </el-button>
            <el-button size="large" @click="clearAll" style="margin-left:12px;">
              <el-icon><Delete /></el-icon> 娓呴櫎铏氭嫙鏁版嵁
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 瀹炴椂娲诲姩 -->
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>
            <div class="panel-header">
              <span>馃摗 瀹炴椂娲诲姩妯℃嫙</span>
              <el-switch v-model="realtimeRunning" active-text="杩愯涓? inactive-text="宸插仠姝?/>
            </div>
          </template>
          <div class="realtime-status">
            <div class="rt-stat-box">
              <div class="rt-stat-num">{{ rtStats.onlineUsers }}</div>
              <div class="rt-stat-label">鍦ㄧ嚎鐢ㄦ埛</div>
            </div>
            <div class="rt-stat-box">
              <div class="rt-stat-num">{{ rtStats.browsing }}</div>
              <div class="rt-stat-label">娴忚涓?/div>
            </div>
            <div class="rt-stat-box">
              <div class="rt-stat-num">{{ rtStats.ordering }}</div>
              <div class="rt-stat-label">涓嬪崟涓?/div>
            </div>
            <div class="rt-stat-box">
              <div class="rt-stat-num">{{ rtStats.newToday }}</div>
              <div class="rt-stat-label">浠婃棩鏂板</div>
            </div>
          </div>
          <div class="live-feed">
            <div class="live-title">馃摵 瀹炴椂鍔ㄦ€?/div>
            <div class="live-item" v-for="(item, i) in liveFeed" :key="i">
              <span class="live-emoji">{{ item.icon }}</span>
              <span class="live-text">{{ item.text }}</span>
              <span class="live-time">{{ item.time }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 鏁版嵁缁熻 -->
    <el-card shadow="never">
      <template #header><span>馃搳 鏁版嵁缁熻闈㈡澘</span></template>
      <el-row :gutter="20">
        <el-col :span="4" v-for="s in dataStats" :key="s.label">
          <div class="data-stat">
            <div class="ds-num">{{ s.value }}</div>
            <div class="ds-label">{{ s.label }}</div>
            <div class="ds-trend" :style="{ color: s.trendUp ? '#52c41a' : '#ff4d4f' }">{{ s.trendUp ? '鈫? : '鈫? }} {{ s.change }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { agentApi } from '@/api/index'

const selectedScale = ref('medium')
const realtimeRunning = ref(true)
const allRunning = ref(false)
let feedTimer = null
let rtTimer = null

const scales = [
  { key:'small', icon:'馃尡', name:'灏忓瀷搴楅摵', desc:'鍒濆垱闃舵', users:'500', products:'50', orders:'200' },
  { key:'medium', icon:'馃彧', name:'涓瀷鍟嗗煄', desc:'鎴愰暱闃舵', users:'5,000', products:'200', orders:'2,000' },
  { key:'large', icon:'馃彚', name:'澶у瀷骞冲彴', desc:'鎴愮啛闃舵', users:'50,000', products:'1,000', orders:'20,000' },
  { key:'huge', icon:'馃實', name:'瓒呯骇骞冲彴', desc:'琛屼笟棰嗗厛', users:'500,000', products:'5,000', orders:'200,000' },
]

const generators = reactive([
  { key:'users', icon:'馃懁', name:'铏氭嫙鐢ㄦ埛', count:'5,000浜?, running:false },
  { key:'products', icon:'馃摝', name:'铏氭嫙鍟嗗搧', count:'200浠?, running:false },
  { key:'orders', icon:'馃搵', name:'铏氭嫙璁㈠崟', count:'2,000鍗?, running:false },
  { key:'reviews', icon:'猸?, name:'鍟嗗搧璇勪环', count:'800鏉?, running:false },
  { key:'kline', icon:'馃搱', name:'K绾挎暟鎹?, count:'90澶?, running:false },
  { key:'customers', icon:'馃挰', name:'瀹㈡湇璁板綍', count:'300鏉?, running:false },
])

const rtStats = reactive({
  onlineUsers: 127,
  browsing: 89,
  ordering: 15,
  newToday: 42,
})

const liveFeed = reactive([
  { icon:'馃懁', text:'鐢ㄦ埛 user_8823 娉ㄥ唽鎴愬姛', time:'鍒氬垰' },
  { icon:'馃洅', text:'鐢ㄦ埛 Lily 涓嬪崟璐拱浜?iPhone 15 Pro', time:'30绉掑墠' },
  { icon:'猸?, text:'鐢ㄦ埛 Tom 缁?MacBook Air 鎵撲簡5鏄熷ソ璇?, time:'1鍒嗛挓鍓? },
  { icon:'馃憖', text:'鐢ㄦ埛 Jerry 姝ｅ湪娴忚 Nike Air Max 270', time:'2鍒嗛挓鍓? },
  { icon:'馃挰', text:'鐢ㄦ埛 Amy 鍜ㄨ浜嗕骇鍝佸昂鐮侀棶棰?, time:'3鍒嗛挓鍓? },
  { icon:'馃摝', text:'璁㈠崟 #202405280045 宸插彂璐?, time:'4鍒嗛挓鍓? },
])

const dataStats = [
  { label:'鎬荤敤鎴?, value:'5,248', trendUp:true, change:'12%' },
  { label:'鎬诲晢鍝?, value:'236', trendUp:true, change:'8%' },
  { label:'鎬昏鍗?, value:'2,156', trendUp:true, change:'23%' },
  { label:'浜ゆ槗棰?, value:'楼128,450', trendUp:true, change:'18%' },
  { label:'濂借瘎鐜?, value:'94.2%', trendUp:true, change:'2%' },
  { label:'澶嶈喘鐜?, value:'32.5%', trendUp:false, change:'3%' },
]

async function runGenerate(type) {
  const gen = generators.find(g => g.key === type)
  if (!gen || gen.running) return
  gen.running = true
  await new Promise(r => setTimeout(r, 1500))
  gen.running = false
  ElMessage.success(`${gen.name}宸茬敓鎴愬畬鎴愶紒`)
}

async function generateAllOriginal() {
  allRunning.value = true
  for (const gen of generators) {
    gen.running = true
    await new Promise(r => setTimeout(r, 800))
    gen.running = false
  }
  allRunning.value = false
  ElMessage.success('馃殌 鍏ㄩ噺铏氭嫙鏁版嵁鐢熸垚瀹屾瘯锛佸晢鍩庣幇鍦ㄧ湅璧锋潵鍍忕湡瀹炲ぇ骞冲彴浜嗭紒')
}

async function clearAll() {
  try {
    await ElMessageBox.confirm('纭娓呴櫎鎵€鏈夎櫄鎷熸暟鎹紵姝ゆ搷浣滀笉鍙挙閿€銆?, '璀﹀憡', { type: 'warning', confirmButtonText: '纭娓呴櫎' })
    ElMessage.success('铏氭嫙鏁版嵁宸叉竻闄?)
  } catch { }
}

// 瀹炴椂鍔ㄦ€佹ā鎷?function addLiveItem() {
  const items = [
    { icon:'馃懁', text:'鐢ㄦ埛 ' + randomName() + ' 娉ㄥ唽鎴愬姛' },
    { icon:'馃洅', text:'鐢ㄦ埛 ' + randomName() + ' 涓嬪崟璐拱浜嗗晢鍝? },
    { icon:'猸?, text:'鐢ㄦ埛 ' + randomName() + ' 鍙戣〃浜嗗晢鍝佽瘎浠? },
    { icon:'馃憖', text:'鐢ㄦ埛 ' + randomName() + ' 姝ｅ湪娴忚鍟嗗煄' },
  ]
  const item = items[Math.floor(Math.random() * items.length)]
  liveFeed.unshift({ ...item, time: '鍒氬垰' })
  if (liveFeed.length > 10) liveFeed.pop()
}

function randomName() {
  const names = ['灏忔槑','Lily','Tom','Jerry','Amy','Jack','Rose','Lucy','David','Emma','Leo','Mia']
  return names[Math.floor(Math.random() * names.length)] + '_' + Math.floor(Math.random() * 9000 + 1000)
}

watch(realtimeRunning, (val) => {
  if (val) {
    feedTimer = setInterval(() => {
      rtStats.onlineUsers = Math.max(50, rtStats.onlineUsers + Math.floor(Math.random() * 5) - 2)
      rtStats.browsing = Math.max(20, rtStats.browsing + Math.floor(Math.random() * 5) - 2)
      rtStats.ordering = Math.max(2, rtStats.ordering + Math.floor(Math.random() * 3) - 1)
      addLiveItem()
    }, 3000)
  } else {
    if (feedTimer) clearInterval(feedTimer)
    if (rtTimer) clearInterval(rtTimer)
  }
}, { immediate: true })

onUnmounted(() => {
  if (feedTimer) clearInterval(feedTimer)
  if (rtTimer) clearInterval(rtTimer)
})
</script>

<style scoped>
.page-container { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-header h1 { font-size: 20px; margin: 0 0 4px; color: var(--text-primary); }
.page-header p { font-size: 13px; color: var(--text-muted); margin: 0; }

.scale-card { text-align: center; border-radius: 12px; cursor: pointer; transition: all 0.2s; border: 2px solid transparent; }
.scale-card:hover { border-color: var(--color-primary-light); }
.scale-card.selected { border-color: #667eea; background: rgba(102,126,234,0.04); }
.scale-icon { font-size: 28px; margin-bottom: 8px; }
.scale-name { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.scale-desc { font-size: 12px; color: var(--text-muted); margin: 4px 0; }
.scale-meta { font-size: 11px; color: var(--text-muted); margin-top: 8px; }

.gen-card {
  text-align: center;
  padding: 20px 12px;
  border-radius: 12px;
  background: var(--bg-page);
  transition: all 0.15s;
  cursor: pointer;
}
.gen-card:hover { background: var(--bg-card); box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.gen-icon { font-size: 28px; margin-bottom: 8px; }
.gen-name { font-size: 14px; font-weight: 500; color: var(--text-primary); margin-bottom: 4px; }
.gen-count { font-size: 12px; color: var(--text-muted); margin-bottom: 12px; }

.panel-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 14px; }

.realtime-status { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.rt-stat-box { text-align: center; padding: 12px; border-radius: 8px; background: var(--bg-page); }
.rt-stat-num { font-size: 24px; font-weight: 700; color: var(--text-primary); }
.rt-stat-label { font-size: 11px; color: var(--text-muted); margin-top: 4px; }

.live-feed { max-height: 200px; overflow-y: auto; }
.live-title { font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 10px; }
.live-item { display: flex; align-items: center; gap: 8px; padding: 6px 0; border-bottom: 1px solid var(--border-color); font-size: 12px; }
.live-item:last-child { border-bottom: none; }
.live-emoji { width: 20px; flex-shrink: 0; }
.live-text { flex: 1; color: var(--text-secondary); }
.live-time { color: var(--text-muted); white-space: nowrap; font-size: 11px; }

.data-stat { text-align: center; padding: 12px; }
.ds-num { font-size: 28px; font-weight: 700; color: var(--text-primary); }
.ds-label { font-size: 12px; color: var(--text-muted); margin: 4px 0; }
.ds-trend { font-size: 12px; font-weight: 500; }
</style>
