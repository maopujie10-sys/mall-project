<template>
  <div class="pc-settle"><div class="card" style="max-width:640px;margin:40px auto;padding:40px">
    <h2 style="text-align:center;margin-bottom:8px">商家入驻</h2>
    <p style="text-align:center;color:var(--text-muted);margin-bottom:32px">加入 TikTokMall，向全球用户销售您的商品</p>
    <el-form :model="form" label-width="100px" size="large">
      <el-form-item label="店铺名称"><el-input v-model="form.shopName" /></el-form-item>
      <el-form-item label="联系人"><el-input v-model="form.contact" /></el-form-item>
      <el-form-item label="联系电话"><el-input v-model="form.phone" /></el-form-item>
      <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
      <el-form-item label="店铺类型"><el-select v-model="form.type" style="width:100%"><el-option label="个人" value="personal" /><el-option label="企业" value="company" /></el-select></el-form-item>
      <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="4" /></el-form-item>
      <el-form-item><el-button type="primary" size="large" style="width:100%" @click="submit">提交入驻申请</el-button></el-form-item>
    </el-form>
  </div></div>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { post } from '@/api/index'

const form = reactive({ shopName: '', contact: '', phone: '', email: '', type: 'personal', description: '' })

async function submit() {
  try { await post('/merchant/settle', form); ElMessage.success('申请已提交，等待审核') } catch { ElMessage.error('提交失败') }
}
</script>

<style scoped>.pc-settle { padding: 24px 0; }</style>
