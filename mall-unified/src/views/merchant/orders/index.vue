<template>
  <div class="merchant-orders">
    <div class="top-bar"><h2>订单管理</h2>
      <el-select v-model="statusFilter" placeholder="筛选状态" clearable @change="load">
        <el-option label="全部" value="" /><el-option label="待付款" value="pending" /><el-option label="待发货" value="paid" /><el-option label="已发货" value="shipped" /><el-option label="已完成" value="completed" /><el-option label="已取消" value="cancelled" />
      </el-select>
    </div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="orderNo" label="订单号" width="180" />
      <el-table-column label="买家" width="100"><template #default="{row}">{{ row.buyerName || row.username }}</template></el-table-column>
      <el-table-column label="商品" min-width="200"><template #default="{row}">{{ (row.items || [row]).map(i => i.name || i.goodsName).join('、') }}</template></el-table-column>
      <el-table-column label="金额" width="100"><template #default="{row}">¥{{ row.totalAmount || row.total || row.amount }}</template></el-table-column>
      <el-table-column label="状态" width="90"><template #default="{row}"><el-tag :type="statusType(row.status)" size="small">{{ row.statusText || row.status }}</el-tag></template></el-table-column>
      <el-table-column label="时间" width="160"><template #default="{row}">{{ row.createTime || row.createdAt }}</template></el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{row}">
          <el-button v-if="row.status === 'paid'" size="small" type="primary" @click="doShip(row)">发货</el-button>
          <el-button size="small" @click="viewDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination-wrap"><el-pagination background layout="prev, pager, next" :total="total" :page-size="20" @current-change="load" /></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { get, post, put, del } from '@/api/index'

const list = ref([]); const loading = ref(false); const total = ref(0); const statusFilter = ref('')
const statusMap = { pending: '待付款', paid: '待发货', shipped: '已发货', completed: '已完成', cancelled: '已取消' }
function statusType(s) { return s === 'completed' ? 'success' : s === 'cancelled' ? 'info' : s === 'pending' ? 'warning' : '' }
function viewDetail(row) { ElMessage.info('订单号: ' + (row.orderNo || row.id)) }

async function load(page = 1) {
  loading.value = true
  try {
    const params = { page, size: 20 }
    if (statusFilter.value) params.status = statusFilter.value
    const r = await post('/api/merchant/order/list', params)
    const d = r.data || r
    list.value = (d.list || d.records || []).map(o => ({ ...o, statusText: statusMap[o.status] || o.status }))
    total.value = d.total || 0
  } catch {} finally { loading.value = false }
}

async function doShip(row) {
  try {
    const { value: trackingNo } = await ElMessageBox.prompt('请输入快递单号', '发货', { confirmButtonText: '确认发货' })
    await post('/api/merchant/order/ship', { orderId: row.id || row.orderId, trackingNo })
    ElMessage.success('发货成功')
    load()
  } catch {}
}

onMounted(() => load())
</script>

<style scoped>
.merchant-orders { padding: 0; }
.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 20px; }
</style>
