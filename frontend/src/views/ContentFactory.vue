<template>
  <div class="page-shell">
    <div class="page-header"><h2>🏭 AI内容工厂</h2><p>商品描述+营销文案+社媒帖子+翻译</p></div>
    <el-tabs v-model="tab">
      <el-tab-pane label="📝 商品描述" name="desc">
        <el-card>
          <el-input v-model="descName" placeholder="商品名称"/>
          <el-input v-model="descCat" placeholder="品类" style="margin-top:8px"/>
          <el-input v-model="descFeatures" placeholder="特点" type="textarea" :rows="2" style="margin-top:8px"/>
          <el-button type="primary" style="margin-top:10px" @click="genDesc">生成描述</el-button>
          <div v-if="descResult" class="cf-output">{{ descResult }}</div>
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="📢 营销文案" name="marketing">
        <el-card>
          <el-input v-model="campName" placeholder="活动名称"/>
          <el-input v-model="campDiscount" placeholder="优惠内容" style="margin-top:8px"/>
          <el-button type="primary" style="margin-top:10px" @click="genMarketing">生成文案</el-button>
          <div v-if="mktResult" class="cf-output">{{ mktResult }}</div>
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="🌐 翻译" name="translate">
        <el-card>
          <el-input v-model="transText" placeholder="要翻译的内容" type="textarea" :rows="3"/>
          <el-select v-model="transLang" style="margin-top:8px;width:200px">
            <el-option value="en" label="英语"/><el-option value="ja" label="日语"/><el-option value="ko" label="韩语"/>
          </el-select>
          <el-button type="primary" style="margin-top:8px" @click="genTranslate">翻译</el-button>
          <div v-if="transResult" class="cf-output">{{ transResult }}</div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup>
import { ref } from "vue"; import { ElMessage } from "element-plus"; import { agentApi } from "@/api"
const tab = ref("desc")
const descName = ref(""); const descCat = ref(""); const descFeatures = ref(""); const descResult = ref("")
const campName = ref(""); const campDiscount = ref(""); const mktResult = ref("")
const transText = ref(""); const transLang = ref("en"); const transResult = ref("")
async function genDesc() { try { const r = await agentApi.post("/agent/content/description", { name: descName.value, category: descCat.value, features: descFeatures.value }); if (r?.ok) descResult.value = r.text } catch (e) { ElMessage.error(e.message) } }
async function genMarketing() { try { const r = await agentApi.post("/agent/content/marketing", { name: campName.value, discount: campDiscount.value }); if (r?.ok) mktResult.value = r.text } catch (e) { ElMessage.error(e.message) } }
async function genTranslate() { try { const r = await agentApi.post("/agent/content/translate", { text: transText.value, target_lang: transLang.value }); if (r?.ok) transResult.value = r.text } catch (e) { ElMessage.error(e.message) } }
</script>
<style scoped>
.page-shell { max-width: 900px; margin: 0 auto; padding: 20px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 20px; color: #e0e0ff; margin: 0; }
.page-header p { font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px 0; }
.cf-output { margin-top: 12px; padding: 14px; background: rgba(102,126,234,0.08); border-radius: 10px; font-size: 14px; color: #e0e0e0; line-height: 1.6; white-space: pre-wrap; }
@media (max-width: 768px) { .page-shell { padding: 10px; } }
</style>
