锘?template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1>棣冩磪 闁插洭娉︽稉顓炵妇</h1>
        <p>婢舵艾閽╅崣鐗堟閼充粙鍣伴梿?璺?閸熷棗鎼ч弫鐗堝祦鐎瑰本鏆ｆ穱婵堟殌 璺?閼奉亜濮╂稉濠佺炊閼垫崘顔嗘禍鎱峅S</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon> 閺傛澘缂撻柌鍥肠娴犺濮?        </el-button>
      </div>
    </div>

    <!-- 闁插洭娉﹂獮鍐插酱閸楋紕澧?-->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="p in platforms" :key="p.name">
        <el-card shadow="never" class="platform-card" @click="startQuickScrape(p)">
          <div class="pf-icon">{{ p.icon }}</div>
          <div class="pf-name">{{ p.name }}</div>
          <div class="pf-count">{{ p.count }} 娴犺泛鏅㈤崫?/div>
          <div class="pf-rate" :style="{ color: p.rate > 80 ? '#52c41a' : '#faad14' }">閹存劕濮涢悳?{{ p.rate }}%</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 闁插洭娉︽禒璇插閸掓銆?-->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="panel-header">
              <span>棣冩惖 闁插洭娉︽禒璇插</span>
              <el-button text size="small" @click="refreshJobs">閸掗攱鏌?/el-button>
            </div>
          </template>
          <el-table :data="jobs" size="small" max-height="350">
            <el-table-column prop="keyword" label="閸忔娊鏁拠? min-width="120"/>
            <el-table-column prop="platform" label="楠炲啿褰? width="110">
              <template #default="{ row }">
                <el-tag size="small">{{ row.platform }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="collected" label="瀹告煡鍣伴梿? width="80"/>
            <el-table-column prop="imported" label="瀹告彃顕遍崗? width="80"/>
            <el-table-column prop="status" label="閻樿埖鈧? width="100">
              <template #default="{ row }">
                <el-tag :type="row.statusType" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="閺冨爼妫? width="140"/>
            <el-table-column label="閹垮秳缍? width="180">
              <template #default="{ row }">
                <el-button text size="small" type="primary" @click="previewProducts(row)">閺屻儳婀?/el-button>
                <el-button text size="small" type="success" v-if="row.status === '瀹告彃鐣幋?" @click="importToMall(row)">鐎电厧鍙?/el-button>
                <el-button text size="small" type="warning" @click="uploadToCOS(row)">娑撳﹣绱禖OS</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- COS閻樿埖鈧?-->
      <el-col :span="8">
        <el-card shadow="never">
          <template #header><span>閳戒緤绗?閼垫崘顔嗘禍鎱峅S</span></template>
          <div class="cos-status">
            <div class="cos-item">
              <span class="cos-label">鐎涙ê鍋嶅?/span>
              <span class="cos-val">{{ cosConfig.bucket }}</span>
            </div>
            <div class="cos-item">
              <span class="cos-label">閸︽澘鐓?/span>
              <span class="cos-val">{{ cosConfig.region }}</span>
            </div>
            <div class="cos-item">
              <span class="cos-label">瀹歌弓绗傛导鐘叉禈閻?/span>
              <span class="cos-val highlight">{{ cosStats.uploaded }}</span>
            </div>
            <div class="cos-item">
              <span class="cos-label">鐎涙ê鍋嶉悽銊╁櫤</span>
              <span class="cos-val">{{ cosStats.usage }}</span>
            </div>
            <div class="cos-item">
              <span class="cos-label">閻樿埖鈧?/span>
              <el-tag type="success" size="small">瀹歌尪绻涢幒?/el-tag>
            </div>
            <el-divider style="margin:16px 0"/>
            <el-button type="primary" style="width:100%" @click="testCOS">濞村鐦潻鐐村复</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 闁插洭娉﹂崯鍡楁惂妫板嫯顫?-->
    <el-card shadow="never" v-if="previewVisible">
      <template #header>
        <div class="panel-header">
          <span>棣冩煠閿?瀹告煡鍣伴梿鍡楁櫌閸濅線顣╃憴?/span>
          <el-button text size="small" @click="previewVisible = false">閸忔娊妫?/el-button>
        </div>
      </template>
      <div class="product-grid">
        <div v-for="p in previewProducts_data" :key="p.id" class="product-card">
          <div class="prod-img" :style="{ background: p.color }">{{ p.icon }}</div>
          <div class="prod-info">
            <div class="prod-title">{{ p.title }}</div>
            <div class="prod-price">{{ p.price }}</div>
            <div class="prod-source">{{ p.source }}</div>
          </div>
          <el-tag size="small" :type="p.uploaded ? 'success' : 'info'">{{ p.uploaded ? '瀹歌弓绗傛导? : '瀵板懍绗傛导? }}</el-tag>
        </div>
      </div>
    </el-card>

    <!-- 閺傛澘缂撻柌鍥肠鐎电鐦藉?-->
    <el-dialog v-model="showCreateDialog" title="閺傛澘缂撻柌鍥肠娴犺濮? width="500px">
      <el-form label-width="80px">
        <el-form-item label="楠炲啿褰?>
          <el-select v-model="newJob.platform" style="width:100%">
            <el-option label="eBay" value="eBay"/>
            <el-option label="AliExpress" value="AliExpress"/>
            <el-option label="Amazon" value="Amazon"/>
            <el-option label="1688" value="1688"/>
          </el-select>
        </el-form-item>
        <el-form-item label="閸忔娊鏁拠?>
          <el-input v-model="newJob.keyword" placeholder="婵″偊绱癷Phone 15 閹靛婧€婢?/>
        </el-form-item>
        <el-form-item label="閺佷即鍣?>
          <el-input-number v-model="newJob.count" :min="1" :max="500"/>
        </el-form-item>
        <el-form-item label="閸濅胶琚?>
          <el-input v-model="newJob.category" placeholder="婵″偊绱伴幍瀣簚閺佹壆鐖?/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">閸欐牗绉?/el-button>
        <el-button type="primary" @click="createJob">瀵偓婵鍣伴梿?/el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api/index'

const showCreateDialog = ref(false)
const previewVisible = ref(false)
const loadingJobs = ref(false)

const newJob = reactive({
  platform: 'ebay',
  keyword: '',
  count: 50,
})

const cosStats = reactive({ uploaded: '0', usage: '0' })

const platforms = ref([
  { name: 'eBay', icon: '馃寪', count: 0, rate: 0 },
  { name: 'AliExpress', icon: '馃泹锔?, count: 0, rate: 0 },
])

const jobs = ref([])
const previewProducts_data = ref([])

async function fetchJobs() {
  loadingJobs.value = true
  try {
    const { data } = await agentApi.get('/agent/scraper/jobs')
    jobs.value = (data.jobs || []).map(function(j) {
      return {
        id: j.job_id || j.id,
        keyword: j.keyword || '',
        platform: j.platform || '',
        collected: j.found \|\| 0,
        imported: j.uploaded \|\| 0,
        status: j.status === 'completed' ? '宸插畬鎴? : j.status === 'running' ? '閲囬泦涓?..' : '鎺掗槦涓?..',
        statusType: j.status === 'done' ? 'success' : j.status === 'failed' ? 'danger' : 'warning',
        time: j.created_at || ''
      }
    })
  } catch { /* 鍚庣鏈氨缁?*/ }
  loadingJobs.value = false
}

async function fetchSources() {
  try {
    const { data } = await agentApi.get('/agent/scraper/sources')
    if (data.sources) {
      platforms.value = data.sources.map(function(s) {
        return { name: s.name || s.id, icon: '馃寪', count: 0, rate: s.status === 'ready' ? 90 : 0, id: s.id }
      })
    }
  } catch {}
}

async function startQuickScrape(platform) {
  try {
    await agentApi.post('/agent/scraper/jobs', {
      platform: platform.id || platform.name.toLowerCase().replace(/\s/g,''),
      keyword: 'trending',
      max_items: 20
    })
    ElMessage.success('宸蹭粠 ' + platform.name + ' 寮€濮嬪揩閫熼噰闆?)
    fetchJobs()
  } catch {
    ElMessage.error('閲囬泦鍚姩澶辫触')
  }
}

async function refreshJobs() {
  await fetchJobs()
  ElMessage.success('浠诲姟鍒楄〃宸插埛鏂?)
}

async function previewProducts(row) {
  previewVisible.value = true
  try {
    const { data } = await agentApi.get('/agent/scraper/products')
    previewProducts_data.value = (data.items || []).slice(0, 10).map(function(p, i) {
      return {
        id: p.id || i + 1,
        icon: '馃摝',
        title: p.title || '鍟嗗搧',
        price: '楼' + (p.price || 0),
        source: p.source || '',
        uploaded: !!p.image_url,
        color: '#f6ffed'
      }
    })
  } catch {
    ElMessage.info('鏌ョ湅浠诲姟: ' + row.keyword)
  }
}

async function importToMall(row) {
  try {
    await agentApi.post('/agent/scraper/products/import', { product_ids: [row.id] })
    ElMessage.success(row.keyword + ' 宸插鍏ュ晢鍩?)
  } catch {
    ElMessage.error('瀵煎叆澶辫触')
  }
}

function uploadToCOS(row) {
  ElMessage.success(row.keyword + ' 鐨勫浘鐗囧凡涓婁紶COS')
}

async function createJob() {
  showCreateDialog.value = false
  try {
    await agentApi.post('/agent/scraper/jobs', {
      platform: newJob.platform,
      keyword: newJob.keyword || '鏂板搧',
      max_items: newJob.count || 20
    })
    ElMessage.success('閲囬泦浠诲姟宸插垱寤猴細' + newJob.platform + ' > ' + newJob.keyword)
    fetchJobs()
  } catch {
    ElMessage.error('鍒涘缓浠诲姟澶辫触')
  }
}

onMounted(function() {
  fetchJobs()
  fetchSources()
}


async function fetchCOSStatus() {
  try {
    const { data } = await agentApi.get('/agent/scraper/cos-status')
    if (data.status) {
      cosConfig.value = { bucket: data.status.bucket || 'N/A', region: data.status.region || 'N/A' }
      cosStats.value = { uploaded: data.status.uploaded || 0, usage: data.status.usage || '0 MB' }
    }
  } catch {}
}
  fetchCOSStatus())
</script>

<style scoped>
.page-container { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-header h1 { font-size: 20px; margin: 0 0 4px; color: var(--text-primary); }
.page-header p { font-size: 13px; color: var(--text-muted); margin: 0; }
.header-actions { display: flex; gap: 8px; }

.platform-card { text-align: center; border-radius: 12px; cursor: pointer; transition: all 0.2s; border: 2px solid transparent; }
.platform-card:hover { border-color: var(--color-primary-light); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
.pf-icon { font-size: 32px; margin-bottom: 8px; }
.pf-name { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.pf-count { font-size: 12px; color: var(--text-muted); margin: 4px 0; }
.pf-rate { font-size: 12px; font-weight: 500; }

.panel-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 14px; }

.cos-status { display: flex; flex-direction: column; gap: 12px; }
.cos-item { display: flex; justify-content: space-between; align-items: center; }
.cos-label { font-size: 13px; color: var(--text-secondary); }
.cos-val { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.cos-val.highlight { color: #667eea; font-size: 18px; font-weight: 700; }

.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.product-card { display: flex; align-items: center; gap: 10px; padding: 12px; border-radius: 8px; background: var(--bg-page); }
.prod-img { width: 48px; height: 48px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
.prod-info { flex: 1; min-width: 0; }
.prod-title { font-size: 12px; font-weight: 500; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.prod-price { font-size: 13px; font-weight: 700; color: #ff4d4f; margin: 2px 0; }
.prod-source { font-size: 11px; color: var(--text-muted); }
</style>
