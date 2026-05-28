<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never" header="端点状态">
          <el-table :data="endpoints" stripe size="small" v-if="endpoints.length">
            <el-table-column prop="name" label="端点" width="120" />
            <el-table-column label="状态" width="80">
              <template #default="{row}">
                <el-tag :type="row.ok ? 'success' : 'danger'" size="small">{{ row.ok ? '正常' : '异常' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="code" label="状态码" width="80" />
            <el-table-column prop="error" label="错误信息" show-overflow-tooltip />
          </el-table>
          <el-empty v-else description="点击一键扫描" :image-size="50" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" header="AI大脑摘要">
          <div v-if="aiSummary && aiSummary.total">
            <p>分析商品: <strong>{{ aiSummary.total }}</strong></p>
            <p>热门: {{ aiSummary.distribution?.hot || 0 }} · 温: {{ aiSummary.distribution?.warm || 0 }} · 冷: {{ aiSummary.distribution?.cold || 0 }} · 死: {{ aiSummary.distribution?.dead || 0 }}</p>
          </div>
          <el-empty v-else description="点击AI大脑分析" :image-size="50" />
        </el-card>
        <el-card shadow="never" header="扫描历史" style="margin-top:12px">
          <el-timeline v-if="scanHistory.length">
            <el-timeline-item v-for="h in scanHistory.slice(0,5)" :key="h.time" :timestamp="h.time">
              {{ h.summary }}
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无记录" :image-size="40" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
defineProps(['stats', 'endpoints', 'scanHistory', 'aiSummary'])
defineEmits(['scan', 'brain'])
</script>