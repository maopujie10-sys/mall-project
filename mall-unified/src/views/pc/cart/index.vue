<template>
  <div class="pc-cart fade-in"><h2>购物车</h2>
    <div v-if="!items.length" class="empty-state"><p>🛒 购物车是空的</p><router-link to="/pc" class="btn btn-primary btn-sm">去逛逛</router-link></div>
    <el-table v-else :data="items" style="width:100%">
      <el-table-column type="selection" width="55" />
      <el-table-column label="商品"><template #default="{row}"><div style="display:flex;gap:12px;align-items:center"><img :src="row.image" style="width:60px;height:60px;border-radius:8px;object-fit:cover" /><span>{{ row.name }}</span></div></template></el-table-column>
      <el-table-column prop="price" label="单价" width="120"><template #default="{row}">¥{{ row.price }}</template></el-table-column>
      <el-table-column label="数量" width="150"><template #default="{row}"><el-input-number v-model="row.quantity" :min="1" size="small" /></template></el-table-column>
      <el-table-column label="小计" width="120"><template #default="{row}">¥{{ (row.price * row.quantity).toFixed(2) }}</template></el-table-column>
      <el-table-column label="操作" width="100"><template #default="{row}"><el-button type="danger" size="small" @click="removeItem(row)">删除</el-button></template></el-table-column>
    </el-table>
    <div v-if="items.length" style="display:flex;justify-content:flex-end;gap:12px;margin-top:24px"><span style="font-size:20px;font-weight:700">合计: ¥{{ total }}</span><button class="btn btn-primary btn-lg" @click="checkout">结算</button></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getCartList, removeCartItem } from '@/api/cart'

const router = useRouter()
const items = ref([])
const total = computed(() => items.value.reduce((s, i) => s + i.price * i.quantity, 0).toFixed(2))

async function removeItem(row) { try { await removeCartItem(row.cartId || row.id); items.value = items.value.filter(i => i !== row); ElMessage.success('已删除') } catch {} }
function checkout() { router.push('/pc/checkout') }

onMounted(async () => { try { const r = await getCartList(); items.value = ((r.data || r).list || []).map(i => ({ ...i, quantity: 1 })) } catch {} })
</script>

<style scoped>
.pc-cart { padding: 24px 0; }
h2 { margin-bottom: 24px; }
.empty-state { text-align: center; padding: 60px; }
</style>
