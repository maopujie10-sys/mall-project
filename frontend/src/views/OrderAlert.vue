<template>
  <div class="order-alert"><div class="page-header"><h2>🔔 订单异常预警</h2><p>退款突增 · 库存告急 · 物流延迟 · 销售额暴跌 → 自动电话通知</p>
    <div class="header-stats"><el-statistic title="总预警" :value="stats.total" /><el-statistic title="P0紧急" :value="stats.P0" /><el-statistic title="P1重要" :value="stats.P1" /><el-statistic title="今日" :value="stats.today" /><el-statistic title="解决率" :value="stats.resolution_rate" suffix="%" /></div>
  </div>
    <el-row :gutter="16">
      <el-col :span="16">
        <el-tabs v-model="tab">
          <el-tab-pane label="🚨 预警历史" name="history">
            <el-button @click="doCheck" size="small" type="danger" style="margin-bottom:8px">🔍 立即检查</el-button>
            <el-table :data="alerts" stripe size="small">
              <el-table-column prop="checked_at" label="时间" width="150" />
              <el-table-column label="级别" width="60"><template #default="{row}"><el-tag size="small" :type="row.level==='P0'?'danger':row.level==='P1'?'warning':'info'">{{ row.level }}</el-tag></template></el-table-column>
              <el-table-column prop="title" label="标题" width="120" />
              <el-table-column prop="detail" label="详情" min-width="250" show-overflow-tooltip />
              <el-table-column label="状态" width="80"><template #default="{row}"><el-tag size="small" :type="row.level==='P0'?'danger':'warning'">{{ row.level==='P0'?'已电话':'已通知' }}</el-tag></template></el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-col>
      <el-col :span="8">
        <el-card><template #header>⚙️ 预警规则</template>
          <div v-for="r in rules" :key="r.id" style="padding:8px 0;border-bottom:1px solid #f0f0f0">
            <div style="display:flex;justify-content:space-between"><strong>{{ r.name }}</strong><el-tag size="small" :type="r.enabled?'success':'info'">{{ r.enabled?'启用':'禁用' }}</el-tag></div>
            <div style="font-size:12px;color:#999;margin-top:2px">{{ r.metric }} > {{ r.threshold }} → {{ r.channel }}</div>
          </div>
        </el-card>
        <el-card style="margin-top:12px"><template #header>📞 电话告警配置</template>
          <el-descriptions :column="1" size="small"><el-descriptions-item v-for="(v,k) in phoneConfig.phones||{}" :key="k" :label="'P'+k">{{ v||'未配置' }}</el-descriptions-item></el-descriptions>
          <el-tag v-if="phoneConfig.simulate" type="warning" size="small" style="margin-top:8px">⚠️ 模拟模式（未配置真实号码）</el-tag>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"; import { getAlertRules, runAlertCheck, getAlertHistory, getAlertStats } from "@/api/order_alert"
const tab=ref("history"); const alerts=ref([]); const rules=ref([]); const stats=ref({}); const phoneConfig=ref({})
onMounted(async()=>{try{const r=await getAlertRules();if(r.ok)rules.value=r.rules}catch{};try{const r=await getAlertHistory();if(r.ok)alerts.value=r.alerts}catch{};try{const r=await getAlertStats();if(r.ok)stats.value=r.stats||{}}catch{}})
async function doCheck(){try{const r=await runAlertCheck();if(r.ok){ElMessage.info(`检查完成，发现${r.issues_found}个问题`);if(r.issues_found)window.location.reload()}}catch(e){ElMessage.error(e.message)}}
</script>
<style scoped>.order-alert{padding:20px}.page-header{margin-bottom:20px}.page-header h2{margin:0 0 4px}.page-header p{margin:0 0 12px;color:#999;font-size:13px}.header-stats{display:flex;gap:24px}</style>
