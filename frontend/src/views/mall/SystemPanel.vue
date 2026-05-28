<template>
  <div>
    <el-tabs type="card">
      <el-tab-pane label="系统参数">
        <el-table :data="sysparas" stripe size="small" v-loading="sp">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="key" label="键" width="180" />
          <el-table-column prop="value" label="值" show-overflow-tooltip />
          <el-table-column label="操作" width="160">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="editSyspara(row)">编辑</el-button>
              <el-button size="small" link type="danger" @click="delSyspara(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="区域">
        <el-table :data="countries" stripe size="small" v-loading="al">
          <el-table-column prop="name" label="国家/地区" />
          <el-table-column prop="code" label="代码" width="80" />
          <el-table-column prop="prefix" label="区号" width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="商城等级">
        <el-table :data="levels" stripe size="small" v-loading="mll">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="name" label="等级名" width="120" />
          <el-table-column prop="threshold" label="门槛" width="100" />
          <el-table-column prop="benefits" label="权益" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="套餐">
        <el-table :data="combos" stripe size="small" v-loading="cbl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="name" label="名称" width="150" />
          <el-table-column prop="price" label="价格" width="100" />
          <el-table-column prop="description" label="描述" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="身份证">
        <el-table :data="idcodes" stripe size="small" v-loading="idl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="user_id" label="用户ID" width="80" />
          <el-table-column prop="real_name" label="姓名" width="100" />
          <el-table-column prop="status" label="状态" width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="管理员">
        <el-table :data="admins" stripe size="small" v-loading="adml">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="role" label="角色" width="100" />
          <el-table-column prop="status" label="状态" width="80" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
    <el-dialog title="编辑系统参数" v-model="sysparaDialog" width="400px">
      <el-form :model="sysparaForm" label-width="60px">
        <el-form-item label="键"><el-input v-model="sysparaForm.key" /></el-form-item>
        <el-form-item label="值"><el-input v-model="sysparaForm.value" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="sysparaDialog=false">取消</el-button><el-button type="primary" @click="saveSyspara">保存</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getSysparaList, saveSyspara, updateSyspara, deleteSyspara, getAreaCountries, getMallLevelList, getComboList, getIdcodeList, getAdminList } from '@/api/mall'
import { ElMessage } from 'element-plus'

const sysparas = ref([]); const sp = ref(false)
const countries = ref([]); const al = ref(false)
const levels = ref([]); const mll = ref(false)
const combos = ref([]); const cbl = ref(false)
const idcodes = ref([]); const idl = ref(false)
const admins = ref([]); const adml = ref(false)
const sysparaDialog = ref(false)
const sysparaForm = ref({ id: null, key: '', value: '' })

async function loadAll() {
  sp.value = al.value = mll.value = cbl.value = idl.value = adml.value = true
  try { const r = await getSysparaList(); sysparas.value = r.list || r.records || r || [] } catch { }
  try { const r = await getAreaCountries('zh'); countries.value = r || [] } catch { }
  try { const r = await getMallLevelList(); levels.value = r.list || r.records || [] } catch { }
  try { const r = await getComboList(); combos.value = r.list || r.records || [] } catch { }
  try { const r = await getIdcodeList(); idcodes.value = r.list || r.records || [] } catch { }
  try { const r = await getAdminList(); admins.value = r.list || r.records || [] } catch { }
  sp.value = al.value = mll.value = cbl.value = idl.value = adml.value = false
}
function editSyspara(row) { sysparaForm.value = { ...row }; sysparaDialog.value = true }
async function saveSyspara() {
  try {
    if (sysparaForm.value.id) await updateSyspara(sysparaForm.value.id, sysparaForm.value)
    else await saveSyspara(sysparaForm.value)
    ElMessage.success('成功'); sysparaDialog.value = false; loadAll()
  } catch { ElMessage.error('失败') }
}
async function delSyspara(id) { try { await deleteSyspara(id); ElMessage.success('成功'); loadAll() } catch { ElMessage.error('失败') } }
onMounted(loadAll)
</script>