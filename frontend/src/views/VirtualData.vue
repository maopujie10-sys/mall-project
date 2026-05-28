<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1>👥 虚拟数据引擎</h1>
        <p>一键生成真实感数据 · 实时活动模拟 · 让商城活起来</p>
      </div>
    </div>

    <!-- 数据规模选择 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="scale in scales" :key="scale.key">
        <el-card shadow="never" class="scale-card" :class="{ selected: selectedScale === scale.key }" @click="selectedScale = scale.key">
          <div class="scale-icon">{{ scale.icon }}</div>
          <div class="scale-name">{{ scale.name }}</div>
          <div class="scale-desc">{{ scale.desc }}</div>
          <div class="scale-meta">用户:{{ scale.users }} 商品:{{ scale.products }} 订单:{{ scale.orders }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 生成控制 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header><span>🎮 数据生成控制台</span></template>
          <el-row :gutter="16">
            <el-col :span="8" v-for="gen in generators" :key="gen.key">
              <div class="gen-card" @click="runGenerate(gen.key)">
                <div class="gen-icon">{{ gen.icon }}</div>
                <div class="gen-name">{{ gen.name }}</div>
                <div class="gen-count">{{ gen.count }}</div>
                <el-button type="primary" size="small" :loading="gen.running" @click.stop="runGenerate(gen.key)">
                  {{ gen.running ? '生成中...' : '一键生成' }}
                </el-button>
              </div>
            </el-col>
          </el-row>
          <el-divider/>
          <div style="text-align:center;">
            <el-button type="success" size="large" @click="generateAll" :loading="allRunning">
              <el-icon><MagicStick /></el-icon> 🚀 一键全量生成
            </el-button>
            <el-button size="large" @click="clearAll" style="margin-left:12px;">
              <el-icon><Delete /></el-icon> 清除虚拟数据
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 实时活动 -->
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>
            <div class="panel-header">
              <span>📡 实时活动模拟</span>
              <el-switch v-model="realtimeRunning" active-text="运行中" inactive-text="已停止"/>
            </div>
          </template>
          <div class="realtime-status">
            <div class="rt-stat-box">
              <div class="rt-stat-num">{{ rtStats.onlineUsers }}</div>
              <div class="rt-stat-label">在线用户</div>
            </div>
            <div class="rt-stat-box">
              <div class="rt-stat-num">{{ rtStats.browsing }}</div>
              <div class="rt-stat-label">浏览中</div>
            </div>
            <div class="rt-stat-box">
              <div class="rt-stat-num">{{ rtStats.ordering }}</div>
              <div class="rt-stat-label">下单中</div>
            </div>
            <div class="rt-stat-box">
              <div class="rt-stat-num">{{ rtStats.newToday }}</div>
              <div class="rt-stat-label">今日新增</div>
            </div>
          </div>
          <div class="live-feed">
            <div class="live-title">📺 实时动态</div>
            <div class="live-item" v-for="(item, i) in liveFeed" :key="i">
              <span class="live-emoji">{{ item.icon }}</span>
              <span class="live-text">{{ item.text }}</span>
              <span class="live-time">{{ item.time }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据统计 -->
    <el-card shadow="never">
      <template #header><span>📊 数据统计面板</span></template>
      <el-row :gutter="20">
        <el-col :span="4" v-for="s in dataStats" :key="s.label">
          <div class="data-stat">
            <div class="ds-num">{{ s.value }}</div>
            <div class="ds-label">{{ s.label }}</div>
            <div class="ds-trend" :style="{ color: s.trendUp ? '#52c41a' : '#ff4d4f' }">{{ s.trendUp ? '↗' : '↘' }} {{ s.change }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const selectedScale = ref('medium')
const realtimeRunning = ref(true)
const allRunning = ref(false)
let feedTimer = null
let rtTimer = null

const scales = [
  { key:'small', icon:'🌱', name:'小型店铺', desc:'初创阶段', users:'500', products:'50', orders:'200' },
  { key:'medium', icon:'🏪', name:'中型商城', desc:'成长阶段', users:'5,000', products:'200', orders:'2,000' },
  { key:'large', icon:'🏢', name:'大型平台', desc:'成熟阶段', users:'50,000', products:'1,000', orders:'20,000' },
  { key:'huge', icon:'🌍', name:'超级平台', desc:'行业领先', users:'500,000', products:'5,000', orders:'200,000' },
]

const generators = reactive([
  { key:'users', icon:'👤', name:'虚拟用户', count:'5,000人', running:false },
  { key:'products', icon:'📦', name:'虚拟商品', count:'200件', running:false },
  { key:'orders', icon:'📋', name:'虚拟订单', count:'2,000单', running:false },
  { key:'reviews', icon:'⭐', name:'商品评价', count:'800条', running:false },
  { key:'kline', icon:'📈', name:'K线数据', count:'90天', running:false },
  { key:'customers', icon:'💬', name:'客服记录', count:'300条', running:false },
])

const rtStats = reactive({
  onlineUsers: 127,
  browsing: 89,
  ordering: 15,
  newToday: 42,
})

const liveFeed = reactive([
  { icon:'👤', text:'用户 user_8823 注册成功', time:'刚刚' },
  { icon:'🛒', text:'用户 Lily 下单购买了 iPhone 15 Pro', time:'30秒前' },
  { icon:'⭐', text:'用户 Tom 给 MacBook Air 打了5星好评', time:'1分钟前' },
  { icon:'👀', text:'用户 Jerry 正在浏览 Nike Air Max 270', time:'2分钟前' },
  { icon:'💬', text:'用户 Amy 咨询了产品尺码问题', time:'3分钟前' },
  { icon:'📦', text:'订单 #202405280045 已发货', time:'4分钟前' },
])

const dataStats = [
  { label:'总用户', value:'5,248', trendUp:true, change:'12%' },
  { label:'总商品', value:'236', trendUp:true, change:'8%' },
  { label:'总订单', value:'2,156', trendUp:true, change:'23%' },
  { label:'交易额', value:'¥128,450', trendUp:true, change:'18%' },
  { label:'好评率', value:'94.2%', trendUp:true, change:'2%' },
  { label:'复购率', value:'32.5%', trendUp:false, change:'3%' },
]

async function runGenerate(type) {
  const gen = generators.find(g => g.key === type)
  if (!gen || gen.running) return
  gen.running = true
  await new Promise(r => setTimeout(r, 1500))
  gen.running = false
  ElMessage.success(`${gen.name}已生成完成！`)
}

async function generateAll() {
  allRunning.value = true
  for (const gen of generators) {
    gen.running = true
    await new Promise(r => setTimeout(r, 800))
    gen.running = false
  }
  allRunning.value = false
  ElMessage.success('🚀 全量虚拟数据生成完毕！商城现在看起来像真实大平台了！')
}

async function clearAll() {
  try {
    await ElMessageBox.confirm('确认清除所有虚拟数据？此操作不可撤销。', '警告', { type: 'warning', confirmButtonText: '确认清除' })
    ElMessage.success('虚拟数据已清除')
  } catch { }
}

// 实时动态模拟
function addLiveItem() {
  const items = [
    { icon:'👤', text:'用户 ' + randomName() + ' 注册成功' },
    { icon:'🛒', text:'用户 ' + randomName() + ' 下单购买了商品' },
    { icon:'⭐', text:'用户 ' + randomName() + ' 发表了商品评价' },
    { icon:'👀', text:'用户 ' + randomName() + ' 正在浏览商城' },
  ]
  const item = items[Math.floor(Math.random() * items.length)]
  liveFeed.unshift({ ...item, time: '刚刚' })
  if (liveFeed.length > 10) liveFeed.pop()
}

function randomName() {
  const names = ['小明','Lily','Tom','Jerry','Amy','Jack','Rose','Lucy','David','Emma','Leo','Mia']
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
