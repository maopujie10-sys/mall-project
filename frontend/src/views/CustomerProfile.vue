<template>
  <div class="page-shell">
    <div class="page-header"><h2>👥 客户画像+情感分析</h2><p>情感识别+兴趣标签+优先处理</p></div>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card><template #header>🔬 情感分析</template>
          <el-input v-model="analyzeText" placeholder="输入客户消息" type="textarea" :rows="3"/>
          <el-button type="primary" style="margin-top:8px" @click="analyze">分析</el-button>
          <div v-if="sentiment" class="sent-result">
            <div class="sent-score" :class="sentiment.sentiment">
              {{ sentiment.sentiment === "positive" ? "😊 正面" : sentiment.sentiment === "negative" ? "😞 负面" : "😐 中性" }} ({{ sentiment.score }})
            </div>
            <div v-if="sentiment.needs_attention" class="sent-urgent">⚠️ 需关注 - 紧急度: {{ sentiment.urgency }}</div>
            <div class="sent-words">正面词: {{ sentiment.positive_words?.join(", ") || "无" }}</div>
            <div class="sent-words">负面词: {{ sentiment.negative_words?.join(", ") || "无" }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card><template #header>📋 客户画像</template>
          <el-input v-model="profileUserId" placeholder="用户ID"/>
          <el-button type="primary" style="margin-top:8px" @click="buildProfile">构建画像</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref } from "vue"; import { ElMessage } from "element-plus"; import { agentApi } from "@/api"
const analyzeText = ref(""); const sentiment = ref(null); const profileUserId = ref("")
async function analyze() {
  if (!analyzeText.value) return
  try { const r = await agentApi.post("/agent/sentiment/analyze", { text: analyzeText.value }); if (r?.data?.ok) sentiment.value = r.data } catch (e) { ElMessage.error(e.message) }
}
async function buildProfile() {
  if (!profileUserId.value) return
  try { const r = await agentApi.post("/agent/sentiment/profile", { user_id: profileUserId.value, messages: [analyzeText.value] }); if (r?.data) ElMessage.success("画像已构建") } catch (e) { ElMessage.error(e.message) }
}
</script>
<style scoped>
.page-shell { max-width: 900px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 20px; color: #e0e0ff; margin: 0; }
.page-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.sent-result { margin-top: 12px; padding: 12px; background: rgba(102,126,234,0.08); border-radius: 10px; }
.sent-score { font-size: 18px; font-weight: 600; }
.sent-score.positive { color: #4ade80; }
.sent-score.negative { color: #f87171; }
.sent-urgent { color: #fbbf24; font-size: 13px; margin-top: 4px; }
.sent-words { font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 4px; }
@media (max-width: 768px) { .page-shell { padding: 10px; } }
</style>
