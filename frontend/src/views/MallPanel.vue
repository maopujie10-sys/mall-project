<template>
  <div class="mall-panel">
    <el-tabs v-model="activeTab" type="border-card" class="mall-tabs">
      <!-- ========== 浠〃鐩?========== -->
      <el-tab-pane name="dashboard">
        <template #label><el-icon><DataAnalysis /></el-icon> 浠〃鐩</template>

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
                <span class="card-tt">閿€鍞秼鍔</span>
                <span class="chart-tabs">
                  <span v-for="(t,i) in ['浠婃棩','杩澶?,'杩?0澶?]" :key="i"
                    class="ctab" :class="{on:chartR===i}" @click="switchChart(i)">{{t}}</span>
                </span>
              </div>
              <div ref="chartRef" class="chart-box"></div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="never" class="order-card">
              <div class="card-tt">璁㈠崟缁熻</div>
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
          <div class="card-tt">鐑攢鍟嗗搧 Top10</div>
          <el-table :data="topGoods" stripe size="small" height="380">
            <el-table-column type="index" label="#" width="50" align="center" />
            <el-table-column prop="name" label="鍟嗗搧鍚嶇О" min-width="200" />
            <el-table-column label="浠锋牸" width="120" align="center">
              <template #default="{row}">楼{{ fmt(row.prizes||row.price) }}</template>
            </el-table-column>
            <el-table-column label="..." width="100" align="center">
              <template #default="{row}">{{ fmt(row.sellCount) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- ========== 鐢ㄦ埛绠＄悊 ========== -->
      <el-tab-pane name="users">
        <template #label><el-icon><User /></el-icon> 鐢ㄦ埛绠＄悊</template>
        <div class="tb-bar">
          <el-input v-model="userKw" placeholder="鎼滅储鐢ㄦ埛" style="width:220px" clearable @clear="fetchUsers" @keyup.enter="fetchUsers" />
          <el-button type="primary" @click="fetchUsers">鎼滅储</el-button>
        </div>
        <el-table :data="users" stripe size="small" height="520">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="username" label="..." width="120" />
          <el-table-column prop="phone" label="..." width="130" />
          <el-table-column prop="balance" label="浣欓" width="110" />
          <el-table-column prop="status" label="..." width="90">
            <template #default="{row}"><el-tag :type="row.status===1?'success':'danger'" size="small">{{ row.status===1?'姝ｅ父':'绂佺敤' }}</el-tag></template>
          </el-table-column>
          <el-table-column label="鎿嶄綔" width="200">
            <template #default="{row}">
              <el-button size="small" @click="toggleUser(row)">{{ row.status===1?'绂佺敤':'鍚敤' }}</el-button>
              <el-button size="small" type="warning" @click="showBalDlg(row)">璋冧綑棰</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="userTotal" :page-size="10" v-model:current-page="userPg" @current-change="fetchUsers" small />
      </el-tab-pane>

      <!-- ========== 鍟嗗绠＄悊 ========== -->
      <el-tab-pane name="merchants">
        <template #label><el-icon><Shop /></el-icon> 鍟嗗绠＄悊</template>
        <div class="tb-bar">
          <el-input v-model="merKw" placeholder="鎼滅储鍟嗗" style="width:220px" clearable @clear="fetchMerchants" @keyup.enter="fetchMerchants" />
          <el-button type="primary" @click="fetchMerchants">鎼滅储</el-button>
          <el-button @click="fetchMerApplies">鍏ラ┗鐢宠</el-button>
        </div>
        <el-table :data="merchants" stripe size="small" height="520">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="name" label="鍟嗗鍚嶇О" min-width="150" />
          <el-table-column prop="phone" label="..." width="130" />
          <el-table-column prop="status" label="..." width="90">
            <template #default="{row}"><el-tag :type="row.status===1?'success':'danger'" size="small">{{ row.status===1?'姝ｅ父':'绂佺敤' }}</el-tag></template>
          </el-table-column>
          <el-table-column label="鎿嶄綔" width="120">
            <template #default="{row}">
              <el-button size="small" @click="toggleMer(row)">{{ row.status===1?'绂佺敤':'鍚敤' }}</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="merTotal" :page-size="10" v-model:current-page="merPg" @current-change="fetchMerchants" small />
      </el-tab-pane>

      <!-- ========== 鍟嗗搧瀹℃牳 ========== -->
      <el-tab-pane name="products">
        <template #label><el-icon><Goods /></el-icon> 鍟嗗搧瀹℃牳</template>
        <div class="tb-bar">
          <el-input v-model="prodKw" placeholder="鎼滅储鍟嗗搧" style="width:220px" clearable @clear="fetchProducts" @keyup.enter="fetchProducts" />
          <el-button type="primary" @click="fetchProducts">鎼滅储</el-button>
        </div>
        <el-table :data="products" stripe size="small" height="520">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="name" label="鍟嗗搧鍚嶇О" min-width="180" />
          <el-table-column prop="price" label="浠锋牸" width="100" />
          <el-table-column prop="status" label="..." width="90">
            <template #default="{row}"><el-tag :type="row.status===1?'success':row.status===0?'warning':'info'" size="small">{{ statTxt(row.status) }}</el-tag></template>
          </el-table-column>
          <el-table-column label="鎿嶄綔" width="160">
            <template #default="{row}">
              <el-button v-if="row.status===0" size="small" type="success" @click="auditProd(row,1)">涓婃灦</el-button>
              <el-button v-if="row.status===1" size="small" type="danger" @click="auditProd(row,0)">涓嬫灦</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="prodTotal" :page-size="10" v-model:current-page="prodPg" @current-change="fetchProducts" small />
      </el-tab-pane>

      <!-- ========== 璁㈠崟绠＄悊 ========== -->
      <el-tab-pane name="orders">
        <template #label><el-icon><Document /></el-icon> 璁㈠崟绠＄悊</template>
        <div class="tb-bar">
          <el-input v-model="orderKw" placeholder="鎼滅储璁㈠崟" style="width:220px" clearable @clear="fetchOrders" @keyup.enter="fetchOrders" />
          <el-button type="primary" @click="fetchOrders">鎼滅储</el-button>
        </div>
        <el-table :data="orders" stripe size="small" height="520">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="orderNo" label="..." width="180" />
          <el-table-column prop="amount" label="閲戦" width="100" />
          <el-table-column prop="status" label="..." width="90">
            <template #default="{row}"><el-tag size="small">{{ row.status }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="createTime" label="鏃堕棿" width="160" />
          <el-table-column label="鎿嶄綔" width="100">
            <template #default="{row}">
              <el-button size="small" type="danger" @click="doRefund(row)">閫€娆</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="orderTotal" :page-size="10" v-model:current-page="orderPg" @current-change="fetchOrders" small />
      </el-tab-pane>

      <!-- ========== 鍏呭€煎鏍?========== -->
      <el-tab-pane name="recharges">
        <template #label><el-icon><Wallet /></el-icon> 鍏呭€煎鏍?<el-badge :value="recPending" :hidden="!recPending" /></template>
        <el-table :data="recharges" stripe size="small" height="560">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="orderNo" label="..." width="180" />
          <el-table-column prop="amount" label="閲戦" width="100" />
          <el-table-column prop="userId" label="鐢ㄦ埛ID" width="80" />
          <el-table-column prop="createTime" label="鏃堕棿" width="160" />
          <el-table-column label="鎿嶄綔" width="160">
            <template #default="{row}">
              <el-button size="small" type="success" @click="auditRec(row,true)">閫氳繃</el-button>
              <el-button size="small" type="danger" @click="auditRec(row,false)">鎷掔粷</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- ========== 鎻愮幇瀹℃牳 ========== -->
      <el-tab-pane name="withdraws">
        <template #label><el-icon><Money /></el-icon> 鎻愮幇瀹℃牳 <el-badge :value="witPending" :hidden="!witPending" /></template>
        <el-table :data="withdraws" stripe size="small" height="560">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="orderNo" label="..." width="180" />
          <el-table-column prop="amount" label="閲戦" width="100" />
          <el-table-column prop="userId" label="鐢ㄦ埛ID" width="80" />
          <el-table-column prop="createTime" label="鏃堕棿" width="160" />
          <el-table-column label="鎿嶄綔" width="220">
            <template #default="{row}">
              <el-button size="small" type="success" @click="auditWit(row,true)">閫氳繃</el-button>
              <el-button size="small" type="danger" @click="auditWit(row,false)">鎷掔粷</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- ========== 杞挱绠＄悊 ========== -->
      <el-tab-pane name="banners">
        <template #label><el-icon><Picture /></el-icon> 杞挱绠＄悊</template>
        <div class="tb-bar">
          <el-select v-model="bannerType" placeholder="绫诲瀷" style="width:120px" clearable @change="fetchBanners">
            <el-option label="棣栭〉" value="home" /><el-option label="娲诲姩" value="activity" />
          </el-select>
          <el-button type="primary" @click="fetchBanners">鍒锋柊</el-button>
          <el-button type="success" @click="showBannerDlg()">鏂板杞挱</el-button>
        </div>
        <el-table :data="banners" stripe size="small" height="480">
          <el-table-column prop="uuid" label="UUID" width="120" />
          <el-table-column prop="title" label="鏍囬" min-width="150" />
          <el-table-column prop="type" label="绫诲瀷" width="100" />
          <el-table-column prop="sort" label="鎺掑簭" width="70" />
          <el-table-column prop="imgUrl" label="鍥剧墖URL" min-width="200" />
          <el-table-column label="鎿嶄綔" width="160">
            <template #default="{row}">
              <el-button size="small" @click="showBannerDlg(row)">缂栬緫</el-button>
              <el-button size="small" type="danger" @click="delBanner(row)">鍒犻櫎</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="bannerTotal" :page-size="20" v-model:current-page="bannerPg" @current-change="fetchBanners" small />
      </el-tab-pane>

      <!-- ========== 鍒嗙被绠＄悊 ========== -->
      <el-tab-pane name="categories">
        <template #label><el-icon><Grid /></el-icon> 鍒嗙被绠＄悊</template>
        <div class="tb-bar">
          <el-select v-model="catLevel" placeholder="灞傜骇" style="width:100px" clearable @change="fetchCategories">
            <el-option label="涓€绾' :value="1" /><el-option label="浜岀骇" :value="2" />
          </el-select>
          <el-button type="primary" @click="fetchCategories">鍒锋柊</el-button>
          <el-button type="success" @click="showCatDlg()">鏂板鍒嗙被</el-button>
        </div>
        <el-table :data="categories" stripe size="small" height="480">
          <el-table-column prop="uuid" label="UUID" width="120" />
          <el-table-column prop="name" label="鍚嶇О" min-width="150" />
          <el-table-column prop="sort" label="鎺掑簭" width="70" />
          <el-table-column prop="level" label="灞傜骇" width="70" />
          <el-table-column prop="status" label="..." width="80">
            <template #default="{row}"><el-tag :type="row.status===1?'success':'danger'" size="small">{{ row.status===1?'鍚敤':'绂佺敤' }}</el-tag></template>
          </el-table-column>
          <el-table-column label="鎿嶄綔" width="220">
            <template #default="{row}">
              <el-button size="small" @click="showCatDlg(row)">缂栬緫</el-button>
              <el-button size="small" :type="row.status===1?'warning':'success'" @click="toggleCatStatus(row)">{{ row.status===1?'绂佺敤':'鍚敤' }}</el-button>
              <el-button size="small" type="danger" @click="delCat(row)">鍒犻櫎</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="catTotal" :page-size="20" v-model:current-page="catPg" @current-change="fetchCategories" small />
      </el-tab-pane>

      <!-- ========== 璇勪环绠＄悊 ========== -->
      <el-tab-pane name="evaluations">
        <template #label><el-icon><Star /></el-icon> 璇勪环绠＄悊</template>
        <div class="tb-bar">
          <el-input v-model="evalKw" placeholder="鎼滅储璇勪环" style="width:220px" clearable @clear="fetchEvaluations" @keyup.enter="fetchEvaluations" />
          <el-select v-model="evalStatus" placeholder="..." style="width:100px" clearable @change="fetchEvaluations">
            <el-option label="鏄剧ず" :value="1" /><el-option label="闅愯棌" :value="0" />
          </el-select>
          <el-button type="primary" @click="fetchEvaluations">鎼滅储</el-button>
        </div>
        <el-table :data="evaluations" stripe size="small" height="480">
          <el-table-column prop="uuid" label="UUID" width="100" />
          <el-table-column prop="userName" label="鐢ㄦ埛" width="100" />
          <el-table-column prop="content" label="鍐呭" min-width="200" show-overflow-tooltip />
          <el-table-column prop="rating" label="璇勫垎" width="70">
            <template #default="{row}">{{ '鈽?.repeat(row.rating||0) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="..." width="80">
            <template #default="{row}"><el-tag :type="row.status===1?'success':'info'" size="small">{{ row.status===1?'鏄剧ず':'闅愯棌' }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="createTime" label="鏃堕棿" width="160" />
          <el-table-column label="鎿嶄綔" width="160">
            <template #default="{row}">
              <el-button size="small" :type="row.status===1?'warning':'success'" @click="toggleEval(row)">{{ row.status===1?'闅愯棌':'鏄剧ず' }}</el-button>
              <el-button size="small" type="danger" @click="delEval(row)">鍒犻櫎</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="evalTotal" :page-size="20" v-model:current-page="evalPg" @current-change="fetchEvaluations" small />
      </el-tab-pane>

      <!-- ========== 灞炴€у垎绫荤鐞?========== -->
      <el-tab-pane name="attrCats">
        <template #label><el-icon><Collection /></el-icon> 灞炴€у垎绫</template>
        <div class="tb-bar">
          <el-input v-model="attrCatKw" placeholder="鎼滅储" style="width:220px" clearable @clear="fetchAttrCats" @keyup.enter="fetchAttrCats" />
          <el-button type="primary" @click="fetchAttrCats">鎼滅储</el-button>
          <el-button type="success" @click="showAttrCatDlg()">鏂板鍒嗙被</el-button>
        </div>
        <el-table :data="attrCats" stripe size="small" height="480">
          <el-table-column prop="id" label="ID" width="200" />
          <el-table-column prop="name" label="鍚嶇О" min-width="150" />
          <el-table-column prop="sort" label="鎺掑簭" width="80" />
          <el-table-column label="鎿嶄綔" width="160">
            <template #default="{row}">
              <el-button size="small" @click="showAttrCatDlg(row)">缂栬緫</el-button>
              <el-button size="small" type="danger" @click="delAttrCat(row)">鍒犻櫎</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="attrCatTotal" :page-size="20" v-model:current-page="attrCatPg" @current-change="fetchAttrCats" small />
      </el-tab-pane>

      <!-- ========== 灞炴€х鐞?========== -->
      <el-tab-pane name="attrs">
        <template #label><el-icon><SetUp /></el-icon> 灞炴€х鐞</template>
        <div class="tb-bar">
          <el-input v-model="attrCatFilter" placeholder="灞炴€у垎绫籌D" style="width:220px" clearable @clear="fetchAttrs" @keyup.enter="fetchAttrs" />
          <el-button type="primary" @click="fetchAttrs">鎼滅储</el-button>
          <el-button type="success" @click="showAttrDlg()">鏂板灞炴€</el-button>
        </div>
        <el-table :data="attrs" stripe size="small" height="480">
          <el-table-column prop="id" label="ID" width="200" />
          <el-table-column prop="categoryId" label="鍒嗙被ID" width="200" />
          <el-table-column prop="sort" label="鎺掑簭" width="80" />
          <el-table-column label="鎿嶄綔" width="160">
            <template #default="{row}">
              <el-button size="small" @click="showAttrDlg(row)">缂栬緫</el-button>
              <el-button size="small" type="danger" @click="delAttr(row)">鍒犻櫎</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination style="margin-top:12px" background layout="prev,next" :total="attrTotal" :page-size="20" v-model:current-page="attrPg" @current-change="fetchAttrs" small />
      </el-tab-pane>
    </el-tabs>

    <!-- 璋冧綑棰濆脊绐?-->
    <el-dialog v-model="balDlg.show" title="璋冩暣浣欓" width="400px">
      <el-form label-width="80px">
        <el-form-item label="鐢ㄦ埛">{{ balDlg.user }}</el-form-item>
        <el-form-item label="閲戦"><el-input v-model="balDlg.amount" placeholder="姝ｆ暟澧炲姞,璐熸暟鍑忓皯" /></el-form-item>
        <el-form-item label="澶囨敞"><el-input v-model="balDlg.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="balDlg.show=false">鍙栨秷</el-button><el-button type="primary" @click="doAdjust">纭</el-button></template>
    </el-dialog>

    <!-- 鍏ラ┗瀹℃牳寮圭獥 -->
    <el-dialog v-model="applyDlg.show" title="鍏ラ┗鐢宠瀹℃牳" width="500px">
      <el-table :data="applies" stripe size="small" height="400">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="..." width="120" />
        <el-table-column prop="phone" label="..." width="130" />
        <el-table-column label="鎿嶄綔" width="140">
          <template #default="{row}">
            <el-button size="small" type="success" @click="auditApply(row,true)">閫氳繃</el-button>
            <el-button size="small" type="danger" @click="auditApply(row,false)">鎷掔粷</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 杞挱缂栬緫寮圭獥 -->
    <el-dialog v-model="bannerDlg.show" :title="bannerDlg.uuid?'缂栬緫杞挱':'鏂板杞挱'" width="500px">
      <el-form label-width="80px">
        <el-form-item label="鏍囬"><el-input v-model="bannerDlg.title" /></el-form-item>
        <el-form-item label="绫诲瀷"><el-select v-model="bannerDlg.type" style="width:100%"><el-option label="棣栭〉" value="home" /><el-option label="娲诲姩" value="activity" /></el-select></el-form-item>
        <el-form-item label="鍥剧墖URL"><el-input v-model="bannerDlg.imgUrl" placeholder="https://..." /></el-form-item>
        <el-form-item label="閾炬帴URL"><el-input v-model="bannerDlg.linkUrl" /></el-form-item>
        <el-form-item label="鎺掑簭"><el-input-number v-model="bannerDlg.sort" :min="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="bannerDlg.show=false">鍙栨秷</el-button><el-button type="primary" @click="saveBannerDlg">淇濆瓨</el-button></template>
    </el-dialog>

    <!-- 鍒嗙被缂栬緫寮圭獥 -->
    <el-dialog v-model="catDlg.show" :title="catDlg.uuid?'缂栬緫鍒嗙被':'鏂板鍒嗙被'" width="500px">
      <el-form label-width="80px">
        <el-form-item label="鍚嶇О"><el-input v-model="catDlg.name" /></el-form-item>
        <el-form-item label="灞傜骇"><el-input-number v-model="catDlg.level" :min="1" :max="3" /></el-form-item>
        <el-form-item label="鐖剁骇ID"><el-input v-model="catDlg.parentId" placeholder="0" /></el-form-item>
        <el-form-item label="绫诲瀷"><el-input-number v-model="catDlg.type" :min="1" /></el-form-item>
        <el-form-item label="鎺掑簭"><el-input-number v-model="catDlg.sort" :min="0" /></el-form-item>
        <el-form-item label="鐘舵€?><el-switch v-model="catDlg.status" :active-value="1" :inactive-value="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="catDlg.show=false">鍙栨秷</el-button><el-button type="primary" @click="saveCatDlg">淇濆瓨</el-button></template>
    </el-dialog>

    <!-- 灞炴€у垎绫荤紪杈戝脊绐?-->
    <el-dialog v-model="attrCatDlg.show" :title="attrCatDlg.uuid?'缂栬緫灞炴€у垎绫':'鏂板灞炴€у垎绫?" width="400px">
      <el-form label-width="80px">
        <el-form-item label="鍚嶇О"><el-input v-model="attrCatDlg.name" /></el-form-item>
        <el-form-item label="鎺掑簭"><el-input-number v-model="attrCatDlg.sort" :min="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="attrCatDlg.show=false">鍙栨秷</el-button><el-button type="primary" @click="saveAttrCatDlg">淇濆瓨</el-button></template>
    </el-dialog>

    <!-- 灞炴€х紪杈戝脊绐?-->
    <el-dialog v-model="attrDlg.show" :title="attrDlg.uuid?'缂栬緫灞炴€':'鏂板灞炴€?" width="400px">
      <el-form label-width="100px">
        <el-form-item label="灞炴€у垎绫籌D"><el-input v-model="attrDlg.categoryId" /></el-form-item>
        <el-form-item label="鎺掑簭"><el-input-number v-model="attrDlg.sort" :min="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="attrDlg.show=false">鍙栨秷</el-button><el-button type="primary" @click="saveAttrDlg">淇濆瓨</el-button></template>
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
  getMerchantList, updateMerchantStatus, getMerchantApplyList, auditMerchantApply, getDashboardLine, getDashboardGoods,
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

