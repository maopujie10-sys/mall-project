<template>
  <div class="merchant-reg"><div class="card" style="max-width:560px;margin:40px auto;padding:40px">
    <h2 style="text-align:center;margin-bottom:24px">商家入驻申请</h2>
    <el-form :model="form" label-width="100px" size="large">
      <el-form-item label="店铺名称"><el-input v-model="form.shopName" placeholder="您的店铺名称" /></el-form-item>
      <el-form-item label="联系人"><el-input v-model="form.contact" placeholder="联系人姓名" /></el-form-item>
      <el-form-item label="手机号"><el-input v-model="form.phone" placeholder="手机号码" /></el-form-item>
      <el-form-item label="邮箱"><el-input v-model="form.email" placeholder="联系邮箱" /></el-form-item>
      <el-form-item label="店铺类型"><el-select v-model="form.type" placeholder="选择类型" style="width:100%"><el-option label="个人" value="personal" /><el-option label="企业" value="company" /></el-select></el-form-item>
      <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" placeholder="简单描述您的业务" /></el-form-item>
      <el-form-item><el-button type="primary" style="width:100%" @click="submit">提交申请</el-button></el-form-item>
    </el-form>
  </div></div>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { get, post, put, del } from '@/api/index'

const form = reactive({ shopName: '', contact: '', phone: '', email: '', type: 'personal', description: '' })

async function submit() {
  try { await post('/merchant/settle', form); ElMessage.success('申请已提交，等待审核') } catch { ElMessage.error('提交失败') }
}
</script>

<style scoped>.merchant-reg { padding: 24px; }</style>
