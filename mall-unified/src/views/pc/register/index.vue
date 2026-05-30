<template>
  <div class="pc-register fade-in">
    <div class="reg-card card">
      <div class="reg-header"><h2>注册</h2><p>创建 TikTokMall 账号</p></div>
      <el-form ref="formRef" :model="form" :rules="rules" size="large">
        <el-form-item prop="username"><el-input v-model="form.username" placeholder="用户名" /></el-form-item>
        <el-form-item prop="email"><el-input v-model="form.email" placeholder="邮箱" /></el-form-item>
        <el-form-item prop="password"><el-input v-model="form.password" type="password" placeholder="密码（6-12位）" show-password /></el-form-item>
        <el-form-item prop="confirmPassword"><el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" show-password @keyup.enter="handleRegister" /></el-form-item>
        <el-form-item><el-button class="reg-btn" type="primary" :loading="loading" @click="handleRegister">注册</el-button></el-form-item>
      </el-form>
      <p style="text-align:center;font-size:13px;color:var(--text-muted)">已有账号？<router-link to="/pc/login">立即登录</router-link></p>
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
const form = reactive({ username: '', email: '', password: '', confirmPassword: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ type: 'email', message: '有效邮箱', trigger: 'blur' }],
  password: [{ required: true, min: 6, max: 12, message: '6-12位', trigger: 'blur' }],
  confirmPassword: [{ required: true, message: '请确认密码', trigger: 'blur' }, { validator: (_, v, cb) => v !== form.password ? cb('不一致') : cb(), trigger: 'blur' }]
}

async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try { await userStore.register(form); ElMessage.success('注册成功'); router.push('/pc/login') } catch (e) { ElMessage.error(e.message || '注册失败') } finally { loading.value = false }
}
</script>

<style scoped>
.pc-register { min-height: 60vh; display: flex; align-items: center; justify-content: center; padding: 40px 20px; }
.reg-card { width: 100%; max-width: 420px; padding: 40px; }
.reg-header { text-align: center; margin-bottom: 32px; }
.reg-header h2 { font-size: 26px; font-weight: 700; }
.reg-header p { color: var(--text-muted); font-size: 14px; }
.reg-btn { width: 100%; height: 44px; border-radius: var(--border-radius-sm); }
</style>
