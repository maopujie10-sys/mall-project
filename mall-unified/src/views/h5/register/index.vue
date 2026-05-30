<template>
  <div class="register-page">
    <!-- 顶部 -->
    <div class="register-header">
      <div class="header-right" v-if="isShelves">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" fill="#94a3b8"/>
        </svg>
      </div>
    </div>

    <h1 class="register-title">{{ $t('common.register') }}</h1>

    <!-- Tab 切换 (特殊项目隐藏) -->
    <div class="tab-row" v-if="!isSpecialItem">
      <button :class="['tab-btn', { active: TabShow === 1 }]" @click="TabClick(1)">{{ $t('common.phoneLogin') }}</button>
      <button :class="['tab-btn', { active: TabShow === 2 }]" @click="TabClick(2)">{{ $t('common.emailLogin') }}</button>
    </div>

    <!-- 表单 -->
    <div class="form-section">
      <!-- 手机号输入 (TabShow === 1) -->
      <van-field
        v-if="TabShow === 1"
        v-model="formData.username"
        :label="$t('common.phone')"
        :placeholder="$t('common.phone') + '...'"
        maxlength="20"
        clearable
        class="form-field"
        @update:model-value="onPhoneInput"
      >
        <template #left-icon>
          <span class="dial-code-btn" @click.stop="openNational">
            +{{ dialCode }}
            <svg width="10" height="6" viewBox="0 0 10 6" fill="none">
              <path d="M1 1l4 4 4-4" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
        </template>
      </van-field>

      <!-- 邮箱输入 (TabShow === 2) -->
      <van-field
        v-if="TabShow === 2"
        v-model="formData.username"
        :label="$t('common.emailLogin')"
        :placeholder="$t('common.emailLogin') + '...'"
        maxlength="64"
        clearable
        class="form-field"
      />

      <!-- 特殊项目: 验证码 + 手机号 -->
      <template v-if="isSpecialItem">
        <van-field
          v-model="formData.phone"
          :label="$t('common.phone')"
          :placeholder="$t('common.phone') + '...'"
          maxlength="20"
          clearable
          class="form-field"
          @update:model-value="onPhoneInput2"
        >
          <template #left-icon>
            <span class="dial-code-btn" @click.stop="openNational">
              +{{ dialCode }}
              <svg width="10" height="6" viewBox="0 0 10 6" fill="none">
                <path d="M1 1l4 4 4-4" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
          </template>
        </van-field>
      </template>

      <!-- 密码 -->
      <van-field
        v-model="formData.password"
        type="password"
        :label="$t('common.password')"
        :placeholder="$t('common.password') + ' (6-12 位)...'"
        maxlength="20"
        class="form-field"
      />

      <!-- 确认密码 -->
      <van-field
        v-model="formData.re_password"
        type="password"
        :label="$t('common.confirmPassword')"
        :placeholder="$t('common.confirmPassword') + '...'"
        maxlength="20"
        class="form-field"
      />
    </div>

    <!-- 注册按钮 -->
    <button class="register-submit-btn" @click="postForm">
      {{ $t('common.register') }}
    </button>

    <!-- 去登录 -->
    <div class="login-row">
      <span class="login-line"></span>
      <span class="login-text">{{ $t('common.hasAccount') }}</span>
      <router-link to="/m/login" class="login-link">{{ $t('common.goLogin') }}</router-link>
      <span class="login-line"></span>
    </div>

    <!-- 客服 -->
    <div class="customer-service" @click="handleJump">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="var(--color-primary)" stroke-width="2"/>
        <path d="M8 14s1.5 2 4 2 4-2 4-2" stroke="var(--color-primary)" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="9" cy="9.5" r="1" fill="var(--color-primary)"/>
        <circle cx="15" cy="9.5" r="1" fill="var(--color-primary)"/>
      </svg>
    </div>

    <!-- 验证弹窗 -->
    <van-overlay :show="showCaptcha" @click="showCaptcha = false">
      <div class="captcha-modal" @click.stop>
        <div class="captcha-title">{{ $t('common.sliderVerify') }}</div>
        <p class="captcha-hint">{{ $t('common.dragToComplete') }}</p>
        <div class="captcha-placeholder">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="3" width="18" height="18" rx="3" stroke="var(--color-primary)" stroke-width="1.5"/>
            <path d="M8 12l3 3 5-5" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>{{ $t('common.verifyPass') }}</span>
        </div>
        <button class="captcha-confirm-btn" @click="onCaptchaSuccess">
          {{ $t('common.confirm') }}
        </button>
      </div>
    </van-overlay>

    <!-- 国家码选择 -->
    <van-action-sheet v-model:show="showNational" :title="$t('common.selectCountryCode')">
      <div class="country-list">
        <div v-for="item in countryCodes" :key="item.code" class="country-item" @click="selectCountry(item)">
          <span>{{ item.name }}</span>
          <span class="country-code">+{{ item.code }}</span>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import {
  Field as VanField,
  Overlay as VanOverlay,
  ActionSheet as VanActionSheet,
  showToast,
  showNotify
} from 'vant'
import { useUserStore } from '@/stores/user'
import { registerNoVerifcode, justShopRegister } from '@/api/user'
import { registerApi } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

