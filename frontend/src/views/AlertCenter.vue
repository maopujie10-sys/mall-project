<template>
  <div class="alert-center">
    <h2>閸涘﹨顒熸稉顓炵妇</h2>
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6" v-for="s in levelStats" :key="s.level">
        <div class="stat-card" :class="s.level">
          <div class="stat-label">{{ s.name }}</div>
          <div class="stat-num">{{ s.count }}</div>
          <div class="stat-sub">閺堫亣袙閸? {{ s.unresolved }}</div>
        </div>
      </el-col>
    </el-row>
    <el-card shadow="never" style="margin-top:16px">
      <template #header>
        <span>閸涘﹨顒熼崚妤勩€?/span>
        <el-select v-model="filterLevel" size="small" clearable placeholder="缁涙盯鈧鐡戠痪? style="width:120px;margin-left:12px">
          <el-option v-for="(n, k) in levelMap" :key="k" :label="`${k} - ${n}`" :value="k" />
        </el-select>
        <el-button size="small" @click="fetchAlerts" style="margin-left:8px">閸掗攱鏌?/el-button>
      </template>
      <el-table :data="alerts" stripe size="small" empty-text="閺嗗倹妫ら崨濠咁劅">
        <el-table-column label="缁涘楠? width="80">
          <template #default="{row}">
            <el-tag :type="tagType(row.level)" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="閺冨爼妫? width="80" />
        <el-table-column prop="title" label="閺嶅洭顣? min-width="200" />
        <el-table-column prop="detail" label="鐠囷附鍎? min-width="200" show-overflow-tooltip />
        <el-table-column prop="source" label="閺夈儲绨? width="80" />
        <el-table-column label="閻樿埖鈧? width="80">
          <template #default="{row}">
            <el-tag :type="row.resolved ? 'info' : 'danger'" size="small">{{ row.resolved ? '瀹歌尪袙閸? : '閺堫亣袙閸? }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="閹垮秳缍? width="100">
          <template #default="{row}">
            <el-button v-if="!row.resolved" size="small" type="primary" link @click="doResolve(row.id)">鐟欙絽鍠?/el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAlertList, getAlertStats, resolveAlert } from '@/api/alert'
import { ElMessage } from 'element-plus'

const levelMap = { P1: '缁毖勨偓?, P2: '娑撱儵鍣?, P3: '娑撯偓閼?, P4: '鐟欏倸鐧? }
const alerts = ref([])
const stats = ref({})
const filterLevel = ref('')

const levelStats = computed(() => {
  return Object.entries(levelMap).map(([k, v]) => ({
    level: k, name: v,
    count: stats.value[k]?.count || 0,
    unresolved: stats.value[k]?.unresolved || 0,
  }))
})

function tagType(level) {
  return { P1: 'danger', P2: 'warning', P3: 'primary', P4: 'info' }[level] || 'info'
}

async function fetchAlerts() {
  try {
    const params = filterLevel.value ? { level: filterLevel.value } : {}
    const r = await getAlertList(params)
    alerts.value = r.alerts || []
  } catch { ElMessage.error('閼惧嘲褰囬崨濠咁劅婢惰精瑙?) }
}
async function fetchStats() {
  try { const r = await getAlertStats(); stats.value = r.stats || {} } catch {}
}
async function doResolve(id) {
  try { await resolveAlert(id); ElMessage.success('瀹稿弶鐖ｇ拋鎷屝掗崘?); fetchAlerts(); fetchStats() } catch { ElMessage.error('閹垮秳缍旀径杈Е') }
}
onMounted(() => { fetchAlerts(); fetchStats() })
</script>

<style scoped>
.alert-center { padding: 24px; }
h2 { margin-bottom: 16px; font-size: 18px; }
.stats-row { margin-bottom: 0; }
.stat-card { padding: 16px; border-radius: 8px; color: #fff; text-align: center; }
.stat-card.P1 { background: #f56c6c; }
.stat-card.P2 { background: #e6a23c; }
.stat-card.P3 { background: #409eff; }
.stat-card.P4 { background: #909399; }
.stat-label { font-size: 13px; opacity: 0.9; }
.stat-num { font-size: 28px; font-weight: 700; margin: 4px 0; }
.stat-sub { font-size: 12px; opacity: 0.8; }
</style>
