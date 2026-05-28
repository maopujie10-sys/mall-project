<template>
  <div class="multilang"><div class="page-header"><h2>🌍 多语言商品发布</h2><p>一键翻译中/英/日/韩 → 多平台同步上架</p></div>
    <el-row :gutter="16">
      <el-col :span="16">
        <el-card><template #header>📝 商品信息 <el-tag size="small">中文源</el-tag></template>
          <el-form label-width="80">
            <el-form-item label="标题"><el-input v-model="form.title" placeholder="商品标题" /></el-form-item>
            <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="3" placeholder="商品描述" /></el-form-item>
            <el-form-item label="关键词"><el-input v-model="form.keywords" placeholder="用逗号分隔" /></el-form-item>
            <el-form-item label="规格"><el-input v-model="form.specs" placeholder="颜色:红,尺寸:L" /></el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card><template #header>🌐 目标语言</template>
          <el-checkbox-group v-model="targetLangs">
            <el-checkbox v-for="l in languages" :key="l.code" :label="l.code" border style="width:100%;margin-bottom:6px">{{ l.icon }} {{ l.name }}</el-checkbox>
          </el-checkbox-group>
        </el-card>
        <el-card style="margin-top:12px"><template #header>🏪 发布平台</template>
          <el-checkbox-group v-model="targetPlatforms">
            <el-checkbox v-for="p in platforms" :key="p.id" :label="p.id" border style="width:100%;margin-bottom:6px">{{ p.icon }} {{ p.name }}</el-checkbox>
          </el-checkbox-group>
        </el-card>
        <el-button type="primary" style="width:100%;margin-top:12px;height:44px;font-size:16px" @click="doPublish" :loading="publishing">🚀 一键翻译+发布</el-button>
      </el-col>
    </el-row>
    <el-card v-if="publishResult" style="margin-top:16px">
      <template #header>✅ 发布结果</template>
      <el-table :data="publishResult.results||[]" size="small" stripe>
        <el-table-column prop="platform" label="平台" width="100" />
        <el-table-column prop="language" label="语言" width="80" />
        <el-table-column prop="status" label="状态" width="80"><template #default="{row}"><el-tag :type="row.status==='published'?'success':'danger'">{{ row.status }}</el-tag></template></el-table-column>
        <el-table-column prop="url" label="链接" min-width="200" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"; import { publishProduct, getLanguages, getPlatforms } from "@/api/translate"
const form=ref({title:"2024新款时尚T恤",description:"高品质纯棉面料，舒适透气，多色可选",keywords:"T恤,时尚,纯棉",specs:"颜色:白/黑/灰,尺码:S/M/L/XL"})
const targetLangs=ref(["en","ja","ko"]); const targetPlatforms=ref(["shopify","etsy"])
const languages=ref([]); const platforms=ref([]); const publishing=ref(false); const publishResult=ref(null)
onMounted(async()=>{try{const r=await getLanguages();if(r.ok)languages.value=r.languages}catch{};try{const r=await getPlatforms();if(r.ok)platforms.value=r.platforms}catch{}})
async function doPublish(){if(!targetLangs.length||!targetPlatforms.length)return ElMessage.warning("请选择至少一个语言和平台");publishing.value=true;try{const r=await publishProduct(form.value,targetLangs.value,targetPlatforms.value);if(r.ok){publishResult.value=r;ElMessage.success(`已发布到${r.results.length}个站点`)}}catch(e){ElMessage.error(e.message)};publishing.value=false}
</script>
<style scoped>.multilang{padding:20px}.page-header{margin-bottom:20px}.page-header h2{margin:0 0 4px}.page-header p{margin:0;color:#999;font-size:13px}</style>
