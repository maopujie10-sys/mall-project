<template>
  <div class="vc-shell">
    <div class="vc-header">
      <h2>Video Call</h2>
      <span class="room-badge" v-if="roomId">Room: {{ roomId }}</span>
    </div>

    <div class="vc-video-area">
      <!-- Local video -->
      <video ref="localVideo" autoplay muted playsinline class="vc-local"></video>
      <!-- Remote video -->
      <video ref="remoteVideo" autoplay playsinline class="vc-remote"></video>

      <div v-if="!callActive" class="vc-placeholder">
        <span>Enter a room ID to start</span>
      </div>
    </div>

    <!-- AI Chat sidebar during call -->
    <div class="vc-chat" v-if="callActive">
      <div class="vc-messages" ref="chatMsgs">
        <div v-for="(m, i) in chatMessages" :key="i" :class="['vc-msg', m.role]">{{ m.text }}</div>
      </div>
      <div class="vc-chat-input">
        <input v-model="chatInput" @keyup.enter="sendChatMsg" placeholder="Chat with AI during call..." />
        <button @click="sendChatMsg">Send</button>
      </div>
    </div>

    <!-- Controls -->
    <div class="vc-controls">
      <input v-model="roomId" placeholder="Room ID" class="vc-room-input" v-if="!callActive" />
      <button v-if="!callActive" @click="joinRoom" class="vc-btn join">Join Room</button>
      <button v-if="callActive" @click="toggleMute" class="vc-btn" :class="{ muted: isMuted }">Mic</button>
      <button v-if="callActive" @click="toggleVideo" class="vc-btn" :class="{ muted: !videoOn }">Video</button>
      <button v-if="callActive" @click="hangUp" class="vc-btn hangup">Hang Up</button>
    </div>

    <div class="vc-log" v-if="log.length">
      <div v-for="(l, i) in log" :key="i">{{ l }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'

const roomId = ref('')
const callActive = ref(false)
const isMuted = ref(false)
const videoOn = ref(true)
const chatInput = ref('')
const chatMessages = ref([])
const log = ref([])
const localVideo = ref(null)
const remoteVideo = ref(null)

let pc = null
let ws = null
let localStream = null

function addLog(msg) {
  log.value.push(`[${new Date().toLocaleTimeString()}] ${msg}`)
  if (log.value.length > 15) log.value.shift()
}

async function joinRoom() {
  if (!roomId.value.trim()) return
  const rid = roomId.value.trim()

  // Get user media
  try {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    if (localVideo.value) {
      localVideo.value.srcObject = localStream
    }
  } catch (e) {
    addLog('Camera/Mic access denied: ' + e.message)
    return
  }

  // Connect WebRTC signaling
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${proto}//${location.host}/agent/video/call/${rid}`
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    addLog('Connected to room: ' + rid)
    callActive.value = true
    createPeerConnection()
  }
  ws.onclose = () => { addLog('Disconnected'); hangUp() }
  ws.onerror = () => addLog('Signaling error')

  ws.onmessage = async (e) => {
    try {
      const data = JSON.parse(e.data)
      if (data.type === 'offer') {
        await pc.setRemoteDescription(new RTCSessionDescription(data))
        const answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        ws.send(JSON.stringify({ type: 'answer', sdp: answer.sdp }))
      } else if (data.type === 'answer') {
        await pc.setRemoteDescription(new RTCSessionDescription(data))
      } else if (data.type === 'ice-candidate') {
        if (data.candidate) {
          await pc.addIceCandidate(new RTCIceCandidate(data))
        }
      } else if (data.type === 'ai_response') {
        chatMessages.value.push({ role: 'assistant', text: data.text })
      }
    } catch (err) {
      addLog('Signal error: ' + err.message)
    }
  }
}

function createPeerConnection() {
  pc = new RTCPeerConnection({
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
  })

  pc.onicecandidate = (e) => {
    if (e.candidate && ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ice-candidate', candidate: e.candidate }))
    }
  }

  pc.ontrack = (e) => {
    if (remoteVideo.value) {
      remoteVideo.value.srcObject = e.streams[0]
    }
  }

  // Add local tracks
  if (localStream) {
    localStream.getTracks().forEach(track => pc.addTrack(track, localStream))
  }

  // Create and send offer
  pc.createOffer().then(offer => {
    pc.setLocalDescription(offer)
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'offer', sdp: offer.sdp }))
    }
  }).catch(e => addLog('Offer error: ' + e.message))
}

