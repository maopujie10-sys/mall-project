<template>
  <div>
    <el-tabs type="card">
      <el-tab-pane label="客服消息 (AI Agent)">
        <el-row :gutter="12" style="margin-bottom:12px">
          <el-col :span="8"><div class="metric-card"><div class="metric-label">总消息</div><div class="metric-value">{{ csStats.totalMessages }}</div></div></el-col>
          <el-col :span="8"><div class="metric-card" style="background:#e6f7ff"><div class="metric-label">活跃会话</div><div class="metric-value">{{ csStats.activeConversations }}</div></div></el-col>
          <el-col :span="8"><div class="metric-card" style="background:#f6ffed"><div class="metric-label">满意度</div><div class="metric-value">{{ csStats.satisfaction }}%</div></div></el-col>
        </el-row>
        <el-button size="small" type="primary" @click="loadCsMessages" :loading="csmLoading">刷新消息</el-button>
        <el-table :data="csMessages" stripe size="small" v-loading="csmLoading" style="margin-top:12px">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="content" label="内容" show-overflow-tooltip />
          <el-table-column prop="replied" label="状态" width="80">
            <template #default="{row}"><el-tag :type="row.replied?'success':'warning'" size="small">{{ row.replied?'已回复':'待回复' }}</el-tag></template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="商城会话 (Chat)">
        <el-table :data="conversations" stripe size="small" v-loading="cvLoading">
          <el-table-column prop="conversation_id" label="会话ID" width="200" />
          <el-table-column prop="from_user" label="发送方" width="100" />
          <el-table-column prop="to_user" label="接收方" width="100" />
          <el-table-column prop="last_message" label="最后消息" show-overflow-tooltip />
          <el-table-column label="操作" width="100">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="viewMessages(row.conversation_id)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="投诉管理">
        <el-table :data="complaints" stripe size="small" v-loading="cpLoading">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="reason" label="原因" show-overflow-tooltip />
          <el-table-column label="操作" width="100">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="handleComplaint(row.uuid,{status:'resolved'})">处理</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getCustomerMessages, getCustomerStats, getChatConversations, getComplaintList, handleComplaint as handleC } from '@/api/mall'
import { ElMessage } from 'element-plus'

const csMessages = ref([]); const csmLoading = ref(false)
const csStats = ref({ totalMessages: 0, activeConversations: 0, satisfaction: 95 })
const conversations = ref([]); const cvLoading = ref(false)
const complaints = ref([]); const cpLoading = ref(false)

async function loadCsMessages() {
  csmLoading.value = true
  try {
    const [msgs, stats] = await Promise.all([getCustomerMessages(), getCustomerStats()])
    csMessages.value = msgs.messages || []
    csStats.value = { totalMessages: msgs.total || 0, activeConversations: stats.activeConversations || 0, satisfaction: 95 }
  } catch { }
  csmLoading.value = false
}
async function loadChats() {
  cvLoading.value = true; cpLoading.value = true
  try { const r = await getChatConversations(); conversations.value = r.list || r.records || [] } catch { }
  try { const r = await getComplaintList(); complaints.value = r.list || r.records || [] } catch { }
  cvLoading.value = false; cpLoading.value = false
}
function viewMessages(conversationId) { ElMessage.info(`查看会话: ${conversationId}`) }
async function handleComplaint(uuid) { try { await handleC(uuid, { status: 'resolved' }); ElMessage.success('处理成功'); loadChats() } catch { ElMessage.error('失败') } }
onMounted(() => { loadCsMessages(); loadChats() })
</script>
<style scoped>
.metric-card { padding: 12px; border-radius: 8px; text-align: center; background: #f5f7fa; }
.metric-label { font-size: 12px; color: #909399; }
.metric-value { font-size: 24px; font-weight: 700; color: #303133; }
</style>