<template>
  <div class="page-shell">
    <div class="page-header"><h2>AI</h2><p>AI ->  ->  -> </p></div>
    <el-card><template #header></template>
      <el-input v-model="requirement" placeholder="Excel" type="textarea" :rows="3"/>
      <el-button type="primary" style="margin-top:10px" @click="generate" :loading="loading">AI</el-button>
    </el-card>
    <el-card v-if="code" style="margin-top:16px"><template #header><el-tag size="small" style="margin-left:8px" :type="validation.pass?'success':'danger''>{{validation.pass?'':''}}</el-tag></template>
      <pre class="code-preview">{{ code }}</pre>
      <div style="margin-top:12px;display:flex;gap:8px">
        <el-button type="success" @click="deploy" :loading="deploying" :disabled="!validation.pass">OK</el-button>
        <el-button @click="testCode" :loading="testing">OK</el-button>
        <el-button @click="clearCode">OK</el-button>
      </div>
    </el-card>
    <el-card v-if="deployResult" style="margin-top:16px"><template #header></template>
      <el-alert :type="deployResult.ok?'success':'error'' :title="deployResult.ok?'':''" :description="deployResult.message" show-icon/>
    </el-card>
  </div>
</template>
<script setup>
import { ref } from "vue"; import { ElMessage } from "element-plus"; import { agentApi } from "@/api"
const requirement = ref(''); const code = ref(''); const loading = ref(false); const deploying = ref(false); const testing = ref(false)
const validation = ref({pass:false}); const deployResult = ref(null)

async function generate() {
  if(!requirement.value) { ElMessage.warning('Warning'); return }; loading.value = true
  try {
    const r = await agentApi.post("/agent/deploy/generate", { requirement: requirement.value })
    if(r?.data?.ok) { code.value = r.data.code; validation.value = {pass: r.data.valid !== false } }
    else ElMessage.warning(r?.data?.error || '')
  } catch(e) { ElMessage.error(e.message) }; loading.value = false
}
async function deploy() {
  if(!code.value) return; deploying.value = true
  try {
    const r = await agentApi.post("/agent/deploy/apply", { code: code.value, requirement: requirement.value })
    if(r?.data?.ok) { deployResult.value = {ok:true,message:r.data.message||''}; ElMessage.success('OK') }
    else { deployResult.value = {ok:false,message:r.data.error}; ElMessage.error(r.data.error) }
  } catch(e) { deployResult.value = {ok:false,message:e.message}; ElMessage.error(e.message) }; deploying.value = false
}
async function testCode() {
  if(!code.value) return; testing.value = true
  try {
    const r = await agentApi.post("/agent/deploy/test", { code: code.value })
    if(r?.data?.ok) ElMessage.success(": "+ (r.data.result||''))
    else ElMessage.warning(": "+(r.data.error||''))
  } catch(e) { ElMessage.error(e.message) }; testing.value = false
}
function clearCode() { code.value = ''; deployResult.value = null }
</script>
<style scoped>
.page-shell { max-width: 900px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 16px; } .page-header h2 { font-size: 20px; color: #e0e0ff; margin: 0; } .page-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.code-preview { background: rgba(0,0,0,0.5); border: 1px solid rgba(102,126,234,0.2); border-radius: 8px; padding: 14px; font-size: 13px; color: #a0c4ff; overflow-x: auto; max-height: 400px; white-space: pre-wrap; }
@media (max-width: 768px) { .page-shell { padding: 10px; } }
</style>