function sendChatMsg() {
  const text = chatInput.value.trim()
  if (!text || !ws || ws.readyState !== WebSocket.OPEN) return
  chatMessages.value.push({ role: 'user', text })
  chatInput.value = ''
  ws.send(JSON.stringify({ type: 'chat', text }))
}

function toggleMute() {
  if (localStream) {
    const audioTrack = localStream.getAudioTracks()[0]
    if (audioTrack) {
      audioTrack.enabled = !audioTrack.enabled
      isMuted.value = !audioTrack.enabled
    }
  }
}

function toggleVideo() {
  if (localStream) {
    const videoTrack = localStream.getVideoTracks()[0]
    if (videoTrack) {
      videoTrack.enabled = !videoTrack.enabled
      videoOn.value = videoTrack.enabled
    }
  }
}

function hangUp() {
  if (ws) {
    try { ws.send(JSON.stringify({ type: 'hangup' })) } catch {}
    ws.close()
    ws = null
  }
  if (pc) {
    pc.close()
    pc = null
  }
  if (localStream) {
    localStream.getTracks().forEach(t => t.stop())
    localStream = null
  }
  callActive.value = false
  chatMessages.value = []
}

onUnmounted(() => hangUp())
</script>

<style scoped>
.vc-shell {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 80px);
  padding: 16px;
  max-width: 800px;
  margin: 0 auto;
}
.vc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.vc-header h2 { font-size: 18px; color: #e0e0ff; margin: 0; }
.room-badge { font-size: 11px; padding: 4px 10px; border-radius: 12px; background: rgba(102,126,234,0.15); color: #a0b4ff; }

.vc-video-area {
  position: relative;
  flex: 1;
  min-height: 200px;
  background: rgba(0,0,0,0.3);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 8px;
}
.vc-local {
  position: absolute;
  bottom: 12px; right: 12px;
  width: 120px; height: 90px;
  border-radius: 8px;
  border: 2px solid rgba(102,126,234,0.5);
  object-fit: cover;
  z-index: 2;
}
.vc-remote {
  position: absolute;
  inset: 0;
  width: 100%; height: 100%;
  object-fit: cover;
}
.vc-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.3);
  font-size: 16px;
}

/* Chat sidebar */
.vc-chat {
  max-height: 150px;
  display: flex;
  flex-direction: column;
  margin-bottom: 8px;
}
.vc-messages {
  flex: 1;
  overflow-y: auto;
  font-size: 12px;
  max-height: 100px;
}
.vc-msg { padding: 2px 0; }
.vc-msg.user { color: #52c41a; }
.vc-msg.assistant { color: #a0b4ff; }
.vc-chat-input { display: flex; gap: 4px; margin-top: 4px; }
.vc-chat-input input {
  flex: 1; padding: 6px 10px; border-radius: 12px;
  border: 1px solid rgba(102,126,234,0.3); background: rgba(255,255,255,0.05);
  color: #fff; font-size: 12px; outline: none;
}
.vc-chat-input button {
  padding: 6px 12px; border-radius: 12px; border: none;
  background: #667eea; color: #fff; font-size: 12px; cursor: pointer;
}

.vc-controls {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}
.vc-room-input {
  padding: 8px 14px; border-radius: 20px;
  border: 1px solid rgba(102,126,234,0.3); background: rgba(255,255,255,0.05);
  color: #fff; font-size: 14px; outline: none; width: 160px;
}
.vc-btn {
  padding: 8px 20px; border-radius: 20px; border: none;
  font-size: 13px; cursor: pointer;
}
.vc-btn.join { background: #667eea; color: #fff; }
.vc-btn.hangup { background: #ff4d4f; color: #fff; }
.vc-btn.muted { background: rgba(255,255,255,0.1); color: #666; border: 1px solid rgba(255,255,255,0.1); }
.vc-log { font-size: 10px; color: rgba(255,255,255,0.3); max-height: 40px; overflow-y: auto; }
</style>
