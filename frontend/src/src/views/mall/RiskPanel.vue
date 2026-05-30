<template>
  <div>
    <el-tabs type="card">
      <el-tab-pane label=''>
        <el-table :data="contracts" stripe size="small" v-loading="ctl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="contract_type" label='' width="120" />
          <el-table-column prop="status" label='' width="80" />
          <el-table-column prop="create_time" label='' width="160" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="credits" stripe size="small" v-loading="crl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="user_id" label="ID" width="80" />
          <el-table-column prop="score" label='' width="100" />
          <el-table-column prop="status" label='' width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="loans" stripe size="small" v-loading="ll">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="user_id" label="ID" width="80" />
          <el-table-column prop="amount" label='' width="100" />
          <el-table-column prop="status" label='' width="80" />
          <el-table-column label='' width="160">
            <template #default="{row}">
              <el-button size="small" link type="success" @click="auditLoan({uuid:row.uuid,approved:true})">OK</el-button>
              <el-button size="small" link type="danger" @click="auditLoan({uuid:row.uuid,approved:false})">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="domains" stripe size="small" v-loading="dl">
          <el-table-column prop="domain" label='' />
          <el-table-column prop="status" label='' width="80" />
          <el-table-column label='' width="160">
            <template #default="{row}">
              <el-button size="small" link type="danger" @click="blockDomain({domain:row.domain})">OK</el-button>
              <el-button size="small" link type="success" @click="unblockDomain({domain:row.domain})">OK</el-button>
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
async function auditLoanItem(data) { try { await auditLoan(data); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
async function blockD(data) { try { await blockDomain(data); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
async function unblockD(data) { try { await unblockDomain(data); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
onMounted(loadAll)
</script>