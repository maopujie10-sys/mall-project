<template>
  <div class="login-page fade-in">
    <div class="login-card card">
      <div class="login-banner">
        <div class="banner-inner">
          <div class="logo-icon">M</div>
          <h2>TikTokMall</h2>
          <p>Sign In</p>
        </div>
      </div>

      <div class="login-form-section">
        <h1>Sign In</h1>

        <div class="login-tabs">
          <button :class="['tab-btn', { active: loginType === 1 }]" @click="loginType = 1">Email</button>
          <button :class="['tab-btn', { active: loginType === 2 }]" @click="loginType = 2">Mobile</button>
        </div>

        <!-- Account Login -->
        <el-form v-if="loginType === 1" ref="accountFormRef" :model="accountForm" :rules="accountRules" label-position="top" @keyup.enter="handleAccountLogin">
          <el-form-item label="Email" prop="username">
            <el-input v-model="accountForm.username" placeholder="Please enter email" size="large" />
          </el-form-item>
          <el-form-item label="Password" prop="password">
            <el-input v-model="accountForm.password" :type="showPwd ? 'password' : 'text'" placeholder="Please enter password" size="large">
              <template #suffix>
                <button type="button" class="eye-btn" @click="showPwd = !showPwd">
                  <svg v-if="showPwd" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </template>
            </el-input>
          </el-form-item>
          <div class="form-row">
            <span class="text-muted">Don't have an account? <router-link to="/pc/register" class="link">Sign Up</router-link></span>
            <span class="link" @click="handleForgot">Forgot Password?</span>
          </div>
          <el-button class="submit-btn" type="primary" size="large" :loading="loading" @click="handleAccountLogin">Sign In</el-button>
        </el-form>

        <!-- Mobile Login -->
        <el-form v-else ref="mobileFormRef" :model="mobileForm" :rules="mobileRules" label-position="top" @keyup.enter="handleMobileLogin">
          <el-form-item label="Mobile" prop="username">
            <div class="phone-wrap">
              <el-popover placement="bottom" :width="240" trigger="click">
                <template #reference>
                  <div class="area-btn"><span>+{{ mobileForm.areaCode }}</span><i class="arrow-down"></i></div>
                </template>
                <div class="area-list">
                  <div v-for="c in areaCodes" :key="c.value" :class="['area-item', { active: mobileForm.areaCode === c.value }]" @click="mobileForm.areaCode = c.value">{{ c.label }} (+{{ c.value }})</div>
                </div>
              </el-popover>
              <el-input v-model="mobileForm.username" placeholder="Please enter phone number" size="large" class="phone-inp" maxlength="30" />
            </div>
          </el-form-item>
          <el-form-item label="Password" prop="password">
            <el-input v-model="mobileForm.password" :type="showMPwd ? 'password' : 'text'" placeholder="Please enter password" size="large">
              <template #suffix>
                <button type="button" class="eye-btn" @click="showMPwd = !showMPwd">
                  <svg v-if="showMPwd" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </template>
            </el-input>
          </el-form-item>
          <div class="form-row">
            <span class="text-muted">Don't have an account? <router-link to="/pc/register" class="link">Sign Up</router-link></span>
            <span class="link" @click="handleForgot">Forgot Password?</span>
          </div>
          <el-button class="submit-btn" type="primary" size="large" :loading="loading" @click="handleMobileLogin">Sign In</el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { post } from '@/api/index'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)
const loginType = ref(1)
const showPwd = ref(true)
const showMPwd = ref(true)

const accountFormRef = ref(null)
const mobileFormRef = ref(null)

const accountForm = reactive({ username: '', password: '' })
const mobileForm = reactive({ username: '', password: '', areaCode: '86' })

const areaCodes = [
  { value: '86', label: 'China' }, { value: '1', label: 'US/Canada' }, { value: '44', label: 'UK' },
  { value: '81', label: 'Japan' }, { value: '82', label: 'Korea' }, { value: '886', label: 'Taiwan' },
  { value: '852', label: 'Hong Kong' }, { value: '63', label: 'Philippines' }, { value: '60', label: 'Malaysia' },
  { value: '66', label: 'Thailand' }, { value: '91', label: 'India' }, { value: '62', label: 'Indonesia' },
  { value: '84', label: 'Vietnam' }, { value: '49', label: 'Germany' }, { value: '33', label: 'France' },
  { value: '7', label: 'Russia' }
]

