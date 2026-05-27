<template>
  <div class="site-check">
    <h2>缃戠珯璁块棶妫€娴?/h2>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>妫€鏌ョ綉绔欏彲璁块棶鎬?/template>
          <el-input v-model="checkUrl" placeholder="杈撳叆URL鎴栧煙鍚嶏紝濡?https://example.com" clearable />
          <el-button type="primary" @click="doCheck" :loading="checkLoading" style="margin-top:8px">妫€娴?/el-button>
          <el-result v-if="checkResult" :status="checkResult.accessible ? 'success' : 'error'" :title="checkResult.accessible ? '鍙闂? : '鏃犳硶璁块棶'">
            <template #extra>
              <p>鐘舵€佺爜: {{ checkResult.status_code }}</p>
              <p>寤惰繜: {{ checkResult.latency_ms }}ms</p>
              <p v-if="checkResult.error">閿欒: {{ checkResult.error }}</p>
            </template>
          </el-result>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>DNS 鏌ヨ</template>
          <el-input v-model="dnsDomain" placeholder="杈撳叆鍩熷悕" clearable />
          <el-button type="primary" @click="doDns" :loading="dnsLoading" style="margin-top:8px">鏌ヨ</el-button>
          <pre v-if="dnsResult" class="result-box">{{ dnsResult.records }}</pre>
        </el-card>
      </el-col>
    </el-row>
    <el-card shadow="never" style="margin-top:16px">
      <template #header>SSL 璇佷功妫€娴?/template>
      <el-input v-model="sslDomain" placeholder="杈撳叆鍩熷悕" clearable style="max-width:400px" />
      <el-button type="primary" @click="doSsl" :loading="sslLoading" style="margin-left:8px">妫€娴?/el-button>
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
  if (!url.value) { ElMessage.warning('请输入网址'); return }
  checking.value = true
  try {
    const { data } = await agentApi.post('/site/check', { url: url.value })
    results.value.unshift({ url: url.value, status: data.status_code, accessible: data.accessible, latency: data.latency_ms + 'ms', time: new Date().toTimeString().slice(0,5) })
    ElMessage.success(data.accessible ? '网站可访问' : '网站异常')
  } catch {
    ElMessage.error('检测失败')
  } finally { checking.value = false }
}

async function checkSSL(domain) {
  try {
    const { data } = await agentApi.post('/site/ssl', { domain: domain || url.value })
    ElMessage.success('SSL检测完成')
  } catch { ElMessage.error('SSL检测失败') }
}

onMounted(function() {})
</script>

<style scoped>
.site-check { padding: 24px; }
h2 { margin-bottom: 16px; font-size: 18px; }
.result-box { background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 6px; font-size: 12px; margin-top: 8px; max-height: 200px; overflow: auto; }
</style>
