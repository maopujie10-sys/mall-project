锘?template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1>棣冩噧 閾忔碍瀚欓弫鐗堝祦瀵洘鎼?/h1>
        <p>娑撯偓闁款喚鏁撻幋鎰埂鐎圭偞鍔呴弫鐗堝祦 璺?鐎圭偞妞傚ú璇插З濡剝瀚?璺?鐠佲晛鏅㈤崺搴㈡た鐠ч攱娼?/p>
      </div>
    </div>

    <!-- 閺佺増宓佺憴鍕侀柅澶嬪 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="scale in scales" :key="scale.key">
        <el-card shadow="never" class="scale-card" :class="{ selected: selectedScale === scale.key }" @click="selectedScale = scale.key">
          <div class="scale-icon">{{ scale.icon }}</div>
          <div class="scale-name">{{ scale.name }}</div>
          <div class="scale-desc">{{ scale.desc }}</div>
          <div class="scale-meta">閻劍鍩?{{ scale.users }} 閸熷棗鎼?{{ scale.products }} 鐠併垹宕?{{ scale.orders }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 閻㈢喐鍨氶幒褍鍩?-->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header><span>棣冨箖 閺佺増宓侀悽鐔稿灇閹貉冨煑閸?/span></template>
          <el-row :gutter="16">
            <el-col :span="8" v-for="gen in generators" :key="gen.key">
              <div class="gen-card" @click="runGenerate(gen.key)">
                <div class="gen-icon">{{ gen.icon }}</div>
                <div class="gen-name">{{ gen.name }}</div>
                <div class="gen-count">{{ gen.count }}</div>
                <el-button type="primary" size="small" :loading="gen.running" @click.stop="runGenerate(gen.key)">
                  {{ gen.running ? '閻㈢喐鍨氭稉?..' : '娑撯偓闁款喚鏁撻幋? }}
                </el-button>
              </div>
            </el-col>
          </el-row>
          <el-divider/>
          <div style="text-align:center;">
            <el-button type="success" size="large" @click="generateAll" :loading="allRunning">
              <el-icon><MagicStick /></el-icon> 棣冩畬 娑撯偓闁款喖鍙忛柌蹇曟晸閹?            </el-button>
            <el-button size="large" @click="clearAll" style="margin-left:12px;">
              <el-icon><Delete /></el-icon> 濞撳懘娅庨搹姘珯閺佺増宓?            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 鐎圭偞妞傚ú璇插З -->
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>
            <div class="panel-header">
              <span>棣冩憲 鐎圭偞妞傚ú璇插З濡剝瀚?/span>
              <el-switch v-model="realtimeRunning" active-text="鏉╂劘顢戞稉? inactive-text="瀹告彃浠犲?/>
            </div>
          </template>
          <div class="realtime-status">
            <div class="rt-stat-box">
              <div class="rt-stat-num">{{ rtStats.onlineUsers }}</div>
              <div class="rt-stat-label">閸︺劎鍤庨悽銊﹀煕</div>
            </div>
            <div class="rt-stat-box">
              <div class="rt-stat-num">{{ rtStats.browsing }}</div>
              <div class="rt-stat-label">濞村繗顫嶆稉?/div>
            </div>
            <div class="rt-stat-box">
              <div class="rt-stat-num">{{ rtStats.ordering }}</div>
              <div class="rt-stat-label">娑撳宕熸稉?/div>
            </div>
            <div class="rt-stat-box">
              <div class="rt-stat-num">{{ rtStats.newToday }}</div>
              <div class="rt-stat-label">娴犲﹥妫╅弬鏉款杻</div>
            </div>
          </div>
          <div class="live-feed">
            <div class="live-title">棣冩懙 鐎圭偞妞傞崝銊︹偓?/div>
            <div class="live-item" v-for="(item, i) in liveFeed" :key="i">
              <span class="live-emoji">{{ item.icon }}</span>
              <span class="live-text">{{ item.text }}</span>
              <span class="live-time">{{ item.time }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 閺佺増宓佺紒鐔活吀 -->
    <el-card shadow="never">
      <template #header><span>棣冩惓 閺佺増宓佺紒鐔活吀闂堛垺婢?/span></template>
      <el-row :gutter="20">
        <el-col :span="4" v-for="s in dataStats" :key="s.label">
          <div class="data-stat">
            <div class="ds-num">{{ s.value }}</div>
            <div class="ds-label">{{ s.label }}</div>
            <div class="ds-trend" :style="{ color: s.trendUp ? '#52c41a' : '#ff4d4f' }">{{ s.trendUp ? '閳? : '閳? }} {{ s.change }}</div>
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
import { generateData, getRealtimeActivity, getDashboardStats } from '@/api/virtual'

const selectedScale = ref('medium')
const realtimeRunning = ref(true)
const allRunning = ref(false)
let feedTimer = null
let rtTimer = null

const scales = [
  { key:'small', icon:'棣冨啊', name:'鐏忓繐鐎锋惔妤呮懙', desc:'閸掓繂鍨遍梼鑸殿唽', users:'500', products:'50', orders:'200' },
  { key:'medium', icon:'棣冨涧', name:'娑擃厼鐎烽崯鍡楃厔', desc:'閹存劙鏆遍梼鑸殿唽', users:'5,000', products:'200', orders:'2,000' },
  { key:'large', icon:'棣冨綒', name:'婢堆冪€烽獮鍐插酱', desc:'閹存劗鍟涢梼鑸殿唽', users:'50,000', products:'1,000', orders:'20,000' },
  { key:'huge', icon:'棣冨', name:'鐡掑懐楠囬獮鍐插酱', desc:'鐞涘奔绗熸０鍡楀帥', users:'500,000', products:'5,000', orders:'200,000' },
]

const generators = reactive([
  { key:'users', icon:'棣冩噥', name:'閾忔碍瀚欓悽銊﹀煕', count:'5,000娴?, running:false },
  { key:'products', icon:'棣冩憹', name:'閾忔碍瀚欓崯鍡楁惂', count:'200娴?, running:false },
  { key:'orders', icon:'棣冩惖', name:'閾忔碍瀚欑拋銏犲礋', count:'2,000閸?, running:false },
  { key:'reviews', icon:'鐚?, name:'閸熷棗鎼х拠鍕幆', count:'800閺?, running:false },
  { key:'kline', icon:'棣冩惐', name:'K缁炬寧鏆熼幑?, count:'90婢?, running:false },
  { key:'customers', icon:'棣冩尠', name:'鐎广垺婀囩拋鏉跨秿', count:'300閺?, running:false },
])

const rtStats = reactive({
  onlineUsers: 127,
  browsing: 89,
  ordering: 15,
  newToday: 42,
})

const liveFeed = reactive([
  { icon:'棣冩噥', text:'閻劍鍩?user_8823 濞夈劌鍞介幋鎰', time:'閸掓艾鍨? },
  { icon:'棣冩磪', text:'閻劍鍩?Lily 娑撳宕熺拹顓濇嫳娴?iPhone 15 Pro', time:'30缁夋帒澧? },
  { icon:'鐚?, text:'閻劍鍩?Tom 缂?MacBook Air 閹垫挷绨?閺勭喎銈界拠?, time:'1閸掑棝鎸撻崜? },
  { icon:'棣冩問', text:'閻劍鍩?Jerry 濮濓絽婀ù蹇氼潔 Nike Air Max 270', time:'2閸掑棝鎸撻崜? },
  { icon:'棣冩尠', text:'閻劍鍩?Amy 閸溿劏顕楁禍鍡曢獓閸濅礁鏄傞惍渚€妫舵０?, time:'3閸掑棝鎸撻崜? },
  { icon:'棣冩憹', text:'鐠併垹宕?#202405280045 瀹告彃褰傜拹?, time:'4閸掑棝鎸撻崜? },
])

const dataStats = [
  { label:'閹崵鏁ら幋?, value:'5,248', trendUp:true, change:'12%' },
  { label:'閹鏅㈤崫?, value:'236', trendUp:true, change:'8%' },
  { label:'閹槒顓归崡?, value:'2,156', trendUp:true, change:'23%' },
  { label:'娴溿倖妲楁０?, value:'妤?28,450', trendUp:true, change:'18%' },
  { label:'婵傚€熺槑閻?, value:'94.2%', trendUp:true, change:'2%' },
  { label:'婢跺秷鍠橀悳?, value:'32.5%', trendUp:false, change:'3%' },
]

async function runGenerate(type) {
  const gen = generators.find(g => g.key === type)
  if (!gen || gen.running) return
  gen.running = true
  try {
    const { data } = await generateData(selectedScale.value, type)
    ElMessage.success(gen.name + `鐢熸垚瀹屾垚! ` + JSON.stringify(data.stats))
  } catch {
    ElMessage.error(gen.name + `鐢熸垚澶辫触`)
  }
  gen.running = false
}

async function generateAll() {
  allRunning.value = true
  try {
    const { data } = await generateData(selectedScale.value)
    ElMessage.success('棣冩畬 閸忋劑鍣洪搹姘珯閺佺増宓侀悽鐔稿灇鐎瑰本鐦敍浣告櫌閸╁海骞囬崷銊ф箙鐠ч攱娼甸崓蹇曟埂鐎圭偛銇囬獮鍐插酱娴滃棴绱?)
  } catch {
    ElMessage.error('鐢熸垚澶辫触')
  }
  allRunning.value = false
}

async function clearAll() {
  try {
    await ElMessageBox.confirm('绾喛顓诲〒鍛存珟閹碘偓閺堝娅勯幏鐔告殶閹诡噯绱靛銈嗘惙娴ｆ粈绗夐崣顖涙寵闁库偓閵?, '鐠€锕€鎲?, { type: 'warning', confirmButtonText: '绾喛顓诲〒鍛存珟' })
    ElMessage.success('閾忔碍瀚欓弫鐗堝祦瀹稿弶绔婚梽?)
  } catch { }
}


// 鑾峰彇鐪熷疄浠〃鐩樻暟鎹?async function fetchDashboard() {
  try {
    const { data: db } = await getDashboardStats()
    if (db.stats) {
      dataStats.value = [
        { label: '閻劍鍩涢幀濠氬櫤', value: db.stats.total?.users || 0, change: '+5.2%', trendUp: true },
        { label: '閸熷棗鎼ч幀濠氬櫤', value: db.stats.total?.products || 0, change: '+3.1%', trendUp: true },
        { label: '鐠併垹宕熼幀濠氬櫤', value: db.stats.total?.orders || 0, change: '+12.8%', trendUp: true },
        { label: '24h閹存劒姘︽０?/span>', value: '妤? + (db.stats.total?.volume_24h || 0).toLocaleString(), change: '+8.5%', trendUp: true },
        { label: '娴犲﹥妫╅弬鎵暏閹?/span>', value: db.stats.today?.new_users || 0, change: '+15%', trendUp: true },
        { label: '閸︺劎鍤庢禍鐑樻殶', value: db.online_now || 0, change: '鐎圭偞妞?, trendUp: true }
      ]
    }
  } catch {}
}

// 鐎圭偞妞傞崝銊︹偓浣鼓侀幏?function addLiveItem() {
  const items = [
    { icon:'棣冩噥', text:'閻劍鍩?' + randomName() + ' 濞夈劌鍞介幋鎰' },
    { icon:'棣冩磪', text:'閻劍鍩?' + randomName() + ' 娑撳宕熺拹顓濇嫳娴滃棗鏅㈤崫? },
    { icon:'鐚?, text:'閻劍鍩?' + randomName() + ' 閸欐垼銆冩禍鍡楁櫌閸濅浇鐦庢禒? },
    { icon:'棣冩問', text:'閻劍鍩?' + randomName() + ' 濮濓絽婀ù蹇氼潔閸熷棗鐓? },
  ]
  const item = items[Math.floor(Math.random() * items.length)]
  liveFeed.unshift({ ...item, time: '閸掓艾鍨? })
  if (liveFeed.length > 10) liveFeed.pop()
}

function randomName() {
  const names = ['鐏忓繑妲?,'Lily','Tom','Jerry','Amy','Jack','Rose','Lucy','David','Emma','Leo','Mia']
  return names[Math.floor(Math.random() * names.length)] + '_' + Math.floor(Math.random() * 9000 + 1000)
}

fetchDashboard()
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
