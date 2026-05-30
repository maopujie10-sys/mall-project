<template>
  <div class="merchant-chat"><h2>客服消息</h2>
    <div class="chat-layout">
      <div class="chat-list">
        <div v-for="c in conversations" :key="c.id" class="chat-item" :class="{ active: activeConv === c.id }" @click="activeConv = c.id">
          <span class="chat-name">{{ c.name || c.username }}</span>
          <span class="chat-last">{{ c.lastMessage }}</span>
        </div>
        <div v-if="!conversations.length" class="empty-state"><p>暂无消息</p></div>
      </div>
      <div class="chat-main">
        <div v-if="activeConv" class="chat-messages">
          <div v-for="m in messages" :key="m.id" class="msg" :class="{ mine: m.from === 'me' }">
            <span class="msg-text">{{ m.text || m.content }}</span>
            <span class="msg-time">{{ m.time }}</span>
          </div>
        </div>
        <div v-else class="empty-state"><p>选择对话</p></div>
        <div v-if="activeConv" class="chat-input"><el-input v-model="newMsg" placeholder="输入消息..." @keyup.enter="sendMsg"><template #append><el-button @click="sendMsg">发送</el-button></template></el-input></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get, post, put, del } from '@/api/index'

const conversations = ref([]); const messages = ref([]); const activeConv = ref(null); const newMsg = ref('')

onMounted(async () => {
  try {
    const r = await getChatConversations()
    conversations.value = (r.data || r).list || (r.data || r).rows || []
    if (conversations.value.length) activeConv.value = conversations.value[0].id
  } catch {}
})

async function sendMsg() {
  if (!newMsg.value.trim() || !activeConv.value) return
  try { await sendChatMessage({ conversationId: activeConv.value, message: newMsg.value }); messages.value.push({ id: Date.now(), text: newMsg.value, from: 'me', time: new Date().toLocaleTimeString() }); newMsg.value = '' } catch {}
}
</script>

<style scoped>
.merchant-chat { padding: 0; }
h2 { margin-bottom: 20px; }
.chat-layout { display: grid; grid-template-columns: 240px 1fr; gap: 0; border: 1px solid var(--border-color); border-radius: var(--border-radius); overflow: hidden; height: 500px; }
.chat-list { border-right: 1px solid var(--border-color); overflow-y: auto; }
.chat-item { padding: 14px 16px; cursor: pointer; border-bottom: 1px solid var(--border-color); }
.chat-item.active { background: rgba(99,102,241,0.06); border-right: 2px solid var(--color-primary); }
.chat-name { display: block; font-size: 14px; font-weight: 500; }
.chat-last { font-size: 12px; color: var(--text-muted); display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.chat-main { display: flex; flex-direction: column; overflow: hidden; }
.chat-messages { flex: 1; padding: 16px; overflow-y: auto; }
.msg { margin-bottom: 12px; }
.msg.mine { text-align: right; }
.msg-text { display: inline-block; padding: 8px 14px; border-radius: 12px; background: var(--bg-tertiary); font-size: 13px; max-width: 70%; }
.msg.mine .msg-text { background: var(--color-primary); color: white; }
.msg-time { display: block; font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.chat-input { padding: 10px; border-top: 1px solid var(--border-color); }
.empty-state { flex: 1; display: flex; align-items: center; justify-content: center; color: var(--text-muted); }
@media (max-width: 768px) { .chat-layout { grid-template-columns: 1fr; } }
</style>
