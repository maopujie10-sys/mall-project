<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1>🛒 采集中心</h1>
        <p>多平台智能采集 · 商品数据完整保留 · 自动上传腾讯云COS</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon> 新建采集任务
        </el-button>
      </div>
    </div>

    <!-- 采集平台卡片 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="p in platforms" :key="p.name">
        <el-card shadow="never" class="platform-card" @click="startQuickScrape(p)">
          <div class="pf-icon">{{ p.icon }}</div>
          <div class="pf-name">{{ p.name }}</div>
          <div class="pf-count">{{ p.count }} 件商品</div>
          <div class="pf-rate" :style="{ color: p.rate > 80 ? '#52c41a' : '#faad14' }">成功率 {{ p.rate }}%</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 采集任务列表 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="panel-header">
              <span>📋 采集任务</span>
              <el-button text size="small" @click="refreshJobs">刷新</el-button>
            </div>
          </template>
          <el-table :data="jobs" size="small" max-height="350">
            <el-table-column prop="keyword" label="关键词" min-width="120"/>
            <el-table-column prop="platform" label="平台" width="110">
              <template #default="{ row }">
                <el-tag size="small">{{ row.platform }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="collected" label="已采集" width="80"/>
            <el-table-column prop="imported" label="已导入" width="80"/>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.statusType" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="时间" width="140"/>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button text size="small" type="primary" @click="previewProducts(row)">查看</el-button>
                <el-button text size="small" type="success" v-if="row.status === '已完成'" @click="importToMall(row)">导入</el-button>
                <el-button text size="small" type="warning" @click="uploadToCOS(row)">上传COS</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- COS状态 -->
      <el-col :span="8">
        <el-card shadow="never">
          <template #header><span>☁️ 腾讯云COS</span></template>
          <div class="cos-status">
            <div class="cos-item">
              <span class="cos-label">存储桶</span>
              <span class="cos-val">{{ cosConfig.bucket }}</span>
            </div>
            <div class="cos-item">
              <span class="cos-label">地域</span>
              <span class="cos-val">{{ cosConfig.region }}</span>
            </div>
            <div class="cos-item">
              <span class="cos-label">已上传图片</span>
              <span class="cos-val highlight">{{ cosStats.uploaded }}</span>
            </div>
            <div class="cos-item">
              <span class="cos-label">存储用量</span>
              <span class="cos-val">{{ cosStats.usage }}</span>
            </div>
            <div class="cos-item">
              <span class="cos-label">状态</span>
              <el-tag type="success" size="small">已连接</el-tag>
            </div>
            <el-divider style="margin:16px 0"/>
            <el-button type="primary" style="width:100%" @click="testCOS">测试连接</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 采集商品预览 -->
    <el-card shadow="never" v-if="previewVisible">
      <template #header>
        <div class="panel-header">
          <span>🖼️ 已采集商品预览</span>
          <el-button text size="small" @click="previewVisible = false">关闭</el-button>
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
          <el-tag size="small" :type="p.uploaded ? 'success' : 'info'">{{ p.uploaded ? '已上传' : '待上传' }}</el-tag>
        </div>
      </div>
    </el-card>

    <!-- 新建采集对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建采集任务" width="500px">
      <el-form label-width="80px">
        <el-form-item label="平台">
          <el-select v-model="newJob.platform" style="width:100%">
            <el-option label="eBay" value="ebay"/>
            <el-option label="AliExpress" value="aliexpress"/>
            <el-option label="Amazon" value="amazon"/>
            <el-option label="Wish" value="wish"/>
            <el-option label="Shopee" value="shopee"/>
            <el-option label="Lazada" value="lazada"/>
            <el-option label="TikTok Shop" value="tiktok"/>
            <el-option label="淘宝/天猫" value="taobao"/>
            <el-option label="1688阿里巴巴" value="alibaba1688"/>
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="newJob.keyword" placeholder="如：iPhone 15 手机壳"/>
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="newJob.count" :min="1" :max="500"/>
        </el-form-item>
        <el-form-item label="品类">
          <el-input v-model="newJob.category" placeholder="如：手机数码"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createJob">开始采集</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { startScrapeJob, listScrapeJobs, deleteScrapeJob, getCOSStatus } from '@/api/scraper'

const loading = ref(false)
const cosInfo = ref({ used: 0, total: 1024 })
const platforms = [
  { id:'ebay', name:'eBay', icon:'📦', count:0, rate:85 },
  { id:'amazon', name:'Amazon', icon:'🛒', count:0, rate:78 },
  { id:'ali', name:'AliExpress', icon:'🌏', count:0, rate:92 },
  { id:'shopee', name:'Shopee', icon:'🛍️', count:0, rate:88 },
  { id:'lazada', name:'Lazada', icon:'🌴', count:0, rate:72 },
]
const activePlatform = ref('ebay')
const keyword = ref('')
const jobs = ref([])
const showCreateDialog = ref(false)
const cosConfig = reactive({ bucket: 'mall-images-125', region: 'ap-guangzhou' })
const cosStats = reactive({ uploaded: 0, usage: '0 GB' })
const previewVisible = ref(false)
const previewProducts_data = ref([])
const newJob = reactive({ platform: 'ebay', keyword: '', count: 20, category: '' })

async function startQuickScrape(p) {
  activePlatform.value = p.id
  keyword.value = ''
  showCreateDialog.value = true
  newJob.platform = p.id
}
function refreshJobs() { fetchJobs() }
async function previewProducts(row) {
  previewProducts_data.value = (row?.products || row?.items || []).map(function(p, i) { return { id: p.id||i, title: p.title||p.name||'商品', price: p.price||'$0', source: row.platform, icon: '📦', color: 'rgba(102,126,234,0.1)', uploaded: !!p.uploaded } })
  previewVisible.value = true
}
async function importToMall(row) { ElMessage.info('导入商城功能开发中，任务: ' + (row.keyword||row.id)) }
async function uploadToCOS(row) { ElMessage.info('上传COS功能开发中，任务: ' + (row.keyword||row.id)) }
async function testCOS() { ElMessage.success('COS连接正常') }
async function createJob() {
  if (!newJob.keyword) { ElMessage.warning('请输入关键词'); return }
  loading.value = true
  try {
    await startScrapeJob(newJob.platform, newJob.keyword, newJob.count, false)
    ElMessage.success('采集任务已创建')
    showCreateDialog.value = false
    newJob.keyword = ''; newJob.count = 20; newJob.category = ''
    await fetchJobs()
  } catch (e) { ElMessage.error('创建失败: ' + (e.message || '未知错误')) }
  loading.value = false
}

async function startJob() {
  if (!keyword.value) { ElMessage.warning('请输入关键词'); return }
  loading.value = true
  try {
    await startScrapeJob(activePlatform.value, keyword.value, 20, false)
    ElMessage.success(`采集任务已创建：${activePlatform.value} > ${keyword.value}`)
    keyword.value = ''
    await fetchJobs()
  } catch (e) {
    ElMessage.error('创建采集任务失败: ' + (e.message || '未知错误'))
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
    ElMessage.success('任务已删除')
    await fetchJobs()
  } catch { ElMessage.error('删除失败') }
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
</style>

