<template>
  <div class="merchant-login fade-in">
    <div class="login-card card">
      <div class="login-header">
        <div class="merchant-logo">🏪</div>
        <h2>商家登录</h2>
        <p>TikTokMall 商家管理中心</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" size="large">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名 / 邮箱" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button class="login-btn" type="primary" :loading="loading" @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        <router-link to="/seller/register">注册商家账号</router-link>
        <router-link to="/m/seller/shop">手机端管理</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const formRef = ref(null)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/seller/dashboard')
  } catch (e) {
    ElMessage.error(e.message || '登录失败')
  } finally { loading.value = false }
}
</script>

<style scoped>
.merchant-login { min-height: 80vh; display: flex; align-items: center; justify-content: center; padding: 40px 20px; background: var(--bg-secondary); }
.login-card { width: 100%; max-width: 440px; padding: 48px 40px; }
.login-header { text-align: center; margin-bottom: 36px; }
.merchant-logo { font-size: 48px; margin-bottom: 12px; }
.login-header h2 { font-size: 24px; font-weight: 700; }
.login-header p { color: var(--text-muted); font-size: 14px; margin-top: 4px; }
.login-btn { width: 100%; height: 44px; border-radius: var(--border-radius-sm); background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark)) !important; border: none !important; }
.login-footer { display: flex; justify-content: space-between; margin-top: 20px; }
.login-footer a { font-size: 13px; color: var(--text-muted); }
</style>