const emailRule = { pattern: /^([A-Za-z0-9_\-.])+@([A-Za-z0-9_\-.])+\.([A-Za-z]{2,4})$/, message: 'Invalid email', trigger: 'blur' }
const phoneRule = { pattern: /^[\d]{1,20}$/, message: 'Invalid phone number', trigger: 'blur' }
const pwdRule = { pattern: /^[a-zA-Z0-9!@#$%^&*()_+{}[\]:;'"\\|,.<>?~`\-=/]{6,12}$/, message: '6-12 characters', trigger: 'blur' }

const accountRules = {
  username: [{ required: true, message: 'Please enter email', trigger: 'blur' }, emailRule],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }, pwdRule]
}
const mobileRules = {
  username: [{ required: true, message: 'Please enter phone number', trigger: 'blur' }, phoneRule],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }, pwdRule]
}

async function doLogin(username, password, areaCode) {
  try {
    loading.value = true
    const params = { username, password: encodeURIComponent(password), loginType: 'password', deviceType: 'web' }
    if (areaCode) { params.areaCode = areaCode; params.username = areaCode + ' ' + username }
    const res = await post('/api/user!newlogin.action', params)
    const token = res.data?.token || res.token
    if (token) {
      userStore.token = token
      localStorage.setItem('token', token)
      try { await userStore.fetchUserInfo() } catch {}
      ElMessage.success('Login successful')
      const redirect = route.query.redirect || '/pc'
      router.push(redirect)
    }
  } catch { ElMessage.error('Login failed') }
  finally { loading.value = false }
}

function handleAccountLogin() {
  accountFormRef.value?.validate(async (v) => { if (v) await doLogin(accountForm.username, accountForm.password) })
}
function handleMobileLogin() {
  mobileFormRef.value?.validate(async (v) => { if (v) await doLogin(mobileForm.username, mobileForm.password, mobileForm.areaCode) })
}
function handleForgot() {
  ElMessage.info('Please contact customer service for password reset')
}
</script>

<style scoped>
.login-page { display: flex; align-items: center; justify-content: center; min-height: calc(100vh - 200px); padding: 40px 20px; }
.login-card { display: flex; max-width: 960px; width: 100%; min-height: 500px; overflow: hidden; padding: 0; border-radius: var(--border-radius-lg); box-shadow: var(--shadow-xl); }
.login-banner { width: 380px; flex-shrink: 0; background: linear-gradient(135deg, var(--color-primary-dark), var(--color-primary), var(--color-primary-light)); display: flex; align-items: center; justify-content: center; }
.banner-inner { text-align: center; color: white; }
.banner-inner .logo-icon { width: 60px; height: 60px; background: rgba(255,255,255,0.2); border-radius: 16px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 26px; margin: 0 auto 16px; backdrop-filter: blur(10px); }
.banner-inner h2 { font-size: 22px; margin-bottom: 4px; }
.banner-inner p { opacity: 0.8; font-size: 14px; }
.login-form-section { flex: 1; padding: 48px 40px; }
.login-form-section h1 { font-size: 28px; font-weight: 700; margin-bottom: 24px; color: var(--text-primary); }
.login-tabs { display: flex; gap: 12px; margin-bottom: 32px; }
.tab-btn { padding: 8px 24px; border-radius: var(--border-radius-sm); font-size: 14px; font-weight: 500; background: var(--bg-tertiary); color: var(--text-secondary); border: none; cursor: pointer; transition: all var(--transition-fast); }
.tab-btn.active { background: var(--color-primary); color: white; }
.form-row { display: flex; justify-content: space-between; margin-top: 4px; margin-bottom: 12px; font-size: 13px; }
.text-muted { color: var(--text-muted); }
.link { color: var(--color-primary); cursor: pointer; }
.link:hover { color: var(--color-primary-dark); }
.submit-btn { width: 100%; height: 48px; font-size: 16px; font-weight: 600; margin-top: 8px; border-radius: var(--border-radius-sm); }
.phone-wrap { display: flex; width: 100%; }
.area-btn { display: flex; align-items: center; gap: 4px; padding: 10px 12px; border: 1px solid var(--border-color); border-right: none; border-radius: 8px 0 0 8px; background: var(--bg-tertiary); cursor: pointer; font-size: 14px; white-space: nowrap; user-select: none; }
.arrow-down { width: 0; height: 0; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid var(--text-secondary); }
.phone-inp { flex: 1; } .phone-inp :deep(.el-input__wrapper) { border-radius: 0 8px 8px 0; }
.area-list { max-height: 240px; overflow-y: auto; }
.area-item { padding: 8px 12px; cursor: pointer; font-size: 13px; border-radius: 4px; }
.area-item:hover { background: var(--bg-tertiary); }
.area-item.active { background: rgba(99,102,241,0.1); color: var(--color-primary); font-weight: 500; }
.eye-btn { background: none; color: var(--text-muted); padding: 2px; display: flex; align-items: center; }
.eye-btn:hover { color: var(--text-secondary); }
@media (max-width: 768px) { .login-banner { display: none; } .login-form-section { padding: 32px 24px; } }
</style>
