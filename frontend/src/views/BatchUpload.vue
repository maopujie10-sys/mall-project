<template>
  <div class="batch-upload"><div class="page-header"><h2>📋 Excel批量上架</h2><p>从Excel/CSV导入 → 自动分类/定价 → 一键上架</p></div>
    <el-row :gutter="16">
      <el-col :span="10">
        <el-card><template #header>📤 上传文件</template>
          <el-upload drag :auto-upload="false" :on-change="h=>{uploadFile=h.raw}" accept=".csv,.xlsx,.xls"><el-icon><UploadFilled /></el-icon><div>拖拽或点击上传CSV/Excel</div><template #tip><div style="font-size:12px;color:#999">支持CSV格式，第一行为表头</div></template></el-upload>
          <el-button type="primary" style="width:100%;margin-top:12px" @click="doParse" :loading="parsing">🔍 解析文件</el-button>
          <el-button text size="small" style="margin-top:8px" @click="useSample">📋 使用示例数据</el-button>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card><template #header>📦 商品预览 ({{ products.length }}条)</template>
          <el-table :data="products" size="small" stripe max-height="300">
            <el-table-column v-for="f in fields" :key="f" :prop="f" :label="f" min-width="100" show-overflow-tooltip />
          </el-table>
        </el-card>
        <div v-if="products.length" style="margin-top:12px;display:flex;gap:8px">
          <el-switch v-model="autoPricing" active-text="自动定价(×1.3)" />
          <el-button type="success" @click="doPublish" :loading="publishing">🚀 一键上架 {{ products.length }} 个商品</el-button>
        </div>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref } from "vue"; import { ElMessage } from "element-plus"; import { parseExcel, batchPublish, getTemplate } from "@/api/excel"
const uploadFile=ref(null); const products=ref([]); const fields=ref([]); const parsing=ref(false); const publishing=ref(false); const autoPricing=ref(true)
async function doParse(){if(!uploadFile.value)return ElMessage.warning("请选择文件");parsing.value=true;try{const r=await parseExcel(uploadFile.value);if(r.ok){products.value=r.products||[];fields.value=r.fields||[];ElMessage.success(`解析到${r.rows}条商品`)}}catch(e){ElMessage.error(e.message)};parsing.value=false}
function useSample(){products.value=[{name:"示例商品A",price:"99.00",category:"数码",stock:"100"},{name:"示例商品B",price:"199.00",category:"服饰",stock:"50"}];fields.value=["name","price","category","stock"]}
async function doPublish(){publishing.value=true;try{const r=await batchPublish(products.value,"",autoPricing.value);if(r.ok)ElMessage.success(`✅ 已上架${r.results.length}个商品`)}catch(e){ElMessage.error(e.message)};publishing.value=false}
</script>
<style scoped>.batch-upload{padding:20px}.page-header{margin-bottom:20px}.page-header h2{margin:0 0 4px}.page-header p{margin:0;color:#999;font-size:13px}</style>