// ===== State (preserved from original) =====
const isShelves = ref(true)
const isSpecialItem = ref(false) // SM-wholesaleShop, FamilyShop
const TabShow = ref(isSpecialItem.value ? 2 : 1)
const showCaptcha = ref(false)
const dialCode = ref(localStorage.getItem('dialCode') || '1')
const showNational = ref(false)
const pageDiaCode = ref(false)

const formData = reactive({
  username: '',
  password: '',
  re_password: '',
  verifcode: '',
  phone: ''
})

const countryCodes = [
  { name: 'US/Canada', code: '1' },
  { name: 'China', code: '86' },
  { name: 'UK', code: '44' },
  { name: 'Japan', code: '81' },
  { name: 'South Korea', code: '82' },
  { name: 'Thailand', code: '66' },
  { name: 'Vietnam', code: '84' },
  { name: 'Philippines', code: '63' },
  { name: 'Malaysia', code: '60' },
  { name: 'Indonesia', code: '62' },
  { name: 'India', code: '91' },
  { name: 'Germany', code: '49' },
  { name: 'France', code: '33' },
  { name: 'Russia', code: '7' },
  { name: 'Brazil', code: '55' }
]

// ===== Lifecycle (preserved from original) =====
if (userStore.isLoggedIn) {
  router.push('/')
}

// ===== Methods (preserved from original) =====
function TabClick(e) {
  TabShow.value = e
  formData.username = ''
  formData.password = ''
  formData.re_password = ''
}

function onPhoneInput(val) {
  formData.username = val.replace(/[^\d]/g, '')
}

function onPhoneInput2(val) {
  formData.phone = val.replace(/[^\d]/g, '')
}

function openNational() {
  showNational.value = true
}

function selectCountry(item) {
  if (!pageDiaCode.value) {
    pageDiaCode.value = true
  } else {
    dialCode.value = item.code
    localStorage.setItem('dialCode', item.code)
  }
  showNational.value = false
}

function handleJump() {
  router.push({ path: '/m/settings' })
}

