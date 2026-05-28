<template>
  <div class="site-check">
    <h2>缂冩垹鐝拋鍧楁６濡偓濞?/h2>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>濡偓閺屻儳缍夌粩娆忓讲鐠佸潡妫堕幀?/template>
          <el-input v-model="checkUrl" placeholder="鏉堟挸鍙哢RL閹存牕鐓欓崥宥忕礉婵?https://example.com" clearable />
          <el-button type="primary" @click="doCheck" :loading="checkLoading" style="margin-top:8px">濡偓濞?/el-button>
          <el-result v-if="checkResult" :status="checkResult.accessible ? 'success' : 'error'" :title="checkResult.accessible ? '閸欘垵顔栭梻? : '閺冪姵纭剁拋鍧楁６'">
            <template #extra>
              <p>閻樿埖鈧胶鐖? {{ checkResult.status_code }}</p>
              <p>瀵ゆ儼绻? {{ checkResult.latency_ms }}ms</p>
              <p v-if="checkResult.error">闁挎瑨顕? {{ checkResult.error }}</p>
            </template>
          </el-result>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>DNS 閺屻儴顕?/template>
          <el-input v-model="dnsDomain" placeholder="鏉堟挸鍙嗛崺鐔锋倳" clearable />
          <el-button type="primary" @click="doDns" :loading="dnsLoading" style="margin-top:8px">閺屻儴顕?/el-button>
          <pre v-if="dnsResult" class="result-box">{{ dnsResult.records }}</pre>
        </el-card>
      </el-col>
    </el-row>
    <el-card shadow="never" style="margin-top:16px">
      <template #header>SSL 鐠囦椒鍔熷Λ鈧ù?/template>
      <el-input v-model="sslDomain" placeholder="鏉堟挸鍙嗛崺鐔锋倳" clearable style="max-width:400px" />
      <el-button type="primary" @click="doSsl" :loading="sslLoading" style="margin-left:8px">濡偓濞?/el-button>
      <el-descriptions v-if="sslResult && sslResult.cert_info" :column="1" border style="margin-top:12px">
        <el-descriptions-item v-for="(v, k) in sslResult.cert_info" :key="k" :label="k">{{ v }}</el-descriptions-item>
      </el-descriptions>
      <p v-else-if="sslResult && sslResult.error" style="color:red">{{ sslResult.error }}</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api/index'

const url = ref('')
const results = ref([])
const checking = ref(false)

async function checkSite() {
  if (!url.value) { ElMessage.warning('璇疯緭鍏ョ綉鍧€'); return }
  checking.value = true
  try {
    const { data } = await agentApi.post('/site/check', { url: url.value })
    results.value.unshift({ url: url.value, status: data.status_code, accessible: data.accessible, latency: data.latency_ms + 'ms', time: new Date().toTimeString().slice(0,5) })
    ElMessage.success(data.accessible ? '缃戠珯鍙闂? : '缃戠珯寮傚父')
  } catch {
    ElMessage.error('妫€娴嬪け璐?)
  } finally { checking.value = false }
}

async function checkSSL(domain) {
  try {
    const { data } = await agentApi.post('/site/ssl', { domain: domain || url.value })
    ElMessage.success('SSL妫€娴嬪畬鎴?)
  } catch { ElMessage.error('SSL妫€娴嬪け璐?) }
}

onMounted(function() {})
</script>

<style scoped>
.site-check { padding: 24px; }
h2 { margin-bottom: 16px; font-size: 18px; }
.result-box { background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 6px; font-size: 12px; margin-top: 8px; max-height: 200px; overflow: auto; }
</style>
