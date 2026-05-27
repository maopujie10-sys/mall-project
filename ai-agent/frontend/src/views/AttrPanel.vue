<template>
  <div class="attr-panel">
    <el-row :gutter="16">
      <!-- 左侧：属性分类 -->
      <el-col :span="8">
        <el-card shadow="never" class="card-panel">
          <template #header>
            <div class="card-hd">
              <span>属性分类</span>
              <el-button type="primary" size="small" @click="showCatDlg(null)">新增</el-button>
            </div>
          </template>
          <el-input v-model="catKw" placeholder="搜索分类" size="small" clearable @clear="fetchCats" @keyup.enter="fetchCats" style="margin-bottom:8px" />
          <div class="cat-list">
            <div v-for="c in cats" :key="c.id"
              class="cat-item" :class="{on: selectedCat?.id === c.id}"
              @click="selectCat(c)">
              <span class="cat-name">{{ c.name }}</span>
              <span class="cat-acts">
                <el-button link size="small" type="primary" @click.stop="showCatDlg(c)"><el-icon><Edit /></el-icon></el-button>
                <el-button link size="small" type="danger" @click.stop="delCat(c)"><el-icon><Delete /></el-icon></el-button>
              </span>
            </div>
            <el-empty v-if="!cats.length" description="暂无分类" :image-size="60" />
          </div>
          <el-pagination v-if="catTotal > catPageSize" style="margin-top:8px;justify-content:center" small layout="prev,next" :total="catTotal" :page-size="catPageSize" v-model:current-page="catPg" @current-change="fetchCats" />
        </el-card>
      </el-col>

      <!-- 右侧：属性 + 属性值 -->
      <el-col :span="16">
        <el-card v-if="selectedCat" shadow="never" class="card-panel">
          <template #header>
            <div class="card-hd">
              <span>属性列表 — {{ selectedCat.name }}</span>
              <el-button type="primary" size="small" @click="showAttrDlg(null)">新增属性</el-button>
            </div>
          </template>
          <el-table :data="attrs" stripe size="small" highlight-current-row @row-click="selectAttr" height="240">
            <el-table-column type="index" label="#" width="50" align="center" />
            <el-table-column prop="id" label="ID" width="140" show-overflow-tooltip />
            <el-table-column prop="sort" label="排序" width="80" align="center" />
            <el-table-column label="操作" width="120" align="center">
              <template #default="{row}">
                <el-button link size="small" type="primary" @click.stop="showAttrDlg(row)">编辑</el-button>
                <el-button link size="small" type="danger" @click.stop="delAttr(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination v-if="attrTotal > attrPageSize" style="margin-top:8px;justify-content:center" small layout="prev,next" :total="attrTotal" :page-size="attrPageSize" v-model:current-page="attrPg" @current-change="fetchAttrs" />
        </el-card>

        <el-card v-if="selectedAttr" shadow="never" class="card-panel" style="margin-top:12px">
          <template #header>
            <div class="card-hd">
              <span>属性值 — {{ selectedAttr.id }}</span>
              <el-button type="primary" size="small" @click="showValDlg(null)">新增属性值</el-button>
            </div>
          </template>
          <el-table :data="values" stripe size="small" height="200">
            <el-table-column type="index" label="#" width="50" align="center" />
            <el-table-column prop="name" label="名称" min-width="160" />
            <el-table-column prop="lang" label="语言" width="80" align="center" />
            <el-table-column label="操作" width="120" align="center">
              <template #default="{row}">
                <el-button link size="small" type="primary" @click="showValDlg(row)">编辑</el-button>
                <el-button link size="small" type="danger" @click="delVal(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination v-if="valTotal > valPageSize" style="margin-top:8px;justify-content:center" small layout="prev,next" :total="valTotal" :page-size="valPageSize" v-model:current-page="valPg" @current-change="fetchValues" />
        </el-card>

        <el-empty v-if="!selectedCat" description="请选择一个属性分类" :image-size="80" style="margin-top:60px" />
      </el-col>
    </el-row>

    <!-- 属性分类弹窗 -->
    <el-dialog v-model="catDlg.show" :title="catDlg.isEdit ? '编辑分类' : '新增分类'" width="420px">
      <el-form label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="catDlg.form.name" placeholder="分类名称" maxlength="50" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="catDlg.form.sort" :min="0" :max="9999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="catDlg.show = false">取消</el-button>
        <el-button type="primary" @click="saveCat">保存</el-button>
      </template>
    </el-dialog>

    <!-- 属性弹窗 -->
    <el-dialog v-model="attrDlg.show" :title="attrDlg.isEdit ? '编辑属性' : '新增属性'" width="420px">
      <el-form label-width="80px">
        <el-form-item label="排序">
          <el-input-number v-model="attrDlg.form.sort" :min="0" :max="9999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="attrDlg.show = false">取消</el-button>
        <el-button type="primary" @click="saveAttr">保存</el-button>
      </template>
    </el-dialog>

    <!-- 属性值弹窗 -->
    <el-dialog v-model="valDlg.show" :title="valDlg.isEdit ? '编辑属性值' : '新增属性值'" width="420px">
      <el-form label-width="60px">
        <el-form-item label="名称">
          <el-input v-model="valDlg.form.name" placeholder="属性值名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="语言">
          <el-select v-model="valDlg.form.lang" style="width:100%">
            <el-option label="English (en)" value="en" />
            <el-option label="中文 (cn)" value="cn" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="valDlg.show = false">取消</el-button>
        <el-button type="primary" @click="saveVal">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAttrCategoryList as apiGetAttrCategoryList,
  saveAttrCategory as apiSaveAttrCategory,
  updateAttrCategory as apiUpdateAttrCategory,
  deleteAttrCategory as apiDeleteAttrCategory,
  getAttrList as apiGetAttrList,
  saveAttr as apiSaveAttr,
  updateAttr as apiUpdateAttr,
  deleteAttr as apiDeleteAttr,
  getAttrValueList as apiGetAttrValueList,
  saveAttrValue as apiSaveAttrValue,
  updateAttrValue as apiUpdateAttrValue,
  deleteAttrValue as apiDeleteAttrValue
} from '@/api/mall'

