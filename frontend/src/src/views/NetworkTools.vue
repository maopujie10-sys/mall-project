<template>
  <div class="net-tools">
    <div class="page-header">-<p>Ping  DNS    HTTP? </p></div>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never" style="margin-bottom:16px">
          <template #header><span> Ping</span></template>
          <div style="display:flex;gap:8px">
            <el-input v-model="pingHost" placeholder="P" size="small" @keyup.enter="runPing" />
            <el-button @click="runPing" size="small" type="primary" :loading="pingLoading">Ping</el-button>
          </div>
          <pre v-if="pingResult" class="result-box">{{ pingResult.stdout || pingResult.error || "? }}</pre>
        </el-card>

        <el-card shadow="never" style="margin-bottom:16px">
          <template #header><span> DNS </span></template>
          <div style="display:flex;gap:8px">
            <el-input v-model="dnsDomain" placeholder='' size="small" @keyup.enter="runDns" />
            <el-button @click="runDns" size="small" type="primary" :loading="dnsLoading"></el-button>
          </div>
          <div v-if="dnsResult" class="result-box">
            <div v-if="dnsResult.ips">IP?code v-for="ip in dnsResult.ips" :key="ip" style="display:block">{{ ip }}</code></div>
            <div v-else style="color:#ff4d4f">{{ dnsResult.error }}</div>
          </div>
        </el-card>

        <el-card shadow="never">
          <template #header><span> HTTP ?/span></template>
          <div style="display:flex;gap:8px">
            <el-input v-model="httpUrl" placeholder="https://example.com" size="small" @keyup.enter="runHttp" />
            <el-button @click="runHttp" size="small" type="primary" :loading="httpLoading">?/el-button>
          </div>
          <div v-if="httpResult" class="result-box">
            <div>?el-tag :type="httpResult.status < 400 ? 'success' : 'danger''>{{ httpResult.status }}</el-tag></div>
            <div>{ httpResult.elapsed_ms }}ms</div>
            <div>{ httpResult.size }} bytes</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" style="margin-bottom:16px">
          <template #header>-</template>
          <div style="display:flex;gap:8px;margin-bottom:8px">
            <el-input v-model="scanHost" placeholder="P" size="small" style="width:200px" />
            <el-input v-model="scanPorts" placeholder="22,80,443,3306..." size="small" style="width:250px" />
            <el-button @click="runPortScan" size="small" type="primary" :loading="scanLoading"></el-button>
          </div>
          <div v-if="scanResult" class="result-box">
            <div style="margin-bottom:8px">{{ scanResult.open_count }}/{{ scanResult.results?.length || 0 }}</div>
            <div v-for="r in scanResult.results" :key="r.port" style="display:flex;align-items:center;gap:8px;padding:2px 0">
              <span :style="{color:r.open?'#52c41a':'#999'}">{{ r.open ? '' : '? }}</span>
              <span style="font-family:monospace"> {{ r.port }}</span>
              <el-tag v-if="r.open" size="small" type="success">?/el-tag>
              -
            </div>
          </div>
        </el-card>

        <el-card shadow="never">
          <template #header><span>?</span></template>
          <div style="display:flex;gap:8px">
            <el-input v-model="traceHost" placeholder="P" size="small" @keyup.enter="runTrace" />
            <el-button @click="runTrace" size="small" type="primary" :loading="traceLoading">OK</el-button>
          </div>
          <pre v-if="traceResult" class="result-box">{{ traceResult.stdout || traceResult.error || "? }}</pre>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { agentApi } from "@/api"

const pingHost = ref('')
const pingResult = ref(null)
const pingLoading = ref(false)
const dnsDomain = ref('')
const dnsResult = ref(null)
const dnsLoading = ref(false)
const httpUrl = ref('')
const httpResult = ref(null)
const httpLoading = ref(false)
const scanHost = ref('')
const scanPorts = ref("22,80,443,3306,6379,8080,9000")
const scanResult = ref(null)
const scanLoading = ref(false)
const traceHost = ref('')
const traceResult = ref(null)
const traceLoading = ref(false)

async function runPing() {
  if (!pingHost.value) return
  pingLoading.value = true
  try { pingResult.value = (await agentApi.post("/network/ping", null, { params: { host: pingHost.value, count: 3 } })) }
  catch (e) { pingResult.value = { error: e.message } }
  pingLoading.value = false
}

async function runDns() {
  if (!dnsDomain.value) return
  dnsLoading.value = true
  try { dnsResult.value = (await agentApi.post("/network/dns", null, { params: { domain: dnsDomain.value } })) }
  catch (e) { dnsResult.value = { error: e.message } }
  dnsLoading.value = false
}

async function runHttp() {
  if (!httpUrl.value) return
  httpLoading.value = true
  try { httpResult.value = (await agentApi.post("/network/http-check", null, { params: { url: httpUrl.value } })) }
  catch (e) { httpResult.value = { error: e.message } }
  httpLoading.value = false
}

async function runPortScan() {
  if (!scanHost.value) return
  scanLoading.value = true
  try { scanResult.value = (await agentApi.post("/network/port-scan", null, { params: { host: scanHost.value, ports: scanPorts.value } })) }
  catch (e) { scanResult.value = { error: e.message } }
  scanLoading.value = false
}

async function runTrace() {
  if (!traceHost.value) return
  traceLoading.value = true
  try { traceResult.value = (await agentApi.post("/network/traceroute", null, { params: { host: traceHost.value } })) }
  catch (e) { traceResult.value = { error: e.message } }
  traceLoading.value = false
}
</script>

<style scoped>
.net-tools { padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px; font-size: 18px; }
.page-header p { margin: 0; color: #999; font-size: 13px; }
.result-box {
  margin-top: 10px; padding: 10px; background: rgba(246,248,250,0.15); border-radius: 6px;
  font-size: 12px; font-family: monospace; max-height: 200px; overflow-y: auto;
  line-height: 1.5;
}
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
