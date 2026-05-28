<template>
  <div class="nginx-panel">
    <h2>Nginx 缁狅紕鎮?/h2>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>鏉╂稓鈻奸悩鑸碘偓?/template>
          <div v-if="status !== null">
            <el-tag :type="status.running ? 'success' : 'danger'" size="large">
              {{ status.running ? '鏉╂劘顢戞稉? : '瀹告彃浠犲? }}
            </el-tag>
            <pre class="log-box">{{ status.detail }}</pre>
          </div>
          <el-button @click="fetchStatus" :loading="loading">閸掗攱鏌?/el-button>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>闁板秶鐤嗗ù瀣槸</template>
          <el-button @click="testConfig" :loading="configLoading">nginx -t</el-button>
          <pre v-if="configResult" class="log-box" :style="{color: configResult.ok ? 'green' : 'red'}">{{ configResult.output }}</pre>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>闁插秷娴?/template>
          <el-button type="warning" @click="doReload" :loading="reloadLoading">闁插秷娴?Nginx</el-button>
          <pre v-if="reloadResult" class="log-box">{{ reloadResult.output }}</pre>
        </el-card>
      </el-col>
    </el-row>
    <el-card shadow="never" style="margin-top:16px">
      <template #header>
        <span>闁挎瑨顕ら弮銉ョ箶</span>
        <el-select v-model="logType" size="small" style="width:120px;margin-left:12px">
          <el-option label="闁挎瑨顕ら弮銉ョ箶" value="error" />
          <el-option label="鐠佸潡妫堕弮銉ョ箶" value="access" />
        </el-select>
        <el-button size="small" @click="fetchLogs" style="margin-left:8px">閸掗攱鏌?/el-button>
      </template>
      <pre class="log-box" style="max-height:400px">{{ logs }}</pre>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getNginxStatus, testNginxConfig, getNginxLogs, reloadNginx } from '@/api/nginx'
import { ElMessage } from 'element-plus'

const status = ref(null)
const loading = ref(false)
const configResult = ref(null)
const configLoading = ref(false)
const reloadResult = ref(null)
const reloadLoading = ref(false)
const logs = ref('')
const logType = ref('error')

async function fetchStatus() {
  loading.value = true
  try { status.value = await getNginxStatus() } catch { ElMessage.error('閼惧嘲褰囬悩鑸碘偓浣搞亼鐠?) }
  loading.value = false
}
async function testConfig() {
  configLoading.value = true
  try { configResult.value = await testNginxConfig() } catch { ElMessage.error('濞村鐦径杈Е') }
  configLoading.value = false
}
async function doReload() {
  reloadLoading.value = true
  try { reloadResult.value = await reloadNginx(); ElMessage.success('闁插秷娴囬幋鎰') } catch { ElMessage.error('闁插秷娴囨径杈Е') }
  reloadLoading.value = false
}
async function fetchLogs() {
  try { const r = await getNginxLogs({ lines: 50, type: logType.value }); logs.value = r.content } catch { ElMessage.error('閼惧嘲褰囬弮銉ョ箶婢惰精瑙?) }
}
fetchStatus()
fetchLogs()
</script>

<style scoped>
.nginx-panel { padding: 24px; }
.log-box { background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 6px; font-size: 12px; margin-top: 8px; max-height: 200px; overflow: auto; white-space: pre-wrap; word-break: break-all; }
h2 { margin-bottom: 16px; font-size: 18px; }
</style>
