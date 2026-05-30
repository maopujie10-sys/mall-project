<template>
  <div>
    <el-tabs type="card">
      <el-tab-pane label=''>
        <el-table :data="sysparas" stripe size="small" v-loading="sp">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="key" label='' width="180" />
          <el-table-column prop="value" label='' show-overflow-tooltip />
          <el-table-column label='' width="160">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="editSyspara(row)">OK</el-button>
              <el-button size="small" link type="danger" @click="delSyspara(row.id)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label='国家'>
        <div style="margin-bottom:12px"><el-button size="small" type="primary" @click="showCountryForm()">添加国家</el-button></div>
        <el-table :data="countries" stripe size="small" v-loading="al">
          <el-table-column prop="name" label="国家名称" />
          <el-table-column prop="code" label='代码' width="80" />
          <el-table-column prop="prefix" label='区号' width="80" />
          <el-table-column label='操作' width="160">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="showCountryForm(row)">编辑</el-button>
              <el-button size="small" link type="danger" @click="delCountry(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <!-- 城市子表 -->
        <el-divider>城市管理</el-divider>
        <div style="margin-bottom:12px">
          <el-select v-model="cityCountryFilter" placeholder="筛选国家" style="width:180px" clearable @change="fetchCities">
            <el-option v-for="c in countries" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <el-button size="small" type="primary" @click="showCityForm()">添加城市</el-button>
        </div>
        <el-table :data="adminCities" stripe size="small" v-loading="acl">
          <el-table-column prop="name" label="城市名称" />
          <el-table-column prop="countryId" label="国家ID" width="80" />
          <el-table-column label='操作' width="160">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="showCityForm(row)">编辑</el-button>
              <el-button size="small" link type="danger" @click="delCity(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label='评级'>
        <el-table :data="levels" stripe size="small" v-loading="mll">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="name" label='名称' width="120" />
          <el-table-column prop="threshold" label='门槛' width="100" />
          <el-table-column prop="benefits" label='权益' />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label='套餐'>
        <div style="margin-bottom:12px"><el-button size="small" type="primary" @click="showComboForm()">添加套餐</el-button></div>
        <el-table :data="combos" stripe size="small" v-loading="cbl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="name" label='名称' width="150" />
          <el-table-column prop="price" label='价格' width="100" />
          <el-table-column prop="description" label='描述' />
          <el-table-column label='操作' width="160">
            <template #default="{row}">
              <el-button size="small" link type="primary" @click="showComboForm(row)">编辑</el-button>
              <el-button size="small" link type="danger" @click="delCombo(row.uuid)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="idcodes" stripe size="small" v-loading="idl">
          <el-table-column prop="uuid" label="UUID" width="200" />
          <el-table-column prop="user_id" label="ID" width="80" />
          <el-table-column prop="real_name" label='' width="100" />
          <el-table-column prop="status" label='' width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label=''>
        <el-table :data="admins" stripe size="small" v-loading="adml">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label='' width="120" />
          <el-table-column prop="role" label='' width="100" />
          <el-table-column prop="status" label='' width="80" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
    <el-dialog title='系统参数' v-model="sysparaDialog" width="400px">
      <el-form :model="sysparaForm" label-width="60px">
        <el-form-item label='Key'><el-input v-model="sysparaForm.key" /></el-form-item>
        <el-form-item label='Value'><el-input v-model="sysparaForm.value" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="sysparaDialog=false">取消</el-button><el-button type="primary" @click="saveSyspara">保存</el-button></template>
    </el-dialog>
    <!-- 国家弹窗 -->
    <el-dialog :title="editingCountry?.id?'编辑国家':'添加国家'" v-model="countryDialog" width="400px">
      <el-form :model="countryForm" label-width="80px">
        <el-form-item label='名称'><el-input v-model="countryForm.name" /></el-form-item>
        <el-form-item label='代码'><el-input v-model="countryForm.code" /></el-form-item>
        <el-form-item label='区号'><el-input v-model="countryForm.prefix" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="countryDialog=false">取消</el-button><el-button type="primary" @click="saveCountry">保存</el-button></template>
    </el-dialog>
    <!-- 城市弹窗 -->
    <el-dialog :title="editingCity?.id?'编辑城市':'添加城市'" v-model="cityDialog" width="400px">
      <el-form :model="cityForm" label-width="80px">
        <el-form-item label='名称'><el-input v-model="cityForm.name" /></el-form-item>
        <el-form-item label='国家'>
          <el-select v-model="cityForm.countryId" style="width:100%" placeholder="选择国家">
            <el-option v-for="c in countries" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="cityDialog=false">取消</el-button><el-button type="primary" @click="saveCity">保存</el-button></template>
    </el-dialog>
    <!-- 套餐弹窗 -->
    <el-dialog :title="editingCombo?.uuid?'编辑套餐':'添加套餐'" v-model="comboDialog" width="400px">
      <el-form :model="comboForm" label-width="80px">
        <el-form-item label='名称'><el-input v-model="comboForm.name" /></el-form-item>
        <el-form-item label='价格'><el-input v-model="comboForm.price" /></el-form-item>
        <el-form-item label='描述'><el-input v-model="comboForm.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="comboDialog=false">取消</el-button><el-button type="primary" @click="saveCombo">保存</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { getSysparaList, saveSyspara, updateSyspara, deleteSyspara, getAreaCountries, getAreaAdminCountries, saveAreaCountry, updateAreaCountry, deleteAreaCountry, getAreaAdminCities, saveAreaCity, updateAreaCity, deleteAreaCity, getMallLevelList, getComboList, saveCombo as saveC, updateCombo as updateC, deleteCombo as deleteC, getIdcodeList, getAdminList } from '@/api/mall'
