<template>
  <div class="page-shell">
    <div class="page-header"><h2>AI Content Factory</h2><p>Rewrite + Generate + Translate — all in one place</p></div>
    <el-tabs v-model="tab">
      <el-tab-pane label="Rewrite" name="desc">
        <el-card>
          <el-input v-model="descName" placeholder="Product name" style="margin-bottom:8px"/>
          <el-input v-model="descCat" placeholder="Category (e.g. electronics, clothing)" style="margin-bottom:8px"/>
          <el-input v-model="descFeatures" placeholder="Key features, one per line" type="textarea" :rows="3" style="margin-bottom:10px"/>
          <el-button type="primary" @click="genDesc" :loading="descLoading">Generate Description</el-button>
          <div v-if="descResult" class="cf-output">{{ descResult }}</div>
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="Marketing" name="marketing">
        <el-card>
          <el-input v-model="campName" placeholder="Campaign name" style="margin-bottom:8px"/>
          <el-input v-model="campDiscount" placeholder="Discount offer (e.g. 50% off)" style="margin-bottom:10px"/>
          <el-button type="primary" @click="genMarketing" :loading="mktLoading">Generate Campaign</el-button>
          <div v-if="mktResult" class="cf-output">{{ mktResult }}</div>
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="Translate" name="translate">
        <el-card>
          <el-input v-model="transText" placeholder="Text to translate" type="textarea" :rows="4" style="margin-bottom:8px"/>
          <el-select v-model="transLang" style="width:200px;margin-bottom:8px" placeholder="Target language">
            <el-option value="en" label="English"/>
            <el-option value="ja" label="Japanese"/>
            <el-option value="ko" label="Korean"/>
            <el-option value="es" label="Spanish"/>
            <el-option value="fr" label="French"/>
            <el-option value="de" label="German"/>
            <el-option value="ar" label="Arabic"/>
          </el-select>
          <el-button type="primary" @click="genTranslate" :loading="transLoading" style="display:block">Translate</el-button>
          <div v-if="transResult" class="cf-output">{{ transResult }}</div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup>
import { ref } from "vue"; import { ElMessage } from "element-plus"; import { agentApi } from "@/api"
const tab = ref("desc")
const descName = ref(''); const descCat = ref(''); const descFeatures = ref(''); const descResult = ref(''); const descLoading = ref(false)
const campName = ref(''); const campDiscount = ref(''); const mktResult = ref(''); const mktLoading = ref(false)
const transText = ref(''); const transLang = ref("en"); const transResult = ref(''); const transLoading = ref(false)
async function genDesc() { descLoading.value = true; try { const r = await agentApi.post("/agent/content/description", { name: descName.value, category: descCat.value, features: descFeatures.value }); if (r?.data?.ok) descResult.value = r.data.text } catch (e) { ElMessage.error(e.message) } finally { descLoading.value = false } }
async function genMarketing() { mktLoading.value = true; try { const r = await agentApi.post("/agent/content/marketing", { name: campName.value, discount: campDiscount.value }); if (r?.data?.ok) mktResult.value = r.data.text } catch (e) { ElMessage.error(e.message) } finally { mktLoading.value = false } }
async function genTranslate() { transLoading.value = true; try { const r = await agentApi.post("/agent/content/translate", { text: transText.value, target_lang: transLang.value }); if (r?.data?.ok) transResult.value = r.data.text } catch (e) { ElMessage.error(e.message) } finally { transLoading.value = false } }
</script>
<style scoped>
.page-shell { max-width: 900px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 20px; color: #e0e0ff; margin: 0; }
.page-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.cf-output { margin-top: 12px; padding: 14px; background: rgba(102,126,234,0.08); border-radius: 10px; font-size: 14px; color: #e0e0e0; line-height: 1.6; white-space: pre-wrap; }
@media (max-width: 768px) { .page-shell { padding: 10px; } }
</style>