// ===== 浠〃鐩樻暟鎹?=====
const kpis = reactive([
  { label:'鎬荤敤鎴?, value:0, color:'c1', key:'total_users' },
  { label:'浠婃棩璁㈠崟', value:0, color:'c2', key:'today_orders' },
  { label:'浠婃棩浜ゆ槗棰?, value:0, color:'c3', key:'today_amount' },
  { label:'?, value:0, color:'c4', key:'pending_recharge' },
])
const orderStats = reactive([
  { l:'鎬昏鍗?, v:0 },{ l:'?, v:0 },{ l:'宸插畬鎴?, v:0 },{ l:'宸插彇娑?, v:0 },
])
const topGoods = ref([])
const chartData = reactive({ comm:[], s:[] })

// ===== 鍚勬ā鍧楁暟鎹?=====
const users = ref([]), userKw = ref(''), userPg = ref(1), userTotal = ref(0)
const merchants = ref([]), merKw = ref(''), merPg = ref(1), merTotal = ref(0)
const products = ref([]), prodKw = ref(''), prodPg = ref(1), prodTotal = ref(0)
const orders = ref([]), orderKw = ref(''), orderPg = ref(1), orderTotal = ref(0)
const recharges = ref([]), recPending = ref(0)
const withdraws = ref([]), witPending = ref(0)
const applies = ref([])
const balDlg = reactive({ show:false, user:'', userId:null, amount:'', remark:''}) const applyDlg = reactive({ show:false }) // ===== ===== const banners = ref([]), bannerType = ref(''), bannerPg = ref(1), bannerTotal = ref(0)
const bannerDlg = reactive({ show:false, uuid:'', title:'', type:'home', imgUrl:'', sort:0, linkUrl:'' })

// ===== 鍒嗙被 =====
const categories = ref([]), catLevel = ref(null), catPg = ref(1), catTotal = ref(0)
const catDlg = reactive({ show:false, uuid:'', name:'', sort:0, level:1, parentId:'0', type:1, iconImg:'', status:1 })

// ===== 璇勪环 =====
const evaluations = ref([]), evalKw = ref(''), evalStatus = ref(null), evalPg = ref(1), evalTotal = ref(0)

// ===== 灞炴€у垎绫?+ 灞炴€?=====
const attrCats = ref([]), attrCatKw = ref(''), attrCatPg = ref(1), attrCatTotal = ref(0)
const attrCatDlg = reactive({ show:false, uuid:'', name:'', sort:0 })
const attrs = ref([]), attrCatFilter = ref(''), attrPg = ref(1), attrTotal = ref(0)
const attrDlg = reactive({ show:false, uuid:'', categoryId:'', sort:0 })

// ===== 閫氱敤 =====
function fmt(v) {
  if (v == null) return '0'
  const n = Number(v)
  return Number.isNaN(n) ? String(v) : n.toLocaleString('en-US',{maximumFractionDigits:2})
}
function statTxt(s) { return s===1?'涓婃灦':s===0?'寰呭':'涓嬫灦'} // ===== ?===== async function loadDashboard() { try { const d = await getDashboard() if (d) { kpis[0].value = d.total_users '? d.totalUsers ?? 0 kpis[1].value = d.today_orders ?? d.todayOrders ?? 0 kpis[2].value = d.today_amount ?? d.todayAmount ?? 0 kpis[3].value = (d.pending_recharge||0) + (d.pending_withdraw||0) + (d.pending_merchant||0) orderStats[0].v = d.total_orders ?? 0 } } catch(_){} try { const g = await getDashboardGoods() if (g?.goods) topGoods.value = g.goods.slice(0,10) } catch(_){} try { const l = await getDashboardLine({type:chartR.value}) if (l?.line) { chartData.comm = l.line.map(x=>x.dayString||'')
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
    tooltip:{trigger:'axis'}, legend:{data:['閿€閲?],left:'left',top:0},
    grid:{left:10,right:20,bottom:20,top:40,containLabel:true},
    xAxis:{type:'category',data:chartData.comm,boundaryGap:false},
    yAxis:{type:'value',minInterval:1},
    series:[{name:'閿€閲?,type:'line',smooth:false,data:chartData.s,
      lineStyle:{color:'#FF005A',width:2},itemStyle:{color:'#FF005A'}}],
  })
}
function switchChart(i) { chartR.value=i; loadDashboard() }

// ===== 鐢ㄦ埛 =====
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
    ElMessage.success('宸叉洿鏂?); fetchUsers()
  } catch(e) { ElMessage.error(e.message) }
}
function showBalDlg(row) { balDlg.user=row.username||row.phone; balDlg.userId=row.id; balDlg.amount=''; balDlg.remark=''; balDlg.show=true }
async function doAdjust() {
  try {
    await adjustUserBalance({userId:balDlg.userId,amount:balDlg.amount,remark:balDlg.remark})
    ElMessage.success('?); balDlg.show=false; fetchUsers() } catch(e) { ElMessage.error(e.message) } } // ===== ===== async function fetchMerchants() { try { const d = await getMerchantList({keyword:merKw.value,page:merPg.value,size:10}) if (d?.records) { merchants.value = d.records; merTotal.value = d.total||0 } else if (Array.isArray(d)) { merchants.value = d; merTotal.value = d.length } } catch(_){} } async function toggleMer(row) { try { await updateMerchantStatus({merchantId:row.id,status:row.status===1?0:1}) ElMessage.success('宸叉洿鏂?); fetchMerchants()
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
    ElMessage.success(approved?'宸查€氳繃':'宸叉嫆缁?)
    applies.value = applies.value.filter(x=>x.id!==row.id)
  } catch(e) { ElMessage.error(e.message) }
}

// ===== 鍟嗗搧 =====
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
    ElMessage.success(status===1?'宸蹭笂鏋':'?); fetchProducts() } catch(e) { ElMessage.error(e.message) } } // ===== ===== async function fetchOrders() { try { const d = await getOrderList({keyword:orderKw.value,page:orderPg.value,size:10}) if (d?.records) { orders.value = d.records; orderTotal.value = d.total||0 } else if (Array.isArray(d)) { orders.value = d; orderTotal.value = d.length } } catch(_){} } async function doRefund(row) { try { await ElMessageBox.confirm(` ?${row.orderNo||row.id} ,'閫€娆剧‘璁?,{type:'warning'})
    await forceRefund(row.id)
    ElMessage.success('宸查€€娆?); fetchOrders()
  } catch(_){}
}

// ===== 鍏呭€?=====
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
    ElMessage.success(approved?'宸查€氳繃':'宸叉嫆缁?); fetchRecharges()
  } catch(e) { ElMessage.error(e.message) }
}

