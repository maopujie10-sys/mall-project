<template>
  <div class="auto-reply"><div class="page-header">-<p>  AI    </p>
    <div class="header-stats"><el-statistic title='' :value="stats.total_replies" /><el-statistic title='' :value="stats.rule_matched" /><el-statistic title="AI" :value="stats.ai_replied" /><el-statistic title='' :value="stats.auto_rate" suffix="%" /></div>
  </div>
    <el-tabs v-model="tab">
      <el-tab-pane label=" " name="chat">
        <div class="chat-box" ref="chatBox"><div v-for="(m,i) in chat" :key="i" class="chat-msg" :class="m.role"><div class="chat-bubble">{{ m.text }}</div></div></div>
        <div class="chat-input"><el-input v-model="chatText" placeholder="..." @keyup.enter="doReply" style="flex:1"/><el-button type="primary" @click="doReply">OK</el-button></div>
      </el-tab-pane>
      <el-tab-pane label=" " name="rules">
        <el-button @click="ruleDialog=true" size="small" type="primary" style="margin-bottom:8px">+ </el-button>
        <el-table :data="rules" stripe size="small">
          <el-table-column prop="keyword" label='Status' width="130" />
          <el-table-column prop="reply" label='Status' min-width="200" show-overflow-tooltip />
          <el-table-column prop="category" label='Status' width="80" />
          <el-table-column prop="priority" label='Status' width="70" />
          <el-table-column label='Status' width="80"><template #default="{row}"><el-button text type="danger" size="small" @click="delRule(row.id)">OK</el-button></template></el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
    <el-dialog v-model="ruleDialog" title='' width="450">
      <el-form label-width="80"><el-form-item label=''><el-input v-model="newRule.keyword" placeholder='Enter...' /></el-form-item>
        <el-form-item label=''><el-input v-model="newRule.reply" type="textarea" :rows="3" placeholder="AI" /></el-form-item>
        <el-form-item label=''><el-input-number v-model="newRule.priority" :min="0" :max="100" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="ruleDialog=false">OK</el-button><el-button type="primary" @click="saveRule">OK</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted, nextTick } from "vue"; import { autoReply, getReplyRules, createReplyRule, deleteReplyRule, getAutoReplyStats } from "@/api/autoreply"
const tab=ref("chat"); const chat=ref([{role:"ai",text:"Friday AI"}]); const chatText=ref('')
const rules=ref([]); const stats=ref({}); const ruleDialog=ref(false); const newRule=ref({keyword:'',reply:'',priority:0})
const chatBox=ref(null)
async function doReply(){if(!chatText.value)return;const msg=chatText.value;chat.value.push({role:"user",text:msg});chatText.value='';try{const r=await autoReply(msg);if(r.ok){chat.value.push({role:"ai",text:r.reply+(r.transfer?"\n\n ":'')});if(r.transfer)chat.value.push({role:"ai",text:" "})}}catch(e){chat.value.push({role:"ai",text:""})};await nextTick();chatBox.value.scrollTop=chatBox.value.scrollHeight}
onMounted(async()=>{try{const r=await getReplyRules();if(r.ok)rules.value=r.rules}catch{};try{const r=await getAutoReplyStats();if(r.ok)stats.value=r.stats||{}}catch{}})
async function saveRule(){try{const r=await createReplyRule(newRule.value);if(r.ok){rules.value=r.rules;ruleDialog.value=false;ElMessage.success('OK')}}catch(e){ElMessage.error(e.message)}}
async function delRule(id){try{const r=await deleteReplyRule(id);if(r.ok){rules.value=rules.value.filter(x=>x.id!=id);ElMessage.success('OK')}}catch(e){ElMessage.error(e.message)}}
</script>
<style scoped>
.auto-reply{padding:20px}.page-header{margin-bottom:20px}.page-header h2{margin:0 0 4px}.page-header p{margin:0 0 12px;color:#999;font-size:13px}.header-stats{display:flex;gap:24px}
.chat-box{height:350px;overflow-y:auto;padding:16px;background: rgba(245,245,245,0.15);border-radius:8px;margin-bottom:12px}.chat-msg{margin-bottom:12px;display:flex}.chat-msg.user{justify-content:flex-end}.chat-bubble{max-width:70%;padding:10px 14px;border-radius:12px;font-size:13px;line-height:1.5;background:#fff;border:1px solid #e8e8e8}.chat-msg.user .chat-bubble{background:#e6f7ff;border-color:#91d5ff}.chat-input{display:flex;gap:8px}
</style>
