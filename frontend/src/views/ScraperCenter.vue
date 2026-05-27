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
            <el-option label="eBay" value="eBay"/>
            <el-option label="AliExpress" value="AliExpress"/>
            <el-option label="Amazon" value="Amazon"/>
            <el-option label="1688" value="1688"/>
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
import { ElMessage } from 'element-plus'

const showCreateDialog = ref(false)
const previewVisible = ref(false)

const newJob = reactive({
  platform: 'eBay',
  keyword: '',
  count: 50,
  category: '',
})

const cosConfig = {
  bucket: 'shangchengtupian-1435149418',
  region: 'ap-singapore',
}

const cosStats = {
  uploaded: '1,247 张',
  usage: '2.3 GB',
}

const platforms = [
  { name:'eBay', icon:'🌍', count:845, rate:92 },
  { name:'AliExpress', icon:'🛍️', count:623, rate:85 },
  { name:'Amazon', icon:'📦', count:340, rate:88 },
  { name:'1688', icon:'🏭', count:210, rate:76 },
]

const jobs = reactive([
  { id:1, keyword:'iPhone 15 配件', platform:'eBay', collected:50, imported:35, status:'已完成', statusType:'success', time:'2024-05-28 14:32' },
  { id:2, keyword:'夏季T恤男', platform:'AliExpress', collected:80, imported:0, status:'已完成', statusType:'success', time:'2024-05-28 12:15' },
  { id:3, keyword:'无线蓝牙耳机', platform:'Amazon', collected:30, imported:30, status:'已完成', statusType:'success', time:'2024-05-28 10:08' },
  { id:4, keyword:'瑜伽垫', platform:'1688', collected:0, imported:0, status:'采集中...', statusType:'warning', time:'2024-05-28 14:45' },
])

const previewProducts_data = [
  { id:1, icon:'📱', title:'iPhone 15 Pro 透明保护壳', price:'¥29.90', source:'eBay', uploaded:true, color:'#e6f7ff' },
  { id:2, icon:'🎧', title:'蓝牙5.3无线耳机', price:'¥159.00', source:'Amazon', uploaded:true, color:'#f6ffed' },
  { id:3, icon:'⌚', title:'Apple Watch 充电支架', price:'¥89.00', source:'eBay', uploaded:false, color:'#fff7e6' },
  { id:4, icon:'🔌', title:'USB-C 快充数据线 2m', price:'¥19.90', source:'AliExpress', uploaded:true, color:'#e6f7ff' },
  { id:5, icon:'🧴', title:'韩国防晒霜 SPF50+', price:'¥89.00', source:'Amazon', uploaded:false, color:'#f6ffed' },
]

function startQuickScrape(platform) {
  ElMessage.success(`已从 ${platform.name} 开始快速采集`)
}

function refreshJobs() { ElMessage.success('任务列表已刷新') }
function previewProducts(row) {
  previewVisible.value = true
  ElMessage.info(`查看任务: ${row.keyword}`)
}
function importToMall(row) {
  ElMessage.success(`${row.keyword} 已导入商城商品库`)
}
function uploadToCOS(row) {
  ElMessage.success(`${row.keyword} 的图片已上传腾讯云COS`)
}
function testCOS() {
  ElMessage.success('腾讯云COS连接正常！')
}
function createJob() {
  showCreateDialog.value = false
  jobs.unshift({
    id: Date.now(),
    keyword: newJob.keyword || '新采集',
    platform: newJob.platform,
    collected: 0,
    imported: 0,
    status: '排队中...',
    statusType: 'info',
    time: new Date().toLocaleString(),
  })
  ElMessage.success(`采集任务已创建：${newJob.platform} > ${newJob.keyword}`)
}
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
