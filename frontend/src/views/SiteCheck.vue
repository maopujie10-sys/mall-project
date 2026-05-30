<template>
  <div class="site-check">
    <h2>{{ \('site.title') }}</h2>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header></template>
          <el-input v-model="checkUrl" placeholder="URL https://example.com" clearable />
          <el-button type="primary" @click="doCheck" :loading="checkLoading" style="margin-top:8px">OK</el-button>
          <el-result v-if="checkResult" :status="checkResult.accessible ? 'success' : 'error'' :title="checkResult.accessible ? '' : ''">
            <template #extra>
              <p>: {{ checkResult.status_code }}</p>
              <p>: {{ checkResult.latency_ms }}ms</p>
              <p v-if="checkResult.error">: {{ checkResult.error }}</p>
            </template>
          </el-result>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>DNS </template>
          <el-input v-model="dnsDomain" placeholder='' clearable />
          <el-button type="primary" @click="doDns" :loading="dnsLoading" style="margin-top:8px">OK</el-button>
          <pre v-if="dnsResult" class="result-box">{{ dnsResult.records }}</pre>
        </el-card>
      </el-col>
    </el-row>
    <el-card shadow="never" style="margin-top:16px">
      <template #header>SSL </template>
      <el-input v-model="sslDomain" placeholder='' clearable style="max-width:400px" />
      <el-button type="primary" @click="doSsl" :loading="sslLoading" style="margin-left:8px">OK</el-button>
      <el-descriptions v-if="sslResult && sslResult.cert_info" :column="1" border style="margin-top:12px">
        <el-descriptions-item v-for="(v, k) in sslResult.cert_info" :key="k" :label="k">{{ v }}</el-descriptions-item>
      </el-descriptions>
      <p v-else-if="sslResult && sslResult.error" style="color:red">{{ sslResult.error }}</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { checkSite, checkDns, checkSsl } from '@/api/site'
import { ElMessage } from 'element-plus'

const checkUrl = ref('')
const checkResult = ref(null)
const checkLoading = ref(false)
const dnsDomain = ref('')
const dnsResult = ref(null)
const dnsLoading = ref(false)
const sslDomain = ref('')
const sslResult = ref(null)
const sslLoading = ref(false)

async function doCheck() {
  if (!checkUrl.value) return
  checkLoading.value = true
  try { checkResult.value = await checkSite(checkUrl.value) } catch { ElMessage.error('Error') }
  checkLoading.value = false
}
async function doDns() {
  if (!dnsDomain.value) return
  dnsLoading.value = true
  try { dnsResult.value = await checkDns(dnsDomain.value) } catch { ElMessage.error('Error') }
  dnsLoading.value = false
}
async function doSsl() {
  if (!sslDomain.value) return
  sslLoading.value = true
  try { sslResult.value = await checkSsl(sslDomain.value) } catch { ElMessage.error('Error') }
  sslLoading.value = false
}
</script>

<style scoped>
.site-check { padding: 24px; }
h2 { margin-bottom: 16px; font-size: 18px; }
.result-box { background: rgba(30,30,30,0.85); color: #d4d4d4; padding: 12px; border-radius: 6px; font-size: 12px; margin-top: 8px; max-height: 200px; overflow: auto; }
</style>
