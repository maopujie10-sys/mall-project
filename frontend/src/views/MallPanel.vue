<template>
  <div class="mall-panel">
    <el-tabs v-model="activeTab" type="border-card" class="mall-tabs">
      <!-- ========== ?========== -->
      <el-tab-pane name="dashboard">
        <template #label><el-icon><DataAnalysis /></el-icon> ?/template>

        <el-row :gutter="16" class="kpi-row">
          <el-col :xs="12" :sm="6" v-for="k in kpis" :key="k.label">
            <div class="kpi-card" :class="k.color">
              <div class="kpi-num">{{ fmt(k.value) }}</div>
              <div class="kpi-label">{{ k.label }}</div>
            </div>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="16">
            <el-card shadow="never">
              <div class="card-hd">
                <span class="card-tt">?/span>
                <span class="chart-tabs">
                  <span v-for="(t,i) in ['','??,'?0?]" :key="i"
                    class="ctab" :class="{on:chartR===i}" @click="switchChart(i)">{{t}}</span>
                </span>
              </div>
              <div ref="chartRef" class="chart-box">{{ ('mall.title') }}</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="never" class="order-card">
              -
              <div class="order-grid">
                <div class="oi" v-for="o in orderStats" :key="o.l">
                  <div class="oi-num">{{ fmt(o.v) }}</div>
                  <div class="oi-lbl">{{ o.l }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-card shadow="never" style="margin-top:16px">
          <div class="card-tt"> Top10</div>
          <el-table :data="topGoods" stripe size="small" height="380">
            <el-table-column type="index" label="#" width="50" align="center" />
            <el-table-column prop="name" :label="\('mall.title')" min-width="200" />
            <el-table-column label='Status' width="120" align="center">
              <template #default="{row}">{{ fmt(row.prizes||row.price) }}</template>
            </el-table-column>
            <el-table-column label="? width="100" align="center">
              <template #default="{row}">{{ fmt(row.sellCount) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- ==========  ========== -->
      <el-tab-pane name="users">
        <template #label><el-icon><User /></el-icon> </template>
        <div class="tb-bar">
          <el-input v-model="userKw" :placeholder="\('mall.search')" style="width:220px" clearable @clear="fetchUsers" @keyup.enter="fetchUsers" />
          <el-button type="primary" @click="fetchUsers">OK</el-button>
        </div>
        <el-table :data="users" stripe size="small" height="520">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="username" label="? width="120" />
          <el-table-column prop="phone" label="? width="130" />
          <el-table-column prop="balance" :label="\('mall.title')" width="110" />
          <el-table-column prop="status" label="? width="90">
            <template #default="{row}"><el-tag :type="row.status===1?'success':'danger' size="small">{{ row.status===1?'':'' }}</el-tag></template>
          </el-table-column>
          <el-table-column label='Status' width="200">
            <template #default="{row}">
              <el-button size="small" @click="toggleUser(row)">{{ row.status===1?'':'' }}</el-button>
              <el-button size="small" type="warning" @click="showBalDlg(row)">?/el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="userTotal" :page-size="10" v-model:current-page="userPg" @current-change="fetchUsers" small />
      </el-tab-pane>

      <!-- ==========  ========== -->
      <el-tab-pane name="merchants">
        <template #label><el-icon><Shop /></el-icon> </template>
        <div class="tb-bar">
          <el-input v-model="merKw" :placeholder="\('mall.search')" style="width:220px" clearable @clear="fetchMerchants" @keyup.enter="fetchMerchants" />
          <el-button type="primary" @click="fetchMerchants">OK</el-button>
          <el-button @click="fetchMerApplies"></el-button>
        </div>
        <el-table :data="merchants" stripe size="small" height="520">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="name" :label="\('mall.title')" min-width="150" />
          <el-table-column prop="phone" label="? width="130" />
          <el-table-column prop="status" label="? width="90">
            <template #default="{row}"><el-tag :type="row.status===1?'success':'danger' size="small">{{ row.status===1?'':'' }}</el-tag></template>
          </el-table-column>
          <el-table-column label='Status' width="120">
            <template #default="{row}">
              <el-button size="small" @click="toggleMer(row)">{{ row.status===1?'':'' }}</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="merTotal" :page-size="10" v-model:current-page="merPg" @current-change="fetchMerchants" small />
      </el-tab-pane>

      <!-- ==========  ========== -->
      <el-tab-pane name="products">
        <template #label><el-icon><Goods /></el-icon> </template>
        <div class="tb-bar">
          <el-input v-model="prodKw" placeholder='Enter...' style="width:220px" clearable @clear="fetchProducts" @keyup.enter="fetchProducts" />
          <el-button type="primary" @click="fetchProducts">OK</el-button>
        </div>
        <el-table :data="products" stripe size="small" height="520">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="name" :label="\('mall.title')" min-width="180" />
          <el-table-column prop="price" label='Status' width="100" />
          <el-table-column prop="status" label="? width="90">
            <template #default="{row}"><el-tag :type="row.status===1?'success':row.status===0?'warning':'info' size="small">{{ statTxt(row.status) }}</el-tag></template>
          </el-table-column>
          <el-table-column label='Status' width="160">
            <template #default="{row}">
              <el-button v-if="row.status===0" size="small" type="success" @click="auditProd(row,1)">OK</el-button>
              <el-button v-if="row.status===1" size="small" type="danger" @click="auditProd(row,0)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="prodTotal" :page-size="10" v-model:current-page="prodPg" @current-change="fetchProducts" small />
      </el-tab-pane>

      <!-- ==========  ========== -->
      <el-tab-pane name="orders">
        <template #label><el-icon><Document /></el-icon> </template>
        <div class="tb-bar">
          <el-input v-model="orderKw" :placeholder="\('mall.search')" style="width:220px" clearable @clear="fetchOrders" @keyup.enter="fetchOrders" />
          <el-button type="primary" @click="fetchOrders">OK</el-button>
        </div>
        <el-table :data="orders" stripe size="small" height="520">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="orderNo" label="? width="180" />
          <el-table-column prop="amount" :label="\('mall.title')" width="100" />
          <el-table-column prop="status" label="? width="90">
            <template #default="{row}"><el-tag size="small">{{ row.status }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="createTime" label='Status' width="160" />
          <el-table-column label='Status' width="100">
            <template #default="{row}">
              <el-button size="small" type="danger" @click="doRefund(row)">?/el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="orderTotal" :page-size="10" v-model:current-page="orderPg" @current-change="fetchOrders" small />
      </el-tab-pane>

      <!-- ========== ?========== -->
      <el-tab-pane name="recharges">
        <template #label><el-icon><Wallet /></el-icon> ?<el-badge :value="recPending" :hidden="!recPending" /></template>
        <el-table :data="recharges" stripe size="small" height="560">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="orderNo" label="? width="180" />
          <el-table-column prop="amount" :label="\('mall.title')" width="100" />
          <el-table-column prop="userId" label="ID" width="80" />
          <el-table-column prop="createTime" label='Status' width="160" />
          <el-table-column label='Status' width="160">
            <template #default="{row}">
              <el-button size="small" type="success" @click="auditRec(row,true)">OK</el-button>
              <el-button size="small" type="danger" @click="auditRec(row,false)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- ==========  ========== -->
      <el-tab-pane name="withdraws">
        <template #label><el-icon><Money /></el-icon>  <el-badge :value="witPending" :hidden="!witPending" /></template>
        <el-table :data="withdraws" stripe size="small" height="560">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="orderNo" label="? width="180" />
          <el-table-column prop="amount" :label="\('mall.title')" width="100" />
          <el-table-column prop="userId" label="ID" width="80" />
          <el-table-column prop="createTime" label='Status' width="160" />
          <el-table-column label='Status' width="220">
            <template #default="{row}">
              <el-button size="small" type="success" @click="auditWit(row,true)">OK</el-button>
              <el-button size="small" type="danger" @click="auditWit(row,false)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- ==========  ========== -->
      <el-tab-pane name="banners">
        <template #label><el-icon><Picture /></el-icon> </template>
        <div class="tb-bar">
          <el-select v-model="bannerType" placeholder='Enter...' style="width:120px" clearable @change="fetchBanners">
            <el-option :label="\('mall.title')" value="home" /><el-option label='Status' value="activity" />
          </el-select>
          <el-button type="primary" @click="fetchBanners">OK</el-button>
          <el-button type="success" @click="showBannerDlg()"></el-button>
        </div>
        <el-table :data="banners" stripe size="small" height="480">
          <el-table-column prop="uuid" label="UUID" width="120" />
          <el-table-column prop="title" :label="\('mall.title')" min-width="150" />
          <el-table-column prop="type" label='Status' width="100" />
          <el-table-column prop="sort" label='Status' width="70" />
          <el-table-column prop="imgUrl" label="URL" min-width="200" />
          <el-table-column label='Status' width="160">
            <template #default="{row}">
              <el-button size="small" @click="showBannerDlg(row)">OK</el-button>
              <el-button size="small" type="danger" @click="delBanner(row)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="bannerTotal" :page-size="20" v-model:current-page="bannerPg" @current-change="fetchBanners" small />
      </el-tab-pane>

      <!-- ==========  ========== -->
      <el-tab-pane name="categories">
        <template #label><el-icon><Grid /></el-icon> </template>
        <div class="tb-bar">
          <el-select v-model="catLevel" placeholder='Enter...' style="width:100px" clearable @change="fetchCategories">
            <el-option label="? :value="1" /><el-option label='Status' :value="2" />
          </el-select>
          <el-button type="primary" @click="fetchCategories">OK</el-button>
          <el-button type="success" @click="showCatDlg()"></el-button>
        </div>
        <el-table :data="categories" stripe size="small" height="480">
          <el-table-column prop="uuid" label="UUID" width="120" />
          <el-table-column prop="name" :label="\('mall.title')" min-width="150" />
          <el-table-column prop="sort" label='Status' width="70" />
          <el-table-column prop="level" label='Status' width="70" />
          <el-table-column prop="status" label="? width="80">
            <template #default="{row}"><el-tag :type="row.status===1?'success':'danger' size="small">{{ row.status===1?'':'' }}</el-tag></template>
          </el-table-column>
          <el-table-column label='Status' width="220">
            <template #default="{row}">
              <el-button size="small" @click="showCatDlg(row)">OK</el-button>
              <el-button size="small" :type="row.status===1?'warning':'success'' @click="toggleCatStatus(row)">{{ row.status===1?'':'' }}</el-button>
              <el-button size="small" type="danger" @click="delCat(row)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="catTotal" :page-size="20" v-model:current-page="catPg" @current-change="fetchCategories" small />
      </el-tab-pane>

      <!-- ==========  ========== -->
      <el-tab-pane name="evaluations">
        <template #label><el-icon><Star /></el-icon> </template>
        <div class="tb-bar">
          <el-input v-model="evalKw" placeholder='Enter...' style="width:220px" clearable @clear="fetchEvaluations" @keyup.enter="fetchEvaluations" />
          <el-select v-model="evalStatus" placeholder="? style="width:100px" clearable @change="fetchEvaluations">
            <el-option :label="\('mall.title')" :value="1" /><el-option label='Status' :value="0" />
          </el-select>
          <el-button type="primary" @click="fetchEvaluations">OK</el-button>
        </div>
        <el-table :data="evaluations" stripe size="small" height="480">
          <el-table-column prop="uuid" label="UUID" width="100" />
          <el-table-column prop="userName" :label="\('mall.title')" width="100" />
          <el-table-column prop="content" :label="\('mall.title')" min-width="200" show-overflow-tooltip />
          <el-table-column prop="rating" label='Status' width="70">
            <template #default="{row}">{{ '?.repeat(row.rating||0) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="? width="80">
            <template #default="{row}"><el-tag :type="row.status===1?'success':'info' size="small">{{ row.status===1?'':'' }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="createTime" label='Status' width="160" />
          <el-table-column label='Status' width="160">
            <template #default="{row}">
              <el-button size="small" :type="row.status===1?'warning':'success'' @click="toggleEval(row)">{{ row.status===1?'':'' }}</el-button>
              <el-button size="small" type="danger" @click="delEval(row)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="evalTotal" :page-size="20" v-model:current-page="evalPg" @current-change="fetchEvaluations" small />
      </el-tab-pane>

      <!-- ========== ?========== -->
      <el-tab-pane name="attrCats">
        <template #label><el-icon><Collection /></el-icon> ?/template>
        <div class="tb-bar">
          <el-input v-model="attrCatKw" placeholder='Enter...' style="width:220px" clearable @clear="fetchAttrCats" @keyup.enter="fetchAttrCats" />
          <el-button type="primary" @click="fetchAttrCats">OK</el-button>
          <el-button type="success" @click="showAttrCatDlg()"></el-button>
        </div>
        <el-table :data="attrCats" stripe size="small" height="480">
          <el-table-column prop="id" label="ID" width="200" />
          <el-table-column prop="name" :label="\('mall.title')" min-width="150" />
          <el-table-column prop="sort" label='Status' width="80" />
          <el-table-column label='Status' width="160">
            <template #default="{row}">
              <el-button size="small" @click="showAttrCatDlg(row)">OK</el-button>
              <el-button size="small" type="danger" @click="delAttrCat(row)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="attrCatTotal" :page-size="20" v-model:current-page="attrCatPg" @current-change="fetchAttrCats" small />
      </el-tab-pane>

      <!-- ========== ?========== -->
      <el-tab-pane name="attrs">
        <template #label><el-icon><SetUp /></el-icon> ?/template>
        <div class="tb-bar">
          <el-input v-model="attrCatFilter" placeholder="D" style="width:220px" clearable @clear="fetchAttrs" @keyup.enter="fetchAttrs" />
          <el-button type="primary" @click="fetchAttrs">OK</el-button>
          <el-button type="success" @click="showAttrDlg()">?/el-button>
        </div>
        <el-table :data="attrs" stripe size="small" height="480">
          <el-table-column prop="id" label="ID" width="200" />
          <el-table-column prop="categoryId" label="ID" width="200" />
          <el-table-column prop="sort" label='Status' width="80" />
          <el-table-column label='Status' width="160">
            <template #default="{row}">
              <el-button size="small" @click="showAttrDlg(row)">OK</el-button>
              <el-button size="small" type="danger" @click="delAttr(row)">OK</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="attrTotal" :page-size="20" v-model:current-page="attrPg" @current-change="fetchAttrs" small />
      </el-tab-pane>
    </el-tabs>

    <!-- ?-->
    <el-dialog v-model="balDlg.show" :title="\('mall.title')" width="400px">
      <el-form label-width="80px">
        <el-form-item :label="\('mall.title')">{{ balDlg.user }}</el-form-item>
        <el-form-item :label="\('mall.title')"><el-input v-model="balDlg.amount" placeholder="," /></el-form-item>
        <el-form-item label=''><el-input v-model="balDlg.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="balDlg.show=false">OK</el-button><el-button type="primary" @click="doAdjust"></el-button></template>
    </el-dialog>

    
    <el-dialog v-model="applyDlg.show" :title="\('mall.title')" width="500px">
      <el-table :data="applies" stripe size="small" height="400">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="? width="120" />
        <el-table-column prop="phone" label="? width="130" />
        <el-table-column label='Status' width="140">
          <template #default="{row}">
            <el-button size="small" type="success" @click="auditApply(row,true)">OK</el-button>
            <el-button size="small" type="danger" @click="auditApply(row,false)">OK</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    
    <el-dialog v-model="bannerDlg.show" :title="bannerDlg.uuid?'':''' width="500px">
      <el-form label-width="80px">
        <el-form-item :label="\('mall.title')"><el-input v-model="bannerDlg.title" /></el-form-item>
        <el-form-item label=''><el-select v-model="bannerDlg.type" style="width:100%"><el-option :label="\('mall.title')" value="home" /><el-option label='Status' value="activity" /></el-select></el-form-item>
        <el-form-item label="URL"><el-input v-model="bannerDlg.imgUrl" placeholder="https://..." /></el-form-item>
        <el-form-item label="URL"><el-input v-model="bannerDlg.linkUrl" /></el-form-item>
        <el-form-item label=''><el-input-number v-model="bannerDlg.sort" :min="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="bannerDlg.show=false">OK</el-button><el-button type="primary" @click="saveBannerDlg">OK</el-button></template>
    </el-dialog>

    
    <el-dialog v-model="catDlg.show" :title="catDlg.uuid?'':''' width="500px">
      <el-form label-width="80px">
        <el-form-item :label="\('mall.title')"><el-input v-model="catDlg.name" /></el-form-item>
        <el-form-item label=''><el-input-number v-model="catDlg.level" :min="1" :max="3" /></el-form-item>
        <el-form-item label="ID"><el-input v-model="catDlg.parentId" placeholder="0" /></el-form-item>
        <el-form-item label=''><el-input-number v-model="catDlg.type" :min="1" /></el-form-item>
        <el-form-item label=''><el-input-number v-model="catDlg.sort" :min="0" /></el-form-item>
        <el-form-item label=""><el-switch v-model="catDlg.status" :active-value="1" :inactive-value="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="catDlg.show=false">OK</el-button><el-button type="primary" @click="saveCatDlg">OK</el-button></template>
    </el-dialog>

    <!-- ?-->
    <el-dialog v-model="attrCatDlg.show" :title="attrCatDlg.uuid?'?:'?" width="400px">
      <el-form label-width="80px">
        <el-form-item :label="\('mall.title')"><el-input v-model="attrCatDlg.name" /></el-form-item>
        <el-form-item label=''><el-input-number v-model="attrCatDlg.sort" :min="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="attrCatDlg.show=false">OK</el-button><el-button type="primary" @click="saveAttrCatDlg">OK</el-button></template>
    </el-dialog>

    <!-- ?-->
    <el-dialog v-model="attrDlg.show" :title="attrDlg.uuid?'?:'?" width="400px">
      <el-form label-width="100px">
        <el-form-item label="D"><el-input v-model="attrDlg.categoryId" /></el-form-item>
        <el-form-item label=''><el-input-number v-model="attrDlg.sort" :min="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="attrDlg.show=false">OK</el-button><el-button type="primary" @click="saveAttrDlg">OK</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  getDashboard, getUserList, updateUserStatus, adjustUserBalance,
  getProductList, auditProduct, getOrderList, forceRefund,
  getRechargePending, auditRecharge, getWithdrawPending, auditWithdraw,
  getMerchantList, updateMerchantStatus, getMerchantApplyList, auditMerchantApply,
  getDashboardHead, getDashboardLine, getDashboardGoods,
  getBannerList, saveBanner, updateBanner, deleteBanner,
  getCategoryList, saveCategory, updateCategory, updateCategoryStatus, deleteCategory,
  getEvaluationList, updateEvaluationStatus, deleteEvaluation,
  getAttrCategoryList, saveAttrCategory, updateAttrCategory, deleteAttrCategory,
  getAttrList, saveAttr, updateAttr, deleteAttr,
} from '@/api/mall'

