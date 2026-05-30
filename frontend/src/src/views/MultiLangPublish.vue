<template>
  <div class="multilang"><div class="page-header">-<p>///  </p></div>
    <el-row :gutter="16">
      <el-col :span="16">
        <el-card><template #header>  -</template>
          <el-form label-width="80">
            <el-form-item label=''><el-input v-model="form.title" placeholder='' /></el-form-item>
            <el-form-item label=''><el-input v-model="form.description" type="textarea" :rows="3" placeholder='' /></el-form-item>
            <el-form-item label=''><el-input v-model="form.keywords" placeholder='' /></el-form-item>
            <el-form-item label=''><el-input v-model="form.specs" placeholder=":,:L" /></el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card><template #header> </template>
          <el-checkbox-group v-model="targetLangs">
            <el-checkbox v-for="l in languages" :key="l.code" :label="l.code" border style="width:100%;margin-bottom:6px">{{ l.icon }} {{ l.name }}</el-checkbox>
          </el-checkbox-group>
        </el-card>
        <el-card style="margin-top:12px"><template #header> </template>
          <el-checkbox-group v-model="targetPlatforms">
            <el-checkbox v-for="p in platforms" :key="p.id" :label="p.id" border style="width:100%;margin-bottom:6px">{{ p.icon }} {{ p.name }}</el-checkbox>
          </el-checkbox-group>
        </el-card>
        <el-button type="primary" style="width:100%;margin-top:12px;height:44px;font-size:16px" @click="doPublish" :loading="publishing"> +</el-button>
      </el-col>
    </el-row>
    <el-card v-if="publishResult" style="margin-top:16px">
      <template #header> </template>
      <el-table :data="publishResult.results||[]" size="small" stripe>
        <el-table-column prop="platform" label='' width="100" />
        <el-table-column prop="language" label='' width="80" />
        <el-table-column prop="status" label='' width="80"><template #default="{row}"><el-tag :type="row.status==='published'?'success':'danger''>{{ row.status }}</el-tag></template></el-table-column>
        <el-table-column prop="url" label='' min-width="200" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"; import { publishProduct, getLanguages, getPlatforms } from "@/api/translate"
const form=ref({title:"2024T",description:'',keywords:"T,",specs:"://,:S/M/L/XL"})
const targetLangs=ref(["en","ja","ko"]); const targetPlatforms=ref(["shopify","etsy"])
const languages=ref([]); const platforms=ref([]); const publishing=ref(false); const publishResult=ref(null)
onMounted(async()=>{try{const r=await getLanguages();if(r.ok)languages.value=r.languages}catch{};try{const r=await getPlatforms();if(r.ok)platforms.value=r.platforms}catch{}})
async function doPublish(){if(!targetLangs.length||!targetPlatforms.length)return ElMessage.warning('Warning');publishing.value=true;try{const r=await publishProduct(form.value,targetLangs.value,targetPlatforms.value);if(r.ok){publishResult.value=r;ElMessage.success(`${r.results.length}`)}}catch(e){ElMessage.error(e.message)};publishing.value=false}
</script>
<style scoped>.multilang{padding:20px}.page-header{margin-bottom:20px}.page-header h2{margin:0 0 4px}.page-header p{margin:0;color:#999;font-size:13px}</style>
