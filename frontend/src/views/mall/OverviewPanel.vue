<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never" header=''>
          <el-table :data="endpoints" stripe size="small" v-if="endpoints.length">
            <el-table-column prop="name" label='' width="120" />
            <el-table-column label='' width="80">
              <template #default="{row}">
                <el-tag :type="row.ok ? 'success' : 'danger'' size="small">{{ row.ok ? '' : '' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="code" label='' width="80" />
            <el-table-column prop="error" label='' show-overflow-tooltip />
          </el-table>
          <el-empty v-else description='' :image-size="50" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" header="AI">
          <div v-if="aiSummary && aiSummary.total">
            <p>: <strong>{{ aiSummary.total }}</strong></p>
            <p>: {{ aiSummary.distribution?.hot || 0 }}  : {{ aiSummary.distribution?.warm || 0 }}  : {{ aiSummary.distribution?.cold || 0 }}  : {{ aiSummary.distribution?.dead || 0 }}</p>
          </div>
          <el-empty v-else description="AI" :image-size="50" />
        </el-card>
        <el-card shadow="never" header='' style="margin-top:12px">
          <el-timeline v-if="scanHistory.length">
            <el-timeline-item v-for="h in scanHistory.slice(0,5)" :key="h.time" :timestamp="h.time">
              {{ h.summary }}
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description='' :image-size="40" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
defineProps(['stats', 'endpoints', 'scanHistory', 'aiSummary'])
defineEmits(['scan', 'brain'])
</script>