const catKw = ref('')
const cats = ref([])
const catPg = ref(1)
const catTotal = ref(0)
const catPageSize = ref(20)
const selectedCat = ref(null)

const attrs = ref([])
const attrPg = ref(1)
const attrTotal = ref(0)
const attrPageSize = ref(20)
const selectedAttr = ref(null)

const values = ref([])
const valPg = ref(1)
const valTotal = ref(0)
const valPageSize = ref(20)

// Category dialog
const catDlg = reactive({
  show: false, isEdit: false,
  form: { id: '', name: '', sort: 0 }
})

function showCatDlg(row) {
  if (row) {
    catDlg.isEdit = true
    catDlg.form = { id: row.id, name: row.name, sort: row.sort || 0 }
  } else {
    catDlg.isEdit = false
    catDlg.form = { id: '', name: '', sort: 0 }
  }
  catDlg.show = true
}

async function saveCat() {
  try {
    if (catDlg.isEdit) {
      await apiUpdateAttrCategory(catDlg.form.id, { name: catDlg.form.name, sort: catDlg.form.sort })
    } else {
      await apiSaveAttrCategory({ name: catDlg.form.name, sort: catDlg.form.sort })
    }
    ElMessage.success('保存成功')
    catDlg.show = false
    fetchCats()
  } catch (e) { ElMessage.error(e.message || '保存失败') }
}

async function delCat(row) {
  try {
    await ElMessageBox.confirm(`确定删除分类「${row.name}」？`, '确认', { type: 'warning' })
    await apiDeleteAttrCategory(row.id)
    ElMessage.success('已删除')
    if (selectedCat.value?.id === row.id) { selectedCat.value = null; attrs.value = []; selectedAttr.value = null; values.value = [] }
    fetchCats()
  } catch { /* cancelled */ }
}

function selectCat(c) {
  selectedCat.value = c
  selectedAttr.value = null
  values.value = []
  attrPg.value = 1
  fetchAttrs()
}

