<template>
  <div class="page-shell">
    <div class="page-header"><h2> AI</h2><p>+++</p></div>
    <el-tabs v-model="tab">
      <el-tab-pane label=" " name="desc">
        <el-card>
          <el-input v-model="descName" placeholder=''/>
          <el-input v-model="descCat" placeholder='' style="margin-top:8px"/>
          <el-input v-model="descFeatures" placeholder='' type="textarea" :rows="2" style="margin-top:8px"/>
          <el-button type="primary" style="margin-top:10px" @click="genDesc">OK</el-button>
          <div v-if="descResult" class="cf-output">{{ descResult }}</div>
        </el-card>
      </el-tab-pane>
      <el-tab-pane label=" " name="marketing">
        <el-card>
          <el-input v-model="campName" placeholder=''/>
          <el-input v-model="campDiscount" placeholder='' style="margin-top:8px"/>
          <el-button type="primary" style="margin-top:10px" @click="genMarketing">OK</el-button>
          <div v-if="mktResult" class="cf-output">{{ mktResult }}</div>
        </el-card>
      </el-tab-pane>
      <el-tab-pane label=" " name="translate">
        <el-card>
          <el-input v-model="transText" placeholder='' type="textarea" :rows="3"/>
          <el-select v-model="transLang" style="margin-top:8px;width:200px">
            <el-option value="en" label=''/><el-option value="ja" label=''/><el-option value="ko" label=''/>
          </el-select>
          <el-button type="primary" style="margin-top:8px" @click="genTranslate">OK</el-button>
          <div v-if="transResult" class="cf-output">{{ transResult }}</div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup>
import { ref } from "vue"; import { ElMessage } from "element-plus"; import { agentApi } from "@/api"
const tab = ref("desc")
const descName = ref(''); const descCat = ref(''); const descFeatures = ref(''); const descResult = ref('')
const campName = ref(''); const campDiscount = ref(''); const mktResult = ref('')
const transText = ref(''); const transLang = ref("en"); const transResult = ref('')
async function genDesc() { try { const r = await agentApi.post("/agent/content/description", { name: descName.value, category: descCat.value, features: descFeatures.value }); if (r?.data?.ok) descResult.value = r.data.text } catch (e) { ElMessage.error(e.message) } }
async function genMarketing() { try { const r = await agentApi.post("/agent/content/marketing", { name: campName.value, discount: campDiscount.value }); if (r?.data?.ok) mktResult.value = r.data.text } catch (e) { ElMessage.error(e.message) } }
async function genTranslate() { try { const r = await agentApi.post("/agent/content/translate", { text: transText.value, target_lang: transLang.value }); if (r?.data?.ok) transResult.value = r.data.text } catch (e) { ElMessage.error(e.message) } }
</script>
<style scoped>
.page-shell { max-width: 900px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 20px; color: #e0e0ff; margin: 0; }
.page-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.cf-output { margin-top: 12px; padding: 14px; background: rgba(102,126,234,0.08); border-radius: 10px; font-size: 14px; color: #e0e0e0; line-height: 1.6; white-space: pre-wrap; }
@media (max-width: 768px) { .page-shell { padding: 10px; } }
</style>
