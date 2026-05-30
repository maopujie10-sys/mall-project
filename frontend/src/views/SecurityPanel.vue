<template>
  <div class="page-container">
    <div class="page-header">
      <h2>瀹夊叏璁剧疆</h2>
      <p>Google 楠岃瘉鍣路 涓ゆ楠岃瘉</p>
    </div>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never">
          <div class="card-title">Google 楠岃瘉鍣?(TOTP)</div>
          <div style="padding:20px 0;text-align:center;">
            <template v-if="!setupDone">
              <el-button type="primary" size="large" @click="doSetup" :loading="settingUp">
                寮€鍚袱姝ラ獙璇?              </el-button>
              <p style="margin-top:12px;color:#999;font-size:13px;">浣跨敤 Google Authenticator 鎴?Authy 淇濇姢鎮ㄧ殑璐︽埛</p>
            </template>
            <template v-else>
              <div v-if="qrCode" style="margin-bottom:20px;">
                <img :src="qrCode" style="width:200px;height:200px;" />
                <p style="margin:12px 0;font-size:13px;color:#666;">鎵嬪姩杈撳叆瀵嗛挜: <code>{{ secret }}</code></p>
              </div>
              <el-form inline style="justify-content:center;">
                <el-form-item><el-input v-model="code" placeholder="6浣嶉獙璇佺爜" maxlength="6" style="width:140px;" /></el-form-item>
                <el-form-item><el-button type="primary" @click="doVerify" :loading="verifying">楠岃瘉</el-button></el-form-item>
              </el-form>
              <el-button type="danger" text @click="doReset">閲嶇疆楠岃瘉鍣</el-button>
            </template>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <div class="card-title">鐘舵€</div>
          <div style="padding:20px 0;">
            <el-result :icon="verified?'success':'warning'" :title="verified?'宸插惎鐢':'未启用'" :sub-title="verified?'两步验证已开启，登录时需要输入验证码':'账户未开启两步验证保护'" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { agentApi } from '@/api/index'
const verified = ref(false)
const setupDone = ref(false)
const settingUp = ref(false)
const verifying = ref(false)
const qrCode = ref('')
const secret = ref('')
const code = ref('')

async function checkStatus() {
  try {
    const { data } = await agentApi.get('/2fa/status')
    verified.value = data.enabled
    if (data.enabled) setupDone.value = true
  } catch (_) {}
}

async function doSetup() {
  settingUp.value = true
  try {
    const { data } = await agentApi.post('/2fa/setup')
    qrCode.value = data.qr_code
    secret.value = data.secret
    setupDone.value = true
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '设置失败')
  } finally { settingUp.value = false }
}

async function doVerify() {
  if (!code.value || code.value.length !== 6) { ElMessage.warning('请输入6位验证码'); return }
  verifying.value = true
  try {
    await agentApi.post(`/2fa/verify?code=${code.value}`)
    verified.value = true
    ElMessage.success('验证成功')
    code.value = ''
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '验证码无效')
  } finally { verifying.value = false }
}

async function doReset() {
  try {
    await agentApi.delete('/2fa/reset')
    verified.value = false; setupDone.value = false; qrCode.value = ''; secret.value = ''
    ElMessage.success('已重置')
  } catch (e) { ElMessage.error('重置失败') }
}

onMounted(checkStatus)
</script>

<style scoped>
.card-title { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 0; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
