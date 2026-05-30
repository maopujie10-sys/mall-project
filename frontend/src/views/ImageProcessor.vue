<template>
  <div class="img-processor"><div class="page-header"><h2> AI</h2>-</div>
    <el-tabs v-model="tab">
      <el-tab-pane label=" " name="bg">
        <el-upload drag :auto-upload="false" :on-change="h=>{imgFile=h.raw}" accept="image/*"><el-icon><Plus /></el-icon><div>{{ \('ecommerce.title') }}</div></el-upload>
        <div style="margin-top:12px;display:flex;gap:8px"><el-input v-model="imgUrl" placeholder="URL" /></div>
        <div v-if="bgResult" style="margin-top:12px"><el-alert :title="bgResult.note||''" type="success" :closable="false" /></div>
      </el-tab-pane>
      <el-tab-pane label=" " name="wm">
        <el-input v-model="wmUrl" placeholder="URL" style="margin-bottom:8px" />
        <div style="display:flex;gap:8px;margin-bottom:8px"><el-input v-model="wmText" placeholder='Enter...' style="width:200px"/><el-select v-model="wmPos"><el-option v-for="p in ['top-left','top-right','bottom-left','bottom-right','center']" :key="p" :label="p" :value="p"/></el-select></div>
        
      </el-tab-pane>
      <el-tab-pane label=" " name="batch">
        <el-input v-model="batchUrls" type="textarea" :rows="4" placeholder="URL" style="margin-bottom:8px" />
        <el-select v-model="batchOp" style="margin-bottom:8px;width:100%"><el-option v-for="o in [['remove_bg',''],['watermark',''],['resize',''],['enhance','']]" :key="o[0]" :label="o[1]" :value="o[0]" /></el-select>
        
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup>
import { ref } from "vue"; import { removeBg, addWatermark, batchProcess } from "@/api/image"
const tab=ref("bg"); const imgUrl=ref(''); const imgFile=ref(null); const bgResult=ref(null)
const wmUrl=ref(''); const wmText=ref("Friday AI"); const wmPos=ref("bottom-right")
const batchUrls=ref(''); const batchOp=ref("remove_bg")
async function doRemoveBg(){try{const r=await removeBg(imgUrl.value,imgFile.value);if(r.ok)bgResult.value=r;ElMessage.success(r.note||'')}catch(e){ElMessage.error(e.message)}}
async function doWatermark(){try{const r=await addWatermark(wmUrl.value,wmText.value,wmPos.value);if(r.ok)ElMessage.success(r.note)}catch(e){ElMessage.error(e.message)}}
async function doBatch(){const urls=batchUrls.value.split("\n").filter(Boolean);if(!urls.length)return ElMessage.warning("URL");try{const r=await batchProcess(urls,batchOp.value);if(r.ok)ElMessage.success(` ${r.results.length} `)}catch(e){ElMessage.error(e.message)}}
</script>
<style scoped>.img-processor{padding:20px}.page-header{margin-bottom:20px}.page-header h2{margin:0 0 4px}.page-header p{margin:0;color:#999;font-size:13px}</style>
