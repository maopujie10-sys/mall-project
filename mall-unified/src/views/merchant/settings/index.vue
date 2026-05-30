<template>
  <div class="merchant-settings"><h2>设置</h2><div class="card">
    <div class="setting-row"><span>修改密码</span><el-button size="small">修改</el-button></div>
    <div class="setting-row"><span>账号安全</span><el-button size="small">管理</el-button></div>
    <div class="setting-row"><span>通知设置</span><el-switch v-model="notifyOn" /></div>
    <div class="setting-row"><span>语言</span><el-select v-model="lang" size="small" style="width:120px"><el-option label="中文" value="zh" /><el-option label="English" value="en" /></el-select></div>
  </div></div>
</template>

<script setup>
import { ref } from 'vue'
const notifyOn = ref(true)
const lang = ref('zh')
</script>

<style scoped>
.merchant-settings { padding: 0; }
h2 { margin-bottom: 24px; }
.setting-row { display: flex; justify-content: space-between; align-items: center; padding: 16px 0; border-bottom: 1px solid var(--border-color); }
</style>
