<template>
  <div class="pc-order"><h2>我的订单</h2>
    <el-tabs v-model="activeTab" @tab-change="loadOrders">
      <el-tab-pane label="全部" name="all" />
      <el-tab-pane label="待付款" name="pending" />
      <el-tab-pane label="待收货" name="shipped" />
      <el-tab-pane label="已完成" name="completed" />
    </el-tabs>
    <el-table v-if="orders.length" :data="orders">
      <el-table-column prop="orderNo" label="订单号" width="180" />
      <el-table-column label="商品" />
      <el-table-column label="金额" width="120"><template #default="{row}">¥{{ row.total || row.amount }}</template></el-table-column>
      <el-table-column label="状态" width="100"><template #default="{row}"><el-tag>{{ row.status }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="160"><template #default="{row}"><el-button v-if="row.status==='pending'" type="warning" size="small">付款</el-button><el-button v-if="row.status==='shipped'" type="primary" size="small">确认收货</el-button></template></el-table-column>
    </el-table>
    <div v-else class="empty-state"><p>暂无订单</p></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOrderList } from '@/api/orders'
const orders = ref([])
const activeTab = ref('all')
async function loadOrders() { try { const r = await getOrderList({ status: activeTab.value, page: 1 }); orders.value = ((r.data || r).list || (r.data || r).rows || []) } catch {} }
onMounted(loadOrders)
</script>

<style scoped>
.pc-order { padding: 24px 0; }
h2 { margin-bottom: 24px; }
.empty-state { text-align: center; padding: 60px; }
</style>
