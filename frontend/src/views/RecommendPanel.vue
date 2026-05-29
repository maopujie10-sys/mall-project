<template>
  <div class="page-shell">
    <div class="page-header"><h2>🎯 AI推荐引擎</h2><p>协同过滤+内容推荐 — 个性化商品推荐</p></div>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card><template #header>👤 用户推荐</template>
          <el-input v-model="userId" placeholder="用户ID"/>
          <el-button type="primary" style="margin-top:8px" @click="recUser">推荐</el-button>
          <div v-if="userRecs.length" class="rec-list">
            <div v-for="item in userRecs" :key="item.item_id" class="rec-item">
              <span class="rec-id">{{ item.item_id }}</span><span class="rec-score">⭐ {{ item.score }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card><template #header>🔗 相似商品</template>
          <el-input v-model="itemId" placeholder="商品ID"/>
          <el-button type="primary" style="margin-top:8px" @click="recSimilar">推荐</el-button>
          <div v-if="simItems.length" class="rec-list">
            <div v-for="item in simItems" :key="item.item_id" class="rec-item">
              <span class="rec-id">{{ item.item_id }}</span><span class="rec-score">⭐ {{ item.score }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref } from "vue"; import { ElMessage } from "element-plus"; import { agentApi } from "@/api"
const userId = ref(""); const itemId = ref(""); const userRecs = ref([]); const simItems = ref([])
async function recUser() {
  if (!userId.value) return
  try { const r = await agentApi.get("/agent/recommend/for_user/" + userId.value); if (r?.data?.ok) userRecs.value = r.data.items } catch (e) { ElMessage.error(e.message) }
}
async function recSimilar() {
  if (!itemId.value) return
  try { const r = await agentApi.get("/agent/recommend/similar/" + itemId.value); if (r?.data?.ok) simItems.value = r.data.items } catch (e) { ElMessage.error(e.message) }
}
</script>
<style scoped>
.page-shell { max-width: 900px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 20px; color: #e0e0ff; margin: 0; }
.page-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.rec-list { margin-top: 10px; }
.rec-item { display: flex; justify-content: space-between; padding: 8px 10px; background: rgba(102,126,234,0.06); border-radius: 8px; margin-bottom: 6px; font-size: 13px; }
.rec-id { color: #a0c4ff; }
.rec-score { color: #fbbf24; }
@media (max-width: 768px) { .page-shell { padding: 10px; } }
</style>