const activeTab = ref('dashboard')
const chartRef = ref(null)
const chartR = ref(0)
let chart = null, timer = null

// ===== ?=====
const kpis = reactive([
  { label:'?, value:0, color:'c1', key:'total_users' },
  { label:'', value:0, color:'c2', key:'today_orders' },
  { label:'?, value:0, color:'c3', key:'today_amount' },
  { label:'?, value:0, color:'c4', key:'pending_recharge' },
])
const orderStats = reactive([
  { l:'?, v:0 },{ l:'?, v:0 },{ l:'?, v:0 },{ l:'?, v:0 },
])
const topGoods = ref([])
const chartData = reactive({ comm:[], s:[] })

// ===== ?=====
const users = ref([]), userKw = ref(''), userPg = ref(1), userTotal = ref(0)
const merchants = ref([]), merKw = ref(''), merPg = ref(1), merTotal = ref(0)
const products = ref([]), prodKw = ref(''), prodPg = ref(1), prodTotal = ref(0)
const orders = ref([]), orderKw = ref(''), orderPg = ref(1), orderTotal = ref(0)
const recharges = ref([]), recPending = ref(0)
const withdraws = ref([]), witPending = ref(0)
const applies = ref([])
const balDlg = reactive({ show:false, user:'', userId:null, amount:'', remark:'' })
const applyDlg = reactive({ show:false })

// =====  =====
const banners = ref([]), bannerType = ref(''), bannerPg = ref(1), bannerTotal = ref(0)
const bannerDlg = reactive({ show:false, uuid:'', title:'', type:'home', imgUrl:'', sort:0, linkUrl:'' })

// =====  =====
const categories = ref([]), catLevel = ref(null), catPg = ref(1), catTotal = ref(0)
const catDlg = reactive({ show:false, uuid:'', name:'', sort:0, level:1, parentId:'0', type:1, iconImg:'', status:1 })

// =====  =====
const evaluations = ref([]), evalKw = ref(''), evalStatus = ref(null), evalPg = ref(1), evalTotal = ref(0)

// ===== ?+ ?=====
const attrCats = ref([]), attrCatKw = ref(''), attrCatPg = ref(1), attrCatTotal = ref(0)
const attrCatDlg = reactive({ show:false, uuid:'', name:'', sort:0 })
const attrs = ref([]), attrCatFilter = ref(''), attrPg = ref(1), attrTotal = ref(0)
const attrDlg = reactive({ show:false, uuid:'', categoryId:'', sort:0 })

// =====  =====
function fmt(v) {
  if (v == null) return '0'
  const n = Number(v)
  return Number.isNaN(n) ? String(v) : n.toLocaleString('en-US',{maximumFractionDigits:2})
}
function statTxt(s) { return s===1?'':s===0?'':'' }

// ===== ?=====
async function loadDashboard() {
  try {
    const d = await getDashboard()
    if (d) {
      kpis[0].value = d.total_users ?? d.totalUsers ?? 0
      kpis[1].value = d.today_orders ?? d.todayOrders ?? 0
      kpis[2].value = d.today_amount ?? d.todayAmount ?? 0
      kpis[3].value = (d.pending_recharge||0) + (d.pending_withdraw||0) + (d.pending_merchant||0)
      orderStats[0].v = d.total_orders ?? 0
    }
  } catch(_){}
  try {
    const g = await getDashboardGoods()
    if (g?.goods) topGoods.value = g.goods.slice(0,10)
  } catch(_){}
  try {
    const l = await getDashboardLine({type:chartR.value})
    if (l?.line) {
      chartData.comm = l.line.map(x=>x.dayString||'')
      chartData.s = l.line.map(x=>x.countSales||0)
    }
  } catch(_){}
  nextTick(()=>initChart())
}

function initChart() {
  if (!chartRef.value) return
  if (chart) chart.dispose()
  chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip:{trigger:'axis'}, legend:{data:['?],left:'left',top:0},
    grid:{left:10,right:20,bottom:20,top:40,containLabel:true},
    xAxis:{type:'category',data:chartData.comm,boundaryGap:false},
    yAxis:{type:'value',minInterval:1},
    series:[{name:'?,type:'line',smooth:false,data:chartData.s,
      lineStyle:{color:'#FF005A',width:2},itemStyle:{color:'#FF005A'}}],
  })
}
function switchChart(i) { chartR.value=i; loadDashboard() }

// =====  =====
async function fetchUsers() {
  try {
    const d = await getUserList({keyword:userKw.value,page:userPg.value,size:10})
    if (d?.records) { users.value = d.records; userTotal.value = d.total||0 }
    else if (Array.isArray(d)) { users.value = d; userTotal.value = d.length }
  } catch(_){}
}
async function toggleUser(row) {
  try {
    await updateUserStatus({userId:row.id,status:row.status===1?0:1})
    ElMessage.success('?); fetchUsers()
  } catch(e) { ElMessage.error(e.message) }
}
function showBalDlg(row) { balDlg.user=row.username||row.phone; balDlg.userId=row.id; balDlg.amount=''; balDlg.remark=''; balDlg.show=true }
async function doAdjust() {
  try {
    await adjustUserBalance({userId:balDlg.userId,amount:balDlg.amount,remark:balDlg.remark})
    ElMessage.success('?); balDlg.show=false; fetchUsers()
  } catch(e) { ElMessage.error(e.message) }
}

// =====  =====
async function fetchMerchants() {
  try {
    const d = await getMerchantList({keyword:merKw.value,page:merPg.value,size:10})
    if (d?.records) { merchants.value = d.records; merTotal.value = d.total||0 }
    else if (Array.isArray(d)) { merchants.value = d; merTotal.value = d.length }
  } catch(_){}
}
async function toggleMer(row) {
  try {
    await updateMerchantStatus({merchantId:row.id,status:row.status===1?0:1})
    ElMessage.success('?); fetchMerchants()
  } catch(e) { ElMessage.error(e.message) }
}
async function fetchMerApplies() {
  try {
    const d = await getMerchantApplyList({page:1,size:50})
    applies.value = d?.records || (Array.isArray(d)?d:[])
    applyDlg.show = true
  } catch(_){}
}
async function auditApply(row, approved) {
  try {
    await auditMerchantApply({applyId:row.id,approved})
    ElMessage.success(approved?'':'?)
    applies.value = applies.value.filter(x=>x.id!==row.id)
  } catch(e) { ElMessage.error(e.message) }
}

// =====  =====
async function fetchProducts() {
  try {
    const d = await getProductList({keyword:prodKw.value,page:prodPg.value,size:10})
    if (d?.records) { products.value = d.records; prodTotal.value = d.total||0 }
    else if (Array.isArray(d)) { products.value = d; prodTotal.value = d.length }
  } catch(_){}
}
async function auditProd(row, status) {
  try {
    await auditProduct({productId:row.id,status})
    ElMessage.success(status===1?'?:'?); fetchProducts()
  } catch(e) { ElMessage.error(e.message) }
}

// =====  =====
async function fetchOrders() {
  try {
    const d = await getOrderList({keyword:orderKw.value,page:orderPg.value,size:10})
    if (d?.records) { orders.value = d.records; orderTotal.value = d.total||0 }
    else if (Array.isArray(d)) { orders.value = d; orderTotal.value = d.length }
  } catch(_){}
}
async function doRefund(row) {
  try {
    await ElMessageBox.confirm(`?${row.orderNo||row.id},'?,{type:'warning'})
    await forceRefund(row.id)
    ElMessage.success('?); fetchOrders()
  } catch(_){}
}

// ===== ?=====
async function fetchRecharges() {
  try {
    const d = await getRechargePending({page:1,size:100})
    recharges.value = d?.records || (Array.isArray(d)?d:[])
    recPending.value = recharges.value.length
  } catch(_){}
}
async function auditRec(row, approved) {
  try {
    await auditRecharge({id:row.id,approved,reason:''})
    ElMessage.success(approved?'':'?); fetchRecharges()
  } catch(e) { ElMessage.error(e.message) }
}

// =====  =====
async function fetchWithdraws() {
  try {
    const d = await getWithdrawPending({page:1,size:100})
    withdraws.value = d?.records || (Array.isArray(d)?d:[])
    witPending.value = withdraws.value.length
  } catch(_){}
}
async function auditWit(row, approved) {
  try {
    await auditWithdraw({id:row.id,approved,txHash:'',reason:''})
    ElMessage.success(approved?'':'?); fetchWithdraws()
  } catch(e) { ElMessage.error(e.message) }
}

// =====  =====
async function fetchBanners() {
  try {
    const params = { page: bannerPg.value, size: 20 }
    if (bannerType.value) params.type = bannerType.value
    const d = await getBannerList(params)
    if (d?.records) { banners.value = d.records; bannerTotal.value = d.total || 0 }
    else if (Array.isArray(d)) { banners.value = d; bannerTotal.value = d.length }
  } catch(_){}
}
function showBannerDlg(row) {
  if (row) {
    bannerDlg.uuid = row.uuid; bannerDlg.title = row.title||''; bannerDlg.type = row.type||'home'
    bannerDlg.imgUrl = row.imgUrl||''; bannerDlg.sort = row.sort||0; bannerDlg.linkUrl = row.linkUrl||''
  } else {
    bannerDlg.uuid = ''; bannerDlg.title = ''; bannerDlg.type = 'home'
    bannerDlg.imgUrl = ''; bannerDlg.sort = 0; bannerDlg.linkUrl = ''
  }
  bannerDlg.show = true
}
async function saveBannerDlg() {
  try {
    const body = { title:bannerDlg.title, type:bannerDlg.type, imgUrl:bannerDlg.imgUrl, sort:bannerDlg.sort, linkUrl:bannerDlg.linkUrl }
    if (bannerDlg.uuid) await updateBanner(bannerDlg.uuid, body)
    else await saveBanner(body)
    ElMessage.success('?); bannerDlg.show = false; fetchBanners()
  } catch(e) { ElMessage.error(e.message) }
}
async function delBanner(row) {
  try {
    await ElMessageBox.confirm('','',{type:'warning'})
    await deleteBanner(row.uuid); ElMessage.success('?); fetchBanners()
  } catch(_){}
}

// =====  =====
async function fetchCategories() {
  try {
    const params = { page: catPg.value, size: 20 }
    if (catLevel.value) params.level = catLevel.value
    const d = await getCategoryList(params)
    if (d?.records) { categories.value = d.records; catTotal.value = d.total || 0 }
    else if (Array.isArray(d)) { categories.value = d; catTotal.value = d.length }
  } catch(_){}
}
function showCatDlg(row) {
  if (row) {
    catDlg.uuid = row.uuid; catDlg.name = row.name||''; catDlg.sort = row.sort||0
    catDlg.level = row.level||1; catDlg.parentId = row.parentId||'0'
    catDlg.type = row.type||1; catDlg.iconImg = row.iconImg||''; catDlg.status = row.status||1
  } else {
    catDlg.uuid = ''; catDlg.name = ''; catDlg.sort = 0
    catDlg.level = 1; catDlg.parentId = '0'; catDlg.type = 1; catDlg.iconImg = ''; catDlg.status = 1
  }
  catDlg.show = true
}
async function saveCatDlg() {
  try {
    const body = { name:catDlg.name, sort:catDlg.sort, level:catDlg.level, parentId:catDlg.parentId, type:catDlg.type, iconImg:catDlg.iconImg, status:catDlg.status }
    if (catDlg.uuid) await updateCategory(catDlg.uuid, body)
    else await saveCategory(body)
    ElMessage.success('?); catDlg.show = false; fetchCategories()
  } catch(e) { ElMessage.error(e.message) }
}
async function toggleCatStatus(row) {
  try {
    await updateCategoryStatus(row.uuid, {status: row.status===1?0:1})
    ElMessage.success('?); fetchCategories()
  } catch(e) { ElMessage.error(e.message) }
}
async function delCat(row) {
  try {
    await ElMessageBox.confirm('','',{type:'warning'})
    await deleteCategory(row.uuid); ElMessage.success('?); fetchCategories()
  } catch(_){}
}

// =====  =====
async function fetchEvaluations() {
  try {
    const params = { page: evalPg.value, size: 20 }
    if (evalKw.value) params.keyword = evalKw.value
    if (evalStatus.value !== null && evalStatus.value !== '') params.status = evalStatus.value
    const d = await getEvaluationList(params)
    if (d?.records) { evaluations.value = d.records; evalTotal.value = d.total || 0 }
    else if (Array.isArray(d)) { evaluations.value = d; evalTotal.value = d.length }
  } catch(_){}
}
async function toggleEval(row) {
  try {
    await updateEvaluationStatus(row.uuid, {status: row.status===1?0:1})
    ElMessage.success('?); fetchEvaluations()
  } catch(e) { ElMessage.error(e.message) }
}
async function delEval(row) {
  try {
    await ElMessageBox.confirm('','',{type:'warning'})
    await deleteEvaluation(row.uuid); ElMessage.success('?); fetchEvaluations()
  } catch(_){}
}

// ===== ?=====
async function fetchAttrCats() {
  try {
    const params = { page: attrCatPg.value, size: 20 }
    if (attrCatKw.value) params.keyword = attrCatKw.value
    const d = await getAttrCategoryList(params)
    if (d?.records) { attrCats.value = d.records; attrCatTotal.value = d.total || 0 }
    else if (Array.isArray(d)) { attrCats.value = d; attrCatTotal.value = d.length }
  } catch(_){}
}
function showAttrCatDlg(row) {
  if (row) { attrCatDlg.uuid = row.uuid || row.id; attrCatDlg.name = row.name||''; attrCatDlg.sort = row.sort||0 }
  else { attrCatDlg.uuid = ''; attrCatDlg.name = ''; attrCatDlg.sort = 0 }
  attrCatDlg.show = true
}
async function saveAttrCatDlg() {
  try {
    const body = { name: attrCatDlg.name, sort: attrCatDlg.sort }
    if (attrCatDlg.uuid) await updateAttrCategory(attrCatDlg.uuid, body)
    else await saveAttrCategory(body)
    ElMessage.success('?); attrCatDlg.show = false; fetchAttrCats()
  } catch(e) { ElMessage.error(e.message) }
}
async function delAttrCat(row) {
  try {
    await ElMessageBox.confirm('','',{type:'warning'})
    await deleteAttrCategory(row.uuid || row.id); ElMessage.success('?); fetchAttrCats()
  } catch(_){}
}

// ===== ?=====
async function fetchAttrs() {
  try {
    const params = { page: attrPg.value, size: 20 }
    if (attrCatFilter.value) params.categoryId = attrCatFilter.value
    const d = await getAttrList(params)
    if (d?.records) { attrs.value = d.records; attrTotal.value = d.total || 0 }
    else if (Array.isArray(d)) { attrs.value = d; attrTotal.value = d.length }
  } catch(_){}
}
function showAttrDlg(row) {
  if (row) { attrDlg.uuid = row.uuid || row.id; attrDlg.categoryId = row.categoryId||''; attrDlg.sort = row.sort||0 }
  else { attrDlg.uuid = ''; attrDlg.categoryId = ''; attrDlg.sort = 0 }
  attrDlg.show = true
}
async function saveAttrDlg() {
  try {
    const body = { categoryId: attrDlg.categoryId, sort: attrDlg.sort }
    if (attrDlg.uuid) await updateAttr(attrDlg.uuid, body)
    else await saveAttr(body)
    ElMessage.success('?); attrDlg.show = false; fetchAttrs()
  } catch(e) { ElMessage.error(e.message) }
}
async function delAttr(row) {
  try {
    await ElMessageBox.confirm('','',{type:'warning'})
    await deleteAttr(row.uuid || row.id); ElMessage.success('?); fetchAttrs()
  } catch(_){}
}

// =====  =====
onMounted(() => {
  loadDashboard()
  timer = setInterval(loadDashboard, 30000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (chart) chart.dispose()
})
</script>

<style scoped>
.mall-panel { padding: 0; }
.mall-tabs { border-radius: 8px; overflow: hidden; }

/* KPI */
.kpi-row { margin-bottom: 16px; }
.kpi-card { border-radius: 8px; padding: 22px 16px; color: #fff; text-align: center; min-height: 96px; display: flex; flex-direction: column; justify-content: center; margin-bottom: 12px; }
.kpi-card.c1 { background: rgba(255,131,153,0.12); }
.kpi-card.c2 { background: linear-gradient(135deg,#71C3FF,#54a0ff); }
.kpi-card.c3 { background: linear-gradient(135deg,#7190FF,#5f6fff); }
.kpi-card.c4 { background: linear-gradient(135deg,#5AD7CF,#2ed573); }
.kpi-num { font-size: 28px; font-weight: 700; }
.kpi-label { font-size: 13px; opacity: .9; margin-top: 4px; }

/* Card */
.card-hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.card-tt { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 12px; }

/* Chart tabs */
.ctab { padding: 3px 10px; border:1px solid #ddd; border-radius:4px; font-size:12px; cursor:pointer; color:#999; margin-left:4px; user-select:none; }
.ctab.on { border-color:#1552F0; color:#1552F0; }

/* Chart */
.chart-box { width:100%; height:360px; }

/* Order stats */
.order-card { height: 444px; }
.order-grid { display:flex; flex-wrap:wrap; }
.oi { width:50%; text-align:center; padding:24px 0; }
.oi-num { font-size:22px; font-weight:700; color:#e99d42; }
.oi-lbl { font-size:13px; color:#999; margin-top:4px; }

/* Toolbar */
.tb-bar { display:flex; gap:8px; margin-bottom:12px; }
@media (max-width: 768px) { .page-shell, [class*="page-shell"] { padding: 10px !important; } .page-header h2 { font-size: 16px !important; } .el-row { flex-direction: column !important; } .el-col { max-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; } .el-table { font-size: 12px; } .el-card { margin-bottom: 12px; } }
</style>
