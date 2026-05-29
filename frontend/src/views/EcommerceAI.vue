<template><div class="page-shell"><div class="page-header"><h2>🏪 AI电商引擎</h2><p>选品 · 质检 · 文案 · 定价 · 库存</p></div>
<el-tabs v-model="tab" type="border-card"><el-tab-pane label="🔍 AI选品" name="select">
<el-input v-model="selectCat" placeholder="品类（如：女装/3C/家居）" style="margin-bottom:8px"/>
<el-select v-model="selectMarket" placeholder="市场"><el-option label="TikTok东南亚" value="TikTok东南亚"/><el-option label="TikTok欧美" value="TikTok欧美"/><el-option label="Shopee" value="Shopee"/><el-option label="Amazon" value="Amazon"/></el-select>
<el-button type="primary" style="margin-top:8px" @click="runSelect" :loading="loading">🚀 分析爆品</el-button>
<div v-if="selectResult" class="ai-result" v-html="md(selectResult)"></div></el-tab-pane>

<el-tab-pane label="✅ 客服质检" name="quality">
<el-input v-model="csText" placeholder="粘贴客服对话..." type="textarea" :rows="4"/>
<el-button type="primary" style="margin-top:8px" @click="runQuality" :loading="loading">📋 质检评分</el-button>
<div v-if="qualityResult" class="ai-result" v-html="md(qualityResult)"></div></el-tab-pane>

<el-tab-pane label="📝 营销文案" name="copy">
<el-input v-model="copyProduct" placeholder="产品名称"/>
<el-input v-model="copyFeatures" placeholder="产品特点/卖点" style="margin-top:8px" type="textarea" :rows="2"/>
<el-select v-model="copyPlatform" style="margin-top:8px"><el-option label="TikTok" value="TikTok"/><el-option label="Instagram" value="Instagram"/><el-option label="Facebook" value="Facebook"/></el-select>
<el-button type="primary" style="margin-top:8px" @click="runCopy" :loading="loading">✨ 生成文案</el-button>
<div v-if="copyResult" class="ai-result" v-html="md(copyResult)"></div></el-tab-pane>

<el-tab-pane label="💰 智能定价" name="pricing">
<el-input v-model="priceProduct" placeholder="产品名称"/>
<el-input-number v-model="priceCost" placeholder="成本(元)" :min="0" style="margin-top:8px;width:100%"/>
<el-input-number v-model="priceMargin" placeholder="目标利润率%" :min="0" :max="100" style="margin-top:8px;width:100%"/>
<el-input v-model="compPrices" placeholder="竞品价格(逗号分隔,如: 39,45,50)" style="margin-top:8px"/>
<el-button type="primary" style="margin-top:8px" @click="runPricing" :loading="loading">📊 定价分析</el-button>
<div v-if="pricingResult" class="ai-result" v-html="md(pricingResult)"></div></el-tab-pane>

<el-tab-pane label="📦 库存预测" name="inventory">
<el-input v-model="invProduct" placeholder="产品名称"/>
<el-input-number v-model="invStock" placeholder="当前库存" :min="0" style="margin-top:8px;width:100%"/>
<el-input-number v-model="invLead" placeholder="补货周期(天)" :min="1" style="margin-top:8px;width:100%"/>
<el-input v-model="invSales" placeholder="近30天销量(逗号分隔)" style="margin-top:8px"/>
<el-button type="primary" style="margin-top:8px" @click="runInventory" :loading="loading">🔮 预测补货</el-button>
<div v-if="invResult" class="ai-result" v-html="md(invResult)"></div></el-tab-pane></el-tabs></div></template>

<script setup>
import {ref} from "vue";import {ElMessage} from "element-plus";import {agentApi} from "@/api"
const tab=ref("select");const loading=ref(false)
const selectCat=ref("");const selectMarket=ref("TikTok东南亚");const selectResult=ref("")
const csText=ref("");const qualityResult=ref("")
const copyProduct=ref("");const copyFeatures=ref("");const copyPlatform=ref("TikTok");const copyResult=ref("")
const priceProduct=ref("");const priceCost=ref(0);const priceMargin=ref(30);const compPrices=ref("");const pricingResult=ref("")
const invProduct=ref("");const invStock=ref(0);const invLead=ref(7);const invSales=ref("");const invResult=ref("")

const api=async(url,body)=>{loading.value=true;try{const r=await agentApi.post(url,body);if(r?.data?.ok){loading.value=false;return r.data.result||"完成"}else{loading.value=false;return r?.data?.error||"失败"}}catch(e){loading.value=false;return e.message}}

async function runSelect(){selectResult.value=await api("/agent/ecommerce/product-select",{category:selectCat.value,market:selectMarket.value})}
async function runQuality(){const lines=csText.value.split("\n").filter(l=>l.trim());const msgs=lines.map(l=>{const p=l.indexOf(":");return p>0?{role:l.slice(0,p),content:l.slice(p+1)}:{role:"unknown",content:l}});qualityResult.value=await api("/agent/ecommerce/cs-quality",{conversations:msgs})}
async function runCopy(){copyResult.value=await api("/agent/ecommerce/marketing-copy",{product_name:copyProduct.value,features:copyFeatures.value,platform:copyPlatform.value})}
async function runPricing(){const comps=compPrices.value.split(",").filter(n=>n.trim()).map(n=>({name:"竞品",price:parseFloat(n)}));pricingResult.value=await api("/agent/ecommerce/pricing",{product_name:priceProduct.value,cost:priceCost.value,target_margin:priceMargin.value,competitor_prices:comps})}
async function runInventory(){const sales=invSales.value.split(",").filter(n=>n.trim()).map((n,i)=>({date:`Day${i+1}`,quantity:parseInt(n)}));invResult.value=await api("/agent/ecommerce/inventory-forecast",{product_name:invProduct.value,current_stock:invStock.value,lead_time_days:invLead.value,sales_history:sales})}
function md(t){return t.replace(/\n/g,"<br>").replace(/\*\*(.*?)\*\*/g,"<b>$1</b>")}
</script>
<style scoped>.page-shell{max-width:900px;margin:0 auto;padding:20px}.page-header{margin-bottom:16px}.page-header h2{font-size:20px;color:#e0e0ff;margin:0}.page-header p{font-size:12px;color:rgba(255,255,255,.5);margin:4px 0}.ai-result{margin-top:12px;padding:16px;background:rgba(15,15,35,.8);border:1px solid rgba(102,126,234,.2);border-radius:12px;font-size:13px;color:#e0e0e0;line-height:1.8;white-space:pre-wrap;max-height:500px;overflow-y:auto}@media(max-width:768px){.page-shell{padding:10px}}</style>