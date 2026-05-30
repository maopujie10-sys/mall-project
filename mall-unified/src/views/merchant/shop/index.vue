<template>
  <div class="merchant-shop">
    <h2>店铺管理</h2>
    <el-form :model="form" label-width="100px" style="max-width:640px" v-loading="loading">
      <el-form-item label="店铺名称"><el-input v-model="form.name" placeholder="店铺名称" /></el-form-item>
      <el-form-item label="店铺Logo"><el-input v-model="form.logo" placeholder="LOGO URL" /><span style="margin-left:12px;font-size:12px;color:var(--text-muted)">上传功能待接入</span></el-form-item>
      <el-form-item label="店铺描述"><el-input v-model="form.description" type="textarea" :rows="4" placeholder="描述您的店铺" /></el-form-item>
      <el-form-item label="联系方式"><el-input v-model="form.contact" placeholder="电话/邮箱" /></el-form-item>
      <el-form-item label="客服微信"><el-input v-model="form.wechat" placeholder="微信号" /></el-form-item>
      <el-form-item label="店铺地址"><el-input v-model="form.address" placeholder="地址" /></el-form-item>
      <el-form-item label="营业时间"><el-input v-model="form.businessHours" placeholder="如: 9:00-18:00" /></el-form-item>
      <el-form-item><el-button type="primary" @click="save">保存</el-button></el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { get, post, put, del } from '@/api/index'

const loading = ref(false)
const form = reactive({ name: '', logo: '', description: '', contact: '', wechat: '', address: '', businessHours: '' })

onMounted(async () => {
  loading.value = true
  try { const r = await getShopInfo(); const d = r.data || r; Object.assign(form, d) } catch {} finally { loading.value = false }
})
async function save() {
  try { await updateShopInfo(form); ElMessage.success('保存成功') } catch { ElMessage.error('保存失败') }
}
</script>

<style scoped>.merchant-shop { padding: 0; } h2 { margin-bottom: 24px; }</style>
