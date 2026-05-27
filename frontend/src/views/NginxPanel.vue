<template>
  <div class="nginx-panel">
    <h2>Nginx 管理</h2>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>进程状态</template>
          <div v-if="status !== null">
            <el-tag :type="status.running ? 'success' : 'danger'" size="large">
              {{ status.running ? '运行中' : '已停止' }}
            </el-tag>
            <pre class="log-box">{{ status.detail }}</pre>
          </div>
          <el-button @click="fetchStatus" :loading="loading">刷新</el-button>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>配置测试</template>
          <el-button @click="testConfig" :loading="configLoading">nginx -t</el-button>
          <pre v-if="configResult" class="log-box" :style="{color: configResult.ok ? 'green' : 'red'}">{{ configResult.output }}</pre>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>重载</template>
          <el-button type="warning" @click="doReload" :loading="reloadLoading">重载 Nginx</el-button>
          <pre v-if="reloadResult" class="log-box">{{ reloadResult.output }}</pre>
        </el-card>
      </el-col>
    </el-row>
    <el-card shadow="never" style="margin-top:16px">
      <template #header>
        <span>错误日志</span>
        <el-select v-model="logType" size="small" style="width:120px;margin-left:12px">
          <el-option label="错误日志" value="error" />
          <el-option label="访问日志" value="access" />
        </el-select>
        <el-button size="small" @click="fetchLogs" style="margin-left:8px">刷新</el-button>
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
  try { status.value = await getNginxStatus() } catch { ElMessage.error('获取状态失败') }
  loading.value = false
}
async function testConfig() {
  configLoading.value = true
  try { configResult.value = await testNginxConfig() } catch { ElMessage.error('测试失败') }
  configLoading.value = false
}
async function doReload() {
  reloadLoading.value = true
  try { reloadResult.value = await reloadNginx(); ElMessage.success('重载成功') } catch { ElMessage.error('重载失败') }
  reloadLoading.value = false
}
async function fetchLogs() {
  try { const r = await getNginxLogs({ lines: 50, type: logType.value }); logs.value = r.content } catch { ElMessage.error('获取日志失败') }
}
fetchStatus()
fetchLogs()
</script>

<style scoped>
.nginx-panel { padding: 24px; }
.log-box { background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 6px; font-size: 12px; margin-top: 8px; max-height: 200px; overflow: auto; white-space: pre-wrap; word-break: break-all; }
h2 { margin-bottom: 16px; font-size: 18px; }
</style>
