<template>
  <div class="merchant-products">
    <div class="top-bar"><h2>商品管理</h2><el-button type="primary" @click="showAdd = true">+ 添加商品</el-button></div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="name" label="商品名称" min-width="200"><template #default="{row}"><div style="display:flex;align-items:center;gap:10px"><img :src="row.mainImage" style="width:48px;height:48px;border-radius:6px;object-fit:cover" /><span>{{ row.name || row.goodsName }}</span></div></template></el-table-column>
      <el-table-column prop="price" label="价格" width="100"><template #default="{row}">¥{{ row.price || row.sellingPrice }}</template></el-table-column>
      <el-table-column prop="stock" label="库存" width="80"><template #default="{row}">{{ row.stock || row.inventory || 0 }}</template></el-table-column>
      <el-table-column prop="status" label="状态" width="90"><template #default="{row}"><el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? '上架' : '下架' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{row}">
          <el-button size="small" type="primary" @click="editProduct(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="delProduct(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination-wrap"><el-pagination background layout="prev, pager, next" :total="total" :page-size="20" @current-change="load" /></div>

    <!-- 添加/编辑弹窗 -->
    <el-dialog v-model="showAdd" :title="editing ? '编辑商品' : '添加商品'" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="商品名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="价格"><el-input-number v-model="form.price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="库存"><el-input-number v-model="form.stock" :min="0" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="form.status" :active-value="1" :inactive-value="0" active-text="上架" inactive-text="下架" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showAdd = false">取消</el-button><el-button type="primary" @click="saveProduct">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { get, post, put, del } from '@/api/index'

const list = ref([]); const loading = ref(false); const total = ref(0); const showAdd = ref(false); const editing = ref(false)
const form = reactive({ id: null, name: '', price: 0, stock: 0, description: '', status: 1 })

async function load(page = 1) {
  loading.value = true
  try { const r = await getMerchantProducts({ page, size: 20 }); list.value = (r.data || r).list || (r.data || r).rows || []; total.value = (r.data || r).total || 0 } catch {} finally { loading.value = false }
}
function editProduct(row) { Object.assign(form, row); form.id = row.id; editing.value = true; showAdd.value = true }
async function saveProduct() {
  try { if (editing.value) { await updateProduct(form) } else { await createProduct(form) }; ElMessage.success('保存成功'); showAdd.value = false; load() } catch { ElMessage.error('保存失败') }
}
async function delProduct(row) {
  try { await ElMessageBox.confirm('确定删除该商品？', '提示', { type: 'warning' }); await deleteProduct(row.id); ElMessage.success('已删除'); load() } catch {}
}
onMounted(() => load())
</script>

<style scoped>
.merchant-products { padding: 0; }
.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 20px; }
</style>