function postForm() {
  if (TabShow.value === 1) {
    if (formData.username === '') {
      showToast('请输入手机号')
      return
    }
    const reg = /^[0-9]+[0-9]*$/
    if (!reg.test(formData.username)) {
      showToast('手机号格式有误')
      return
    }
  }
  if (TabShow.value === 2) {
    if (formData.username === '') {
      showToast('请输入邮箱')
      return
    }
    const reg = /^([A-Za-z0-9_\-\.\w{3,}])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/
    if (!reg.test(formData.username)) {
      showToast('邮箱格式有误')
      return
    }
  }

  if (formData.password === '') {
    showToast('请输入密码')
    return
  }

  const pwdReg = /^[a-zA-Z0-9!@#$%^&*()_+{}\[\]:;'"\\|,.<>?~`\-=/]{6,12}$/
  if (!pwdReg.test(formData.password)) {
    showToast('请输入 6-12 位由数字或字母组成的密码')
    return
  }

  if (formData.password !== formData.re_password) {
    showToast('两次密码输入不一致')
    return
  }

  showCaptcha.value = true
}

function onCaptchaSuccess() {
  showCaptcha.value = false
  registerSubmit()
}

async function registerSubmit() {
  const requestFn = isSpecialItem.value ? justShopRegister : registerApi

  const params = {
    password: encodeURIComponent(formData.password)?.trim(),
    re_password: encodeURIComponent(formData.re_password)?.trim(),
    type: TabShow.value
  }

  if (sessionStorage.getItem('ac_code')) {
    params.agentCode = sessionStorage.getItem('ac_code')
    sessionStorage.removeItem('ac_code')
  }

  if (isSpecialItem.value) {
    params.verifcode = formData.verifcode
    params.phone = formData.phone
    params.username = formData.username.trim()
  } else {
    params.username = TabShow.value === 1
      ? `${dialCode.value} ${formData.username.trim()}`
      : formData.username.trim()
  }

  showToast({ type: 'loading', message: '提交中', duration: 0, forbidClick: true })

  try {
    const res = await requestFn(params)
    showToast.clear()
    showNotify({ type: 'success', message: '注册成功' })
    localStorage.setItem('token', res.token)
    let timeZone = ''
    try {
      timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone
    } catch (e) {}
    localStorage.setItem('timeZone', timeZone)
    await userStore.fetchUserInfo()
    router.push({ path: '/' })
  } catch (err) {
    showToast.clear()
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  padding: 0 24px;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
}

.register-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 12px 0;
}

.header-right {
  padding: 8px;
}

.register-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 16px 0 28px;
}

/* Tab */
.tab-row {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}

.tab-btn {
  padding: 7px 20px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.tab-btn.active {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #fff;
  box-shadow: var(--shadow-md);
}

/* 表单 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-section :deep(.van-field) {
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 12px 16px;
  border: 1.5px solid transparent;
  transition: all var(--transition-fast);
}

.form-section :deep(.van-field:focus-within) {
  border-color: var(--color-primary);
  background: var(--bg-primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.dial-code-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  padding-right: 12px;
  border-right: 1px solid var(--border-color);
  cursor: pointer;
  white-space: nowrap;
}

/* 注册按钮 */
.register-submit-btn {
  width: 100%;
  height: 46px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: var(--border-radius);
  border: none;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 24px;
  transition: opacity var(--transition-fast), transform var(--transition-fast);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.register-submit-btn:hover { opacity: 0.92; transform: translateY(-1px); }
.register-submit-btn:active { transform: scale(0.98); }

/* 登录链接 */
.login-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin: 20px 0;
}

.login-line {
  flex: 1;
  height: 1px;
  background: var(--border-color);
}

.login-text {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.login-link {
  font-size: 14px;
  color: var(--color-primary);
  font-weight: 500;
}

/* 客服 */
.customer-service {
  display: flex;
  justify-content: center;
  margin-top: auto;
  padding: 24px 0;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity var(--transition-fast);
}

.customer-service:hover { opacity: 1; }

/* 验证弹窗 */
.captcha-modal {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 300px;
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  padding: 24px;
  text-align: center;
  box-shadow: var(--shadow-xl);
}

.captcha-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.captcha-hint {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.captcha-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  margin-bottom: 16px;
  color: var(--color-primary);
  font-size: 14px;
}

.captcha-confirm-btn {
  width: 100%;
  height: 40px;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--border-radius-sm);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

/* 国家码 */
.country-list {
  max-height: 320px;
  overflow-y: auto;
  padding: 8px 0;
}

.country-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.country-item:hover { background: var(--bg-tertiary); }

.country-code {
  color: var(--text-muted);
  font-weight: 500;
}
</style>
