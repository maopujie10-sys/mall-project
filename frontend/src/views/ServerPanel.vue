<template>
  <div class="page-container">
    <div class="page-header">
      <h2>閺堝秴濮熼崳銊ф磧閹貉囨桨閺?/h2>
      <p>缁崵绮虹挧鍕爱 璺?鏉╂稓鈻肩粻锛勬倞 璺?缁旑垰褰涢惄鎴濇儔</p>
    </div>

    <el-alert v-if="error" :title="error" type="error" show-icon closable @close="error=null" style="margin-bottom:16px" />

    <!-- 閹稿洦鐖ｉ崡锛勫 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">CPU 娴ｈ法鏁ら悳?/div>
          <div class="metric-value">{{ systemMetrics.cpu }}%</div>
          <el-progress :percentage="systemMetrics.cpu" :color="cpuColor" :show-text="false" style="margin-top: 12px;" />
          <div class="metric-sub">4 閺嶇绺?璺?{{ systemMetrics.cpuCores }} 缁捐法鈻?/div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">閸愬懎鐡ㄦ担璺ㄦ暏</div>
          <div class="metric-value">{{ systemMetrics.memory }}%</div>
          <el-progress :percentage="systemMetrics.memory" :color="memColor" :show-text="false" style="margin-top: 12px;" />
          <div class="metric-sub">瀹歌尙鏁?{{ systemMetrics.memUsed }} / 閹槒顓?{{ systemMetrics.memTotal }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">绾句胶娲忔担璺ㄦ暏</div>
          <div class="metric-value">{{ systemMetrics.disk }}%</div>
          <el-progress :percentage="systemMetrics.disk" :color="diskColor" :show-text="false" style="margin-top: 12px;" />
          <div class="metric-sub">瀹歌尙鏁?{{ systemMetrics.diskUsed }} / 閹槒顓?{{ systemMetrics.diskTotal }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">缁崵绮虹拹鐔绘祰</div>
          <div class="metric-value">{{ systemMetrics.loadAvg }}</div>
          <div class="metric-sub">1min / 5min / 15min</div>
          <div style="margin-top: 8px; display: flex; gap: 8px;">
            <span class="status-dot online"><span class="dot"></span>鏉╂劘顢戝锝呯埗</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 鏉╂稓鈻奸崚妤勩€?+ 缁旑垰褰涢惄鎴濇儔 -->
    <el-row :gutter="16">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: 600;">鏉╂稓鈻奸崚妤勩€?/span>
              <el-button text type="primary" size="small" @click="refreshAll" :loading="loading">
                <el-icon><Refresh /></el-icon> 閸掗攱鏌?
              </el-button>
            </div>
          </template>
          <el-table :data="processes" style="width: 100%;" size="small" stripe>
            <template #empty>
              <el-empty description="閺嗗倹妫ゆ潻娑氣柤閺佺増宓? :image-size="60" />
            </template>
            <el-table-column prop="name" label="鏉╂稓鈻奸崥宥囆? min-width="140">
              <template #default="{ row }">
                <span style="display: flex; align-items: center; gap: 6px;">
                  <span class="status-dot" :class="row.status === 'running' ? 'online' : 'offline'">
                    <span class="dot"></span>
                  </span>
                  {{ row.name }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="pid" label="PID" width="80" />
            <el-table-column prop="cpu" label="CPU %" width="80">
              <template #default="{ row }">
                <span :style="{ color: row.cpu > 50 ? 'var(--color-danger)' : row.cpu > 20 ? 'var(--color-warning)' : 'var(--text-primary)' }">
                  {{ row.cpu }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="mem" label="閸愬懎鐡?%" width="90">
              <template #default="{ row }">
                <span :style="{ color: row.mem > 70 ? 'var(--color-danger)' : row.mem > 40 ? 'var(--color-warning)' : 'var(--text-primary)' }">
                  {{ row.mem }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="uptime" label="鏉╂劘顢戦弮鍫曟？" width="120" />
            <el-table-column prop="status" label="閻樿埖鈧? width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'running' ? 'success' : 'danger'" size="small" effect="light">
                  {{ row.status === 'running' ? '鏉╂劘顢戞稉? : '瀹告彃浠犲? }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>
            <span style="font-weight: 600;">缁旑垰褰涢惄鎴濇儔</span>
          </template>
          <div class="port-list">
            <el-empty v-if="ports.length===0" description="閺嗗倹妫ょ粩顖氬經閺佺増宓? :image-size="60" style="padding:20px 0;" />
            <template v-else>
            <div v-for="port in ports" :key="port.port" class="port-item">
              <div class="port-info">
                <span class="status-dot" :class="port.listening ? 'online' : 'offline'">
                  <span class="dot"></span>
                </span>
                <div>
                  <div class="port-name">{{ port.service }}</div>
                  <div class="port-detail">{{ port.port }} 璺?{{ port.protocol }}</div>
                </div>
              </div>
              <el-tag size="small" :type="port.listening ? 'success' : 'danger'" effect="light">
                {{ port.listening ? '閻╂垵鎯夋稉? : '閺堫亞娲冮崥? }}
              </el-tag>
            </div>
            </template>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useServerStore } from '@/stores/server'
import { storeToRefs } from 'pinia'

const serverStore = useServerStore()
const { systemMetrics, processes, ports, loading, cpuColor, memColor, diskColor, error } = storeToRefs(serverStore)

let pollTimer = null

const refreshAll = async () => {
  await serverStore.fetchAll()
  if (!error.value) {
    ElMessage.success('閺佺増宓佸鎻掑煕閺?)
  }
}

onMounted(async () => {
  await serverStore.fetchAll()
  pollTimer = setInterval(() => serverStore.fetchAll(), 10000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.port-list { display: flex; flex-direction: column; }
.port-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}
.port-item:last-child { border-bottom: none; }
.port-info { display: flex; align-items: center; gap: 10px; }
.port-name { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.port-detail { font-size: 12px; color: var(--text-muted); }
</style>