// Attribute dialog
const attrDlg = reactive({
  show: false, isEdit: false,
  form: { id: '', sort: 0 }
})

function showAttrDlg(row) {
  if (row) {
    attrDlg.isEdit = true
    attrDlg.form = { id: row.id, sort: row.sort || 0 }
  } else {
    attrDlg.isEdit = false
    attrDlg.form = { id: '', sort: 0 }
  }
  attrDlg.show = true
}

async function saveAttr() {
  try {
    if (attrDlg.isEdit) {
      await apiUpdateAttr(attrDlg.form.id, { sort: attrDlg.form.sort, categoryId: selectedCat.value.id })
    } else {
      await apiSaveAttr({ sort: attrDlg.form.sort, categoryId: selectedCat.value.id })
    }
    ElMessage.success('保存成功')
    attrDlg.show = false
    fetchAttrs()
  } catch (e) { ElMessage.error(e.message || '保存失败') }
}

async function delAttr(row) {
  try {
    await ElMessageBox.confirm('确定删除该属性？', '确认', { type: 'warning' })
    await apiDeleteAttr(row.id)
    ElMessage.success('已删除')
    if (selectedAttr.value?.id === row.id) { selectedAttr.value = null; values.value = [] }
    fetchAttrs()
  } catch { /* cancelled */ }
}

function selectAttr(row) {
  selectedAttr.value = row
  valPg.value = 1
  fetchValues()
}

// Value dialog
const valDlg = reactive({
  show: false, isEdit: false,
  form: { id: '', name: '', lang: 'en' }
})

function showValDlg(row) {
  if (row) {
    valDlg.isEdit = true
    valDlg.form = { id: row.id, name: row.name, lang: row.lang || 'en' }
  } else {
    valDlg.isEdit = false
    valDlg.form = { id: '', name: '', lang: 'en' }
  }
  valDlg.show = true
}

async function saveVal() {
  try {
    if (valDlg.isEdit) {
      await apiUpdateAttrValue(valDlg.form.id, { name: valDlg.form.name, lang: valDlg.form.lang })
    } else {
      await apiSaveAttrValue({ attrId: selectedAttr.value.id, name: valDlg.form.name, lang: valDlg.form.lang })
    }
    ElMessage.success('保存成功')
    valDlg.show = false
    fetchValues()
  } catch (e) { ElMessage.error(e.message || '保存失败') }
}

async function delVal(row) {
  try {
    await ElMessageBox.confirm('确定删除该属性值？', '确认', { type: 'warning' })
    await apiDeleteAttrValue(row.id)
    ElMessage.success('已删除')
    fetchValues()
  } catch { /* cancelled */ }
}

// Fetch data
async function fetchCats() {
  try {
    const data = await apiGetAttrCategoryList({ keyword: catKw.value, page: catPg.value, size: catPageSize.value })
    cats.value = data.records || []
    catTotal.value = data.total || 0
  } catch { /* ignore */ }
}

async function fetchAttrs() {
  if (!selectedCat.value) return
  try {
    const data = await apiGetAttrList({ categoryId: selectedCat.value.id, page: attrPg.value, size: attrPageSize.value })
    attrs.value = data.records || []
    attrTotal.value = data.total || 0
  } catch { /* ignore */ }
}

async function fetchValues() {
  if (!selectedAttr.value) return
  try {
    const data = await apiGetAttrValueList({ attrId: selectedAttr.value.id, page: valPg.value, size: valPageSize.value })
    values.value = data.records || []
    valTotal.value = data.total || 0
  } catch { /* ignore */ }
}

onMounted(() => { fetchCats() })
</script>

<style scoped>
.attr-panel { padding: 4px; }
.card-panel { height: 100%; }
.card-hd { display: flex; justify-content: space-between; align-items: center; }
.cat-list { max-height: 380px; overflow-y: auto; }
.cat-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; cursor: pointer; border-radius: 4px; margin-bottom: 2px; }
.cat-item:hover { background: #f5f7fa; }
.cat-item.on { background: #ecf5ff; color: #409eff; font-weight: 600; }
.cat-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cat-acts { flex-shrink: 0; margin-left: 8px; }
</style>
