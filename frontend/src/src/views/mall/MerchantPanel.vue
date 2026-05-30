<template>
  <div>
    <el-tabs type="card">
      <el-tab-pane label=''>
        <el-table :data="merchants" stripe size="small" v-loading="ml">
          <el-table-column prop="uuid" label="UUID" width="180" />
          <el-table-column prop="name" label='' width="150" />
          <el-table-column prop="status" label='' width="80" />
          <el-table-column label='' width="160">
            <template #default="{row}">
              <el-button size="small" link @click="toggleStatus(row)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="applies" stripe size="small" v-loading="al">
          <el-table-column prop="uuid" label="UUID" width="180" />
          <el-table-column prop="name" label='' width="150" />
          <el-table-column label='' width="160">
            <template #default="{row}">
              <el-button size="small" link type="success" @click="auditApply({uuid:row.uuid,approved:true})">OK</el-button>
              <el-button size="small" link type="danger" @click="auditApply({uuid:row.uuid,approved:false})">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="dashList" stripe size="small" v-loading="dl" />
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="finList" stripe size="small" v-loading="fl" />
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="goodsList" stripe size="small" v-loading="gl">
          <el-table-column prop="goods_id" label="ID" width="180" />
          <el-table-column prop="title" label='' />
          <el-table-column prop="price" label='' width="100" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="ordList" stripe size="small" v-loading="ol">
          <el-table-column prop="order_id" label='' width="180" />
          <el-table-column prop="total" label='' width="100" />
          <el-table-column prop="status" label='' width="80" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getMerchantList, getMerchantApplyList, getMerchantDashboard, getMerchantFinance, getMerchantGoods, getMerchantOrders, updateMerchantStatus, auditMerchantApply } from '@/api/mall'
import { ElMessage } from 'element-plus'
const merchants = ref([]); const ml = ref(false)
const applies = ref([]); const al = ref(false)
const dashList = ref([]); const dl = ref(false)
const finList = ref([]); const fl = ref(false)
const goodsList = ref([]); const gl = ref(false)
const ordList = ref([]); const ol = ref(false)
async function loadAll() {
  ml.value = al.value = dl.value = fl.value = gl.value = ol.value = true
  try { const r = await getMerchantList(); merchants.value = r.list || r.records || [] } catch { }
  try { const r = await getMerchantApplyList(); applies.value = r.list || r.records || [] } catch { }
  try { dashList.value = [await getMerchantDashboard()] } catch { }
  try { const r = await getMerchantFinance(); finList.value = r.list || r.records || [] } catch { }
  try { const r = await getMerchantGoods(); goodsList.value = r.list || r.records || [] } catch { }
  try { const r = await getMerchantOrders(); ordList.value = r.list || r.records || [] } catch { }
  ml.value = al.value = dl.value = fl.value = gl.value = ol.value = false
}
async function toggleStatus(row) { try { await updateMerchantStatus({ uuid: row.uuid, status: row.status === 1 ? 0 : 1 }); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
async function auditApply(data) { try { await auditMerchantApply(data); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
onMounted(loadAll)
</script>