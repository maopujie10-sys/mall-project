<template>
  <div class="page-shell">
    <div class="page-header">-<p>  AISQL  </p></div>
    <el-card><template #header> </template>
      <el-input v-model="question" placeholder='Enter...' type="textarea" :rows="2"/>
      
      <div v-if="result" class="sql-result">
        <div class="sql-explain">{{ result.explanation }}</div>
        <pre class="sql-code">{{ result.sql }}</pre>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { ref } from "vue"; import { ElMessage } from "element-plus"; import { agentApi } from "@/api"
const question = ref(''); const result = ref(null); const loading = ref(false)
async function query() {
  if (!question.value) return; loading.value = true
  try { const r = await agentApi.post("/agent/text2sql/query", { question: question.value }); if (r?.data?.ok) result.value = r.data; else { ElMessage.warning(r?.data?.error || ''); result.value = r.data } } catch (e) { ElMessage.error(e.message) }
  loading.value = false
}
</script>
<style scoped>
.page-shell { max-width: 900px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 20px; color: #e0e0ff; margin: 0; }
.page-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.sql-result { margin-top: 14px; }
.sql-explain { font-size: 13px; color: rgba(255,255,255,0.6); margin-bottom: 8px; }
.sql-code { background: rgba(0,0,0,0.5); border: 1px solid rgba(102,126,234,0.2); border-radius: 8px; padding: 14px; font-size: 13px; color: #a0c4ff; overflow-x: auto; }
@media (max-width: 768px) { .page-shell { padding: 10px; } }
</style>
