<template>
  <div class="batch-upload"><div class="page-header"><h2> Excel</h2><p>Excel/CSV  /  </p></div>
    <el-row :gutter="16">
      <el-col :span="10">
        <el-card><template #header> </template>
          <el-upload drag :auto-upload="false" :on-change="h=>{uploadFile=h.raw}" accept=".csv,.xlsx,.xls"><el-icon><UploadFilled /></el-icon><div>CSV/Excel</div><template #tip><div style="font-size:12px;color:#999">CSV</div></template></el-upload>
          
          
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card><template #header>  ({{ products.length }})</template>
          <el-table :data="products" size="small" stripe max-height="300">
            <el-table-column v-for="f in fields" :key="f" :prop="f" :label="f" min-width="100" show-overflow-tooltip />
          </el-table>
        </el-card>
        <div v-if="products.length" style="margin-top:12px;display:flex;gap:8px">
          <el-switch v-model="autoPricing" active-text="(1.3)" />
          <el-button type="success" @click="doPublish" :loading="publishing">  {{ products.length }} </el-button>
        </div>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref } from "vue"; import { parseExcel, batchPublish, getTemplate } from "@/api/excel"
const uploadFile=ref(null); const products=ref([]); const fields=ref([]); const parsing=ref(false); const publishing=ref(false); const autoPricing=ref(true)
async function doParse(){if(!uploadFile.value)return ElMessage.warning('Warning');parsing.value=true;try{const r=await parseExcel(uploadFile.value);if(r.ok){products.value=r.products||[];fields.value=r.fields||[];ElMessage.success(`${r.rows}`)}}catch(e){ElMessage.error(e.message)};parsing.value=false}
function useSample(){products.value=[{name:"A",price:"99.00",category:'',stock:"100"},{name:"B",price:"199.00",category:'',stock:"50"}];fields.value=["name","price","category","stock"]}
async function doPublish(){publishing.value=true;try{const r=await batchPublish(products.value,'',autoPricing.value);if(r.ok)ElMessage.success(` ${r.results.length}`)}catch(e){ElMessage.error(e.message)};publishing.value=false}
</script>
<style scoped>.batch-upload{padding:20px}.page-header{margin-bottom:20px}.page-header h2{margin:0 0 4px}.page-header p{margin:0;color:#999;font-size:13px}</style>
