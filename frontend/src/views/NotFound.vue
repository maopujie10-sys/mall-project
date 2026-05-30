<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <div class="nf-icon">
        <el-icon :size="80" color="var(--text-disabled)"><WarningFilled /></el-icon>
      </div>
      <h1 class="nf-code">404</h1>
      <h2 class="nf-title">{{ \('notFound.title') }}</h2>
      <p class="nf-desc">{{ \('notFound.title') }}</p>
      <div class="nf-actions">
        <el-button type="primary" size="large" @click="$router.push('/dashboard')">
          <el-icon><HomeFilled /></el-icon> 
        </el-button>
        <el-button size="large" @click="$router.go(-1)">
          <el-icon><Back /></el-icon> 
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.not-found-page {
  min-height: 100vh;
  background: rgba(13,16,37,0.55);
  display: flex;
  align-items: center;
  justify-content: center;
}
.not-found-content {
  text-align: center;
  padding: 60px 40px;
}
.nf-icon { margin-bottom: 16px; }
.nf-code {
  font-size: 120px;
  font-weight: 800;
  color: var(--text-disabled);
  line-height: 1;
  letter-spacing: -4px;
  margin-bottom: 8px;
}
.nf-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.nf-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 32px;
}
.nf-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
