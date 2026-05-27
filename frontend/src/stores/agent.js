import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { sendChat, confirmTask, getAgentTasks, handover } from '@/api/agent'

export const useAgentStore = defineStore('agent', () => {
  const messages = ref([])
  const steps = ref([])
  const isRunning = ref(false)
  const currentTaskId = ref(null)

  const messageCount = computed(() => messages.value.length)

  function addUserMessage(text) {
    messages.value.push({
      role: 'user',
      text,
      time: new Date().toLocaleTimeString(),
    })
  }

  function addAIMessage(text, risk, needConfirm, stepsData) {
    messages.value.push({
      role: 'ai',
      text,
      risk,
      needConfirm,
      time: new Date().toLocaleTimeString(),
      steps: stepsData,
    })
  }

  function clearSteps() {
    steps.value = []
  }

  function addStep(step) {
    steps.value.push(step)
  }

  function updateStep(id, updates) {
    const idx = steps.value.findIndex((s) => s.id === id)
    if (idx !== -1) {
      Object.assign(steps.value[idx], updates)
    }
  }

  async function sendMessage(text) {
    if (!text || !text.trim() || isRunning.value) return

    isRunning.value = true
    clearSteps()
    addUserMessage(text)

    try {
      const response = await sendChat(text)

      // Process steps from backend response
      if (response.steps && Array.isArray(response.steps)) {
        for (const step of response.steps) {
          addStep({
            id: step.id || Date.now() + Math.random(),
            name: step.name || step.tool || '姝ラ',
            tool: step.tool || '',
            status: step.status || 'pending',
            evidence: step.evidence || '',
          })
        }
      }

      // Process response message
      const risk = response.risk || 'l1'
      const needConfirm = response.needConfirm || false
      const reply = response.reply || response.message || response.text || '浠诲姟澶勭悊瀹屾垚'
      const stepsOut = response.steps?.map((s, i) => ({
        step: i + 1,
        name: s.name || s.tool || '',
        ok: s.status === 'done' || s.status === 'success',
        detail: s.evidence || '',
      }))

      if (needConfirm) {
        currentTaskId.value = response.taskId || null
      }

      addAIMessage(reply, risk, needConfirm, stepsOut)
    } catch (error) {
      addAIMessage(
        `璇锋眰澶辫触: ${error.message || '缃戠粶閿欒锛岃妫€鏌ュ悗绔湇鍔℃槸鍚︽甯?}`,
        'l3',
        false,
        null
      )
    } finally {
      isRunning.value = false
    }
  }

  async function confirmMsgAction(msg, approved) {
    if (!msg || !msg.needConfirm) return
    try {
      if (currentTaskId.value) {
        await confirmTask(currentTaskId.value, approved)
      }
      if (approved) {
        messages.value.push({
          role: 'ai',
          text: '浠诲姟宸茬‘璁ゆ墽琛屻€傛鍦ㄨ繘琛屾搷浣?..',
          risk: 'l2',
          time: new Date().toLocaleTimeString(),
        })
      } else {
        messages.value.push({
          role: 'ai',
          text: '鎿嶄綔宸茶鎷掔粷锛屼换鍔″彇娑堛€?,
          risk: 'l3',
          time: new Date().toLocaleTimeString(),
        })
      }
      msg.needConfirm = false
      currentTaskId.value = null
    } catch (error) {
      messages.value.push({
        role: 'ai',
        text: `鎿嶄綔澶辫触: ${error.message}`,
        risk: 'l3',
        time: new Date().toLocaleTimeString(),
      })
    }
  }

  async function fetchTasks() {
    try {
      return await getAgentTasks()
    } catch {
      return []
    }
  }

  async function handoverToHuman(reason) {
    try {
      await handover(reason)
      return true
    } catch {
      return false
    }
  }

  return {
    messages,
    steps,
    isRunning,
    currentTaskId,
    messageCount,
    addUserMessage,
    addAIMessage,
    clearSteps,
    addStep,
    updateStep,
    sendMessage,
    confirmMsgAction,
    fetchTasks,
    handoverToHuman,
  }
})
