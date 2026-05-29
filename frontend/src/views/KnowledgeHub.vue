<template>
  <div class="page-shell">
    <div class="page-header"><h2>📚 知识中心</h2><p>RAG检索增强 — 文档摄入+语义搜索+智能问答</p></div>
    <el-row :gutter="16">
      <el-col :span="14">
        <el-card><template #header>🔍 智能问答</template>
          <el-input v-model="question" placeholder="输入问题，如：退款政策是什么？" type="textarea" :rows="2"/>
          <el-button type="primary" style="margin-top:10px" @click="ask" :loading="loading">提问</el-button>
          <div v-if="answer" class="rag-answer">
            <div class="answer-text">{{ answer.answer }}</div>
            <div class="answer-sources">参考来源: {{ answer.sources?.join(", ") || "无" }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card><template #header>📥 摄入文档</template>
          <el-input v-model="ingestText" placeholder="粘贴文档内容" type="textarea" :rows="4"/>
          <el-input v-model="ingestSource" placeholder="来源(可选)" style="margin-top:8px"/>
          <el-button style="margin-top:8px" @click="ingest">摄入</el-button>
          <div class="rag-stats"><span>📄 {{ stats.total_docs }} 文档</span><span>🔤 {{ stats.total_keywords }} 关键词</span></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { agentApi } from "@/api"
const question = ref("")
const answer = ref(null)
const loading = ref(false)
const ingestText = ref("")
const ingestSource = ref("")
const stats = ref({ total_docs: 0, total_keywords: 0 })
async function ask() {
  if (!question.value) { ElMessage.warning("请输入问题"); return }
  loading.value = true
  try { const r = await agentApi.post("/agent/rag/ask", { question: question.value }); if (r?.data?.ok) answer.value = r.data } catch (e) { ElMessage.error(e.message) }
  loading.value = false
}
async function ingest() {
  if (!ingestText.value) return
  try { const r = await agentApi.post("/agent/rag/ingest", { text: ingestText.value, source: ingestSource.value }); if (r?.data?.ok) { ElMessage.success("文档已摄入"); ingestText.value = ""; fetchStats() } } catch (e) { ElMessage.error(e.message) }
}
async function fetchStats() { try { const r = await agentApi.get("/agent/rag/stats"); if (r?.data) stats.value = r.data } catch {} }
onMounted(fetchStats)
</script>
<style scoped>
.page-shell { max-width: 900px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 20px; color: #e0e0ff; margin: 0; }
.page-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.rag-answer { margin-top: 12px; padding: 14px; background: rgba(102,126,234,0.08); border-radius: 10px; }
.answer-text { font-size: 14px; color: #e0e0e0; line-height: 1.6; }
.answer-sources { font-size: 11px; color: rgba(255,255,255,0.3); margin-top: 8px; }
.rag-stats { display: flex; gap: 16px; margin-top: 12px; font-size: 13px; color: rgba(255,255,255,0.6); }
@media (max-width: 768px) { .page-shell { padding: 10px; } }
</style>