import { ElMessage, ElMessageBox } from 'element-plus'

const sysparas = ref([]); const sp = ref(false)
const countries = ref([]); const al = ref(false)
const levels = ref([]); const mll = ref(false)
const combos = ref([]); const cbl = ref(false)
const idcodes = ref([]); const idl = ref(false)
const admins = ref([]); const adml = ref(false)
const sysparaDialog = ref(false)
const sysparaForm = ref({ id: null, key: '', value: '' })
// 国家/城市/套餐管理
const countryDialog = ref(false); const editingCountry = ref(null)
const countryForm = ref({ name: '', code: '', prefix: '' })
const cityDialog = ref(false); const editingCity = ref(null)
const cityForm = ref({ name: '', countryId: '' })
const adminCities = ref([]); const acl = ref(false); const cityCountryFilter = ref('')
const comboDialog = ref(false); const editingCombo = ref(null)
const comboForm = ref({ name: '', price: '', description: '' })

async function loadAll() {
  sp.value = true; al.value = true; mll.value = true; cbl.value = true; idl.value = true; adml.value = true
  try { const r = await getSysparaList(); sysparas.value = r.list || r.records || r || [] } catch { }
  try { const r = await getAreaAdminCountries({ page: 1, size: 100 }); countries.value = r.list || r.records || r || [] } catch { }
  try { const r = await getMallLevelList(); levels.value = r.list || r.records || [] } catch { }
  try { const r = await getComboList(); combos.value = r.list || r.records || [] } catch { }
  try { const r = await getIdcodeList(); idcodes.value = r.list || r.records || [] } catch { }
  try { const r = await getAdminList(); admins.value = r.list || r.records || [] } catch { }
  sp.value = false; al.value = false; mll.value = false; cbl.value = false; idl.value = false; adml.value = false
}
function editSyspara(row) { sysparaForm.value = { ...row }; sysparaDialog.value = true }
async function saveSyspara() {
  try {
    if (sysparaForm.value.id) await updateSyspara(sysparaForm.value.id, sysparaForm.value)
    else await saveSyspara(sysparaForm.value)
    ElMessage.success('OK'); sysparaDialog.value = false; loadAll()
  } catch { ElMessage.error('Error') }
}
async function delSyspara(id) { try { await deleteSyspara(id); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
// 国家
function showCountryForm(row) { editingCountry.value = row; countryForm.value = row ? { name: row.name||'', code: row.code||'', prefix: row.prefix||'' } : { name:'', code:'', prefix:'' }; countryDialog.value = true }
async function saveCountry() {
  try {
    if (editingCountry.value?.id) await updateAreaCountry(editingCountry.value.id, countryForm.value)
    else await saveAreaCountry(countryForm.value)
    ElMessage.success('OK'); countryDialog.value = false; loadAll()
  } catch { ElMessage.error('Error') }
}
async function delCountry(id) { await ElMessageBox.confirm('确认删除?'); try { await deleteAreaCountry(id); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
// 城市
async function fetchCities() {
  acl.value = true
  try { const r = await getAreaAdminCities({ page:1, size:100, country_id: cityCountryFilter.value || undefined }); adminCities.value = r.list || r.records || r || [] } catch { }
  acl.value = false
}
function showCityForm(row) { editingCity.value = row; cityForm.value = row ? { name: row.name||'', countryId: row.countryId||'' } : { name:'', countryId: cityCountryFilter.value||'' }; cityDialog.value = true }
async function saveCity() {
  try {
    if (editingCity.value?.id) await updateAreaCity(editingCity.value.id, cityForm.value)
    else await saveAreaCity(cityForm.value)
    ElMessage.success('OK'); cityDialog.value = false; fetchCities()
  } catch { ElMessage.error('Error') }
}
async function delCity(id) { await ElMessageBox.confirm('确认删除?'); try { await deleteAreaCity(id); ElMessage.success('OK'); fetchCities() } catch { ElMessage.error('Error') } }
// 套餐
function showComboForm(row) { editingCombo.value = row; comboForm.value = row ? { name: row.name||'', price: row.price||'', description: row.description||'' } : { name:'', price:'', description:'' }; comboDialog.value = true }
async function saveCombo() {
  try {
    if (editingCombo.value?.uuid) await updateC(editingCombo.value.uuid, comboForm.value)
    else await saveC(comboForm.value)
    ElMessage.success('OK'); comboDialog.value = false; loadAll()
  } catch { ElMessage.error('Error') }
}
async function delCombo(uuid) { await ElMessageBox.confirm('确认删除?'); try { await deleteC(uuid); ElMessage.success('OK'); loadAll() } catch { ElMessage.error('Error') } }
onMounted(loadAll)
</script>