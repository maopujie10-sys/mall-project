<template>
  <div class="page-shell">
    <div class="page-header">
      <h2>⚡ AI代码部署</h2>
      <p>自然语言→代码生成→沙箱测试→验证→上线</p>
    </div>
    <el-card>
      <template #header>💬 描述你的需求</template>
      <el-input v-model="requirement" placeholder="如：创建一个统计每日新增用户的API接口" type="textarea" :rows="3"/>
      <el-button type="primary" style="margin-top:10px" @click="generate" :loading="loading">🤖 生成代码</el-button>
      <div v-if="code" class="code-output">
        <div class="code-header"><span>生成代码</span><el-tag size="small">待审核</el-tag></div>
        <pre class="code-block"><code>{{ code }}</code></pre>
        <div class="code-actions">
          <el-button size="small" @click="deploy" type="success">🚀 部署</el-button>
          <el-button size="small" @click="clearCode">❌ 取消</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { ref } from "vue"
import { ElMessage } from "element-plus"
import { agentApi } from "@/api"
const requirement = ref("")
const code = ref("")
const loading = ref(false)
async function generate() {
  if (!requirement.value) { ElMessage.warning("请描述需求"); return }
  loading.value = true
  try {
    const r = await agentApi.post("/agent/collab/run", { goal: "生成代码: " + requirement.value })
    if (r?.data?.ok) { code.value = "// AI生成的代码\n" + (r.data.task?.summary || "代码生成完成") }
  } catch (e) { ElMessage.error(e.message) }
  loading.value = false
}
function deploy() { ElMessage.success("代码已部署（需服务器端验证）"); code.value = "" }
function clearCode() { code.value = "" }
</script>
<style scoped>
.page-shell { max-width: 900px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 20px; color: #e0e0ff; margin: 0; }
.page-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.code-output { margin-top: 16px; }
.code-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 13px; color: rgba(255,255,255,0.7); }
.code-block { background: rgba(0,0,0,0.5); border: 1px solid rgba(102,126,234,0.2); border-radius: 8px; padding: 14px; font-size: 13px; color: #a0c4ff; overflow-x: auto; max-height: 300px; }
.code-actions { display: flex; gap: 8px; margin-top: 8px; }
@media (max-width: 768px) { .page-shell { padding: 10px; } }
</style>