// ===== 鎻愮幇 =====
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
    ElMessage.success(approved?'宸查€氳繃':'?); fetchWithdraws() } catch(e) { ElMessage.error(e.message) } } // ===== ===== async function fetchBanners() { try { const params = { page: bannerPg.value, size: 20 } if (bannerType.value) params.type = bannerType.value const d = await getBannerList(params) if (d?.records) { banners.value = d.records; bannerTotal.value = d.total || 0 } else if (Array.isArray(d)) { banners.value = d; bannerTotal.value = d.length } } catch(_){} } function showBannerDlg(row) { if (row) { bannerDlg.uuid = row.uuid; bannerDlg.title = row.title||''; bannerDlg.type = row.type||'home'
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
    ElMessage.success('宸蹭繚瀛?); bannerDlg.show = false; fetchBanners()
  } catch(e) { ElMessage.error(e.message) }
}
async function delBanner(row) {
  try {
    await ElMessageBox.confirm('TODO','TODO',{type:'warning'})
    await deleteBanner(row.uuid); ElMessage.success('宸插垹闄?); fetchBanners()
  } catch(_){}
}

// ===== 鍒嗙被绠＄悊 =====
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
    ElMessage.success('宸蹭繚瀛?); catDlg.show = false; fetchCategories()
  } catch(e) { ElMessage.error(e.message) }
}
async function toggleCatStatus(row) {
  try {
    await updateCategoryStatus(row.uuid, {status: row.status===1?0:1})
    ElMessage.success('宸叉洿鏂?); fetchCategories()
  } catch(e) { ElMessage.error(e.message) }
}
async function delCat(row) {
  try {
    await ElMessageBox.confirm('纭鍒犻櫎璇ュ垎绫伙紵','鍒犻櫎纭',{type:'warning'})
    await deleteCategory(row.uuid); ElMessage.success('宸插垹闄?); fetchCategories()
  } catch(_){}
}

// ===== 璇勪环绠＄悊 =====
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
    ElMessage.success('宸叉洿鏂?); fetchEvaluations()
  } catch(e) { ElMessage.error(e.message) }
}
async function delEval(row) {
  try {
    await ElMessageBox.confirm('纭鍒犻櫎璇ヨ瘎浠凤紵','鍒犻櫎纭',{type:'warning'})
    await deleteEvaluation(row.uuid); ElMessage.success('宸插垹闄?); fetchEvaluations()
  } catch(_){}
}

// ===== 灞炴€у垎绫荤鐞?=====
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
    ElMessage.success('宸蹭繚瀛?); attrCatDlg.show = false; fetchAttrCats()
  } catch(e) { ElMessage.error(e.message) }
}
async function delAttrCat(row) {
  try {
    await ElMessageBox.confirm('纭鍒犻櫎璇ュ睘鎬у垎绫伙紵','鍒犻櫎纭',{type:'warning'})
    await deleteAttrCategory(row.uuid || row.id); ElMessage.success('宸插垹闄?); fetchAttrCats()
  } catch(_){}
}

// ===== 灞炴€х鐞?=====
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
    ElMessage.success('宸蹭繚瀛?); attrDlg.show = false; fetchAttrs()
  } catch(e) { ElMessage.error(e.message) }
}
async function delAttr(row) {
  try {
    await ElMessageBox.confirm('纭鍒犻櫎璇ュ睘鎬э紵','鍒犻櫎纭',{type:'warning'})
    await deleteAttr(row.uuid || row.id); ElMessage.success('宸插垹闄?); fetchAttrs()
  } catch(_){}
}

// ===== 鐢熷懡鍛ㄦ湡 =====
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
