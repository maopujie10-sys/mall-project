<template>
  <div>
    <el-tabs type="card">
      <el-tab-pane label="合同管理">
        <el-table :data="contracts" stripe size="small" v-loading="ctl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="contract_type" label="类型" width="120" />
          <el-table-column prop="status" label="状态" width="80" />
          <el-table-column prop="create_time" label="时间" width="160" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="信用管理">
        <el-table :data="credits" stripe size="small" v-loading="crl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="user_id" label="用户ID" width="80" />
          <el-table-column prop="score" label="信用分" width="100" />
          <el-table-column prop="status" label="状态" width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="借贷管理">
        <el-table :data="loans" stripe size="small" v-loading="ll">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="user_id" label="用户ID" width="80" />
          <el-table-column prop="amount" label="金额" width="100" />
          <el-table-column prop="status" label="状态" width="80" />
          <el-table-column label="操作" width="160">
            <template #default="{row}">
              <el-button size="small" link type="success" @click="auditLoanItem({uuid:row.uuid,approved:true})">通过</el-button>
              <el-button size="small" link type="danger" @click="auditLoanItem({uuid:row.uuid,approved:false})">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="域名轮值">
        <el-table :data="domains" stripe size="small" v-loading="dl">
          <el-table-column prop="domain" label="域名" />
          <el-table-column prop="status" label="状态" width="80" />
          <el-table-column label="操作" width="160">
            <template #default="{row}">
              <el-button size="small" link type="danger" @click="blockD({domain:row.domain})">封禁</el-button>
              <el-button size="small" link type="success" @click="unblockD({domain:row.domain})">解封</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getContractList, getCreditList, getLoanList, auditLoan, getRotationDomains, blockDomain, unblockDomain } from '@/api/mall'
import { ElMessage } from 'element-plus'

const contracts = ref([]); const ctl = ref(false)
const credits = ref([]); const crl = ref(false)
const loans = ref([]); const ll = ref(false)
const domains = ref([]); const dl = ref(false)

async function loadAll() {
  ctl.value = crl.value = ll.value = dl.value = true
  try { const r = await getContractList(); contracts.value = r.list || r.records || [] } catch { }
  try { const r = await getCreditList(); credits.value = r.list || r.records || [] } catch { }
  try { const r = await getLoanList(); loans.value = r.list || r.records || [] } catch { }
  try { const r = await getRotationDomains(); domains.value = r.list || r.records || r || [] } catch { }
  ctl.value = crl.value = ll.value = dl.value = false
}
async function auditLoanItem(data) { try { await auditLoan(data); ElMessage.success('完成'); loadAll() } catch { ElMessage.error('失败') } }
async function blockD(data) { try { await blockDomain(data); ElMessage.success('已封禁'); loadAll() } catch { ElMessage.error('失败') } }
async function unblockD(data) { try { await unblockDomain(data); ElMessage.success('已解封'); loadAll() } catch { ElMessage.error('失败') } }
onMounted(loadAll)
</script>