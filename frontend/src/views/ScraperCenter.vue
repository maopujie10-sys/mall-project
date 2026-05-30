<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1>馃洅 閲囬泦涓績</h1>
        <p>澶氬钩鍙版櫤鑳介噰闆?路 鍟嗗搧鏁版嵁瀹屾暣淇濈暀 路 鑷姩涓婁紶鑵捐浜慍OS</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon> 鏂板缓閲囬泦浠诲姟
        </el-button>
      </div>
    </div>

    <!-- 閲囬泦骞冲彴鍗＄墖 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="p in platforms" :key="p.name">
        <el-card shadow="never" class="platform-card" @click="startQuickScrape(p)">
          <div class="pf-icon">{{ p.icon }}</div>
          <div class="pf-name">{{ p.name }}</div>
          <div class="pf-count">{{ p.count }} 浠跺晢鍝?/div>
          <div class="pf-rate" :style="{ color: p.rate > 80 ? '#52c41a' : '#faad14' }">鎴愬姛鐜?{{ p.rate }}%</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 閲囬泦浠诲姟鍒楄〃 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="panel-header">
              <span>馃搵 閲囬泦浠诲姟</span>
              <el-button text size="small" @click="refreshJobs">鍒锋柊</el-button>
            </div>
          </template>
          <el-table :data="jobs" size="small" max-height="350">
            <el-table-column prop="keyword" label="鍏抽敭璇? min-width="120"/>
            <el-table-column prop="platform" label="骞冲彴" width="110">
              <template #default="{ row }">
                <el-tag size="small">{{ row.platform }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="collected" label="宸查噰闆? width="80"/>
            <el-table-column prop="imported" label="宸插鍏? width="80"/>
            <el-table-column prop="status" label="鐘舵€? width="100">
              <template #default="{ row }">
                <el-tag :type="row.statusType" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="鏃堕棿" width="140"/>
            <el-table-column label="鎿嶄綔" width="180">
              <template #default="{ row }">
                <el-button text size="small" type="primary" @click="previewProducts(row)">鏌ョ湅</el-button>
                <el-button text size="small" type="success" v-if="row.status === '宸插畬鎴?" @click="importToMall(row)">瀵煎叆</el-button>
                <el-button text size="small" type="warning" @click="uploadToCOS(row)">涓婁紶COS</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- COS鐘舵€?-->
      <el-col :span="8">
        <el-card shadow="never">
          <template #header><span>鈽侊笍 鑵捐浜慍OS</span></template>
          <div class="cos-status">
            <div class="cos-item">
              <span class="cos-label">瀛樺偍妗?/span>
              <span class="cos-val">{{ cosConfig.bucket }}</span>
            </div>
            <div class="cos-item">
              <span class="cos-label">鍦板煙</span>
              <span class="cos-val">{{ cosConfig.region }}</span>
            </div>
            <div class="cos-item">
              <span class="cos-label">宸蹭笂浼犲浘鐗?/span>
              <span class="cos-val highlight">{{ cosStats.uploaded }}</span>
            </div>
            <div class="cos-item">
              <span class="cos-label">瀛樺偍鐢ㄩ噺</span>
              <span class="cos-val">{{ cosStats.usage }}</span>
            </div>
            <div class="cos-item">
              <span class="cos-label">鐘舵€?/span>
              <el-tag type="success" size="small">宸茶繛鎺?/el-tag>
            </div>
            <el-divider style="margin:16px 0"/>
            <el-button type="primary" style="width:100%" @click="testCOS">娴嬭瘯杩炴帴</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 閲囬泦鍟嗗搧棰勮 -->
    <el-card shadow="never" v-if="previewVisible">
      <template #header>
        <div class="panel-header">
          <span>馃柤锔?宸查噰闆嗗晢鍝侀瑙?/span>
          <el-button text size="small" @click="previewVisible = false">鍏抽棴</el-button>
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
          <el-tag size="small" :type="p.uploaded ? 'success' : 'info'">{{ p.uploaded ? '宸蹭笂浼? : '寰呬笂浼? }}</el-tag>
        </div>
      </div>
    </el-card>

    <!-- 鏂板缓閲囬泦瀵硅瘽妗?-->
    <el-dialog v-model="showCreateDialog" title="鏂板缓閲囬泦浠诲姟" width="500px">
      <el-form label-width="80px">
        <el-form-item label="骞冲彴">
          <el-select v-model="newJob.platform" style="width:100%">
            <el-option label="eBay" value="ebay"/>
            <el-option label="AliExpress" value="aliexpress"/>
            <el-option label="Amazon" value="amazon"/>
            <el-option label="Wish" value="wish"/>
            <el-option label="Shopee" value="shopee"/>
            <el-option label="Lazada" value="lazada"/>
            <el-option label="TikTok Shop" value="tiktok"/>
            <el-option label="娣樺疂/澶╃尗" value="taobao"/>
            <el-option label="1688闃块噷宸村反" value="alibaba1688"/>
          </el-select>
        </el-form-item>
        <el-form-item label="鍏抽敭璇?>
          <el-input v-model="newJob.keyword" placeholder="濡傦細iPhone 15 鎵嬫満澹?/>
        </el-form-item>
        <el-form-item label="鏁伴噺">
          <el-input-number v-model="newJob.count" :min="1" :max="500"/>
        </el-form-item>
        <el-form-item label="鍝佺被">
          <el-input v-model="newJob.category" placeholder="濡傦細鎵嬫満鏁扮爜"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">鍙栨秷</el-button>
        <el-button type="primary" @click="createJob">寮€濮嬮噰闆?/el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api/index'
import { startScrapeJob, listScrapeJobs, deleteScrapeJob, getCOSStatus } from '@/api/scraper'

const loading = ref(false)
const cosInfo = ref({ used: 0, total: 1024 })
const platforms = [
  { id:'ebay', name:'eBay', icon:'馃摝', count:0 },
  { id:'amazon', name:'Amazon', icon:'馃洅', count:0 },
  { id:'ali', name:'AliExpress', icon:'馃審', count:0 },
  { id:'shopee', name:'Shopee', icon:'馃泹锔?, count:0 },
  { id:'lazada', name:'Lazada', icon:'馃尨', count:0 },
]
const activePlatform = ref('ebay')
const keyword = ref('')
const jobs = ref([])

async function startJob() {
  if (!keyword.value) { ElMessage.warning('璇疯緭鍏ュ叧閿瘝'); return }
  loading.value = true
  try {
    await startScrapeJob(activePlatform.value, keyword.value, 20, false)
    ElMessage.success(`閲囬泦浠诲姟宸插垱寤猴細${activePlatform.value} > ${keyword.value}`)
    keyword.value = ''
    await fetchJobs()
  } catch (e) {
    ElMessage.error('鍒涘缓閲囬泦浠诲姟澶辫触: ' + (e.message || '鏈煡閿欒'))
  }
  loading.value = false
}

async function fetchJobs() {
  try {
    const res = await listScrapeJobs()
    if (res?.data?.jobs) jobs.value = res.data.jobs
  } catch {}
}

async function removeJob(jobId) {
  try {
    await deleteScrapeJob(jobId)
    ElMessage.success('浠诲姟宸插垹闄?)
    await fetchJobs()
  } catch { ElMessage.error('鍒犻櫎澶辫触') }
}

async function fetchCOS() {
  try {
    const res = await getCOSStatus()
    if (res?.data) cosInfo.value = res.data
  } catch {}
}

fetchJobs()
fetchCOS()
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
.product-card { display: flex; align-items: center; gap: 10px; padding: 12px; border-radius: 8px; background: rgba(13,16,37,0.55); }
.prod-img { width: 48px; height: 48px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
.prod-info { flex: 1; min-width: 0; }
.prod-title { font-size: 12px; font-weight: 500; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.prod-price { font-size: 13px; font-weight: 700; color: #ff4d4f; margin: 2px 0; }
.prod-source { font-size: 11px; color: var(--text-muted); }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>

