<template>
  <div class="app-container px-20">
    <SetBootSteps/>
    <el-card>
      <div style="display: flex;justify-content: space-between;align-items: center;">
        <div class="flex items-center">
          <div class="flex items-center">
            <img :src="require('@/assets/images/wallet/Group 2104.png')" alt="" class="w-87 h-87 permission-icon"/>
            <div class="ml-21">
              <p class="mb-10 font-36 font-600">
                <FormatNumberShow :data="huoquyue.money" :currency="true"/>
              </p>
              <p class="font-18" style="color: #999">{{ $t('钱包余额') }}
                <span v-if="huoquyue.frozenMoney>0">({{ $t('冻结金额') }}
                <FormatNumberShow :data="huoquyue.frozenMoney" :currency="true"/>)</span>
              </p>
            </div>
          </div>
          <div class="w-1 h-59 mx-100" style="background: #eee"></div>
          <div class="flex items-center">
            <img :src="require('@/assets/images/wallet/Group 2104 (2).png')" alt="" class="w-87 h-87 permission-icon"/>
            <div class="ml-21">
              <p class="mb-10 font-36 font-600">
                <FormatNumberShow :data="huoquyue.rebate" :currency="true"/>
              </p>
              <p class="font-18" style="color: #999">{{ $t('累计收益') }}</p>
            </div>
          </div>
        </div>
        <div class="flex">
          <el-button type="primary" @click="rechargeEvent">
            {{ ['HIVE'].includes(settings.projectTitle) ? $t('加值') : $t('充值') }}
          </el-button>
          <el-button type="primary" @click="withdrawEvent">
            {{ ['HIVE'].includes(settings.projectTitle) ? $t('提领') : $t('提现') }}
          </el-button>
          <el-button type="primary" plain @click="intoPage" v-if="['HIVE'].includes(settings.projectTitle)">
            {{ $t('信贷服务') }}
          </el-button>
        </div>
      </div>
    </el-card>
    <el-carousel height="158px" style="margin-bottom: 12px" arrow="always"
                 v-if="userInfo&&userInfo.kyc_status == 2&&(inviteFriends&&inviteFriends.length>0||syspara&&syspara.length>0&&([0,1].indexOf(merchantInfo.rechargeBonusStatus)>=0))">
      <el-carousel-item v-if="userInfo&&userInfo.kyc_status == 2&&inviteFriends&&inviteFriends.length>0">
        <div class="swiper-slide">
          <div class="first-charge" @click="showInvitePop=true">
            <el-image style="width: 100%;height: 100%;" :src="inviteBg"
                      fit="cover" class="first-charge-image"></el-image>
            <div class="first-charge-content">
              <div class="first-charge-text">
                <div class="first-charge-title">
                  <span v-html="highlight($t('邀请好友开店 <span class=highlight>豪礼</span>相送'))"></span>
                </div>
                <div class="first-charge-desc">
            <span>
            {{
                $t("累计领取${_$1},可领取${_$2}", {
                  _$1: merchantInfo.inviteReceivedReward,
                  _$2: merchantInfo.inviteAmountReward
                })
              }}
            </span>
                </div>
              </div>
              <div class="first-charge-button">
                <el-button class="first-charge-btn" type="primary" @click.stop="getInviteReward"
                           v-if="merchantInfo.inviteAmountReward>0&&userInfo.kyc_status===2">
                  {{ $t('领取') }}
                </el-button>
                <el-button v-else class="first-charge-btn" type="primary" @click.stop="inviteFun">
                  {{ $t('邀请') }}
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-carousel-item>
      <el-carousel-item
          v-if="userInfo&&userInfo.kyc_status == 2&&syspara&&syspara.length>0&&([0,1].indexOf(merchantInfo.rechargeBonusStatus)>=0)">
        <div class="swiper-slide"
        >
          <div class="first-charge">
            <el-image style="width: 100%;height: 100%;" :src="require('@/assets/activity/first_charge.png')"
                      fit="cover" class="first-charge-image"></el-image>
            <div class="first-charge-content">
              <div class="first-charge-text">
                <div class="first-charge-title">
                  <span class="yellow">{{ $t('首充') }}</span>
                  <span>{{ $t('活动奖励') }}</span>
                </div>
                <div class="first-charge-desc">
            <span v-for="(item,index) in syspara" :key="index">
            {{ item.content }}{{ index !== syspara.length - 1 ? '，' : '' }}
            </span>
                </div>
              </div>
              <div class="first-charge-button">
                <el-button class="first-charge-btn" type="primary" @click="receiveBonus"
                           v-if="!showReceiveBtn&&merchantInfo.rechargeBonusStatus===1">{{ $t('领取') }}
                </el-button>
                <el-button class="first-charge-btn" type="primary" @click="rechargeEvent"
                           v-else-if="!showReceiveBtn&&merchantInfo.rechargeBonusStatus===0">{{ $t('去充值') }}
                </el-button>
                <el-button class="first-charge-btn" type="primary"
                           v-else-if="showReceiveBtn">{{ $t('已领取') }}
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-carousel-item>
    </el-carousel>
    <InviteFriends :showInvitePop="showInvitePop" @changeShowInvitePop="changeShowInvitePop"/>
    <el-card>
      <div class="flex py-15">
        <div :class="{'btn-active': type === 'recharge'}" class="button-item" @click="changeTab('recharge')">
          {{ ['HIVE'].includes(settings.projectTitle) ? $t('加值') : $t('充值') }}
        </div>
        <div :class="{'btn-active': type === 'withdraw'}" class="button-item" @click="changeTab('withdraw')">
          {{ ['HIVE'].includes(settings.projectTitle) ? $t('提领') : $t('提现') }}
        </div>
      </div>
      <!--  充值表格    -->
      <el-table :data="tableData" border class="text-center" style="width: 100%" v-if="type === 'recharge'">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column :label="$t('订单号')" prop="order_no">
        </el-table-column>
        <el-table-column :label="$t('充值数量')" prop="amount">
          <template slot-scope="{row}">
            <FormatNumberShow :data="row.volume" style="color:#67C23A" :decimalPlaces="6"/>
            <el-tag size="mini" :type="row.isThirdParty===1?'warning':''" style="margin-left: 6px">{{
                row.coin
              }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('币种协议')" prop="blockchain_name">
          <template slot-scope="{row}">
            <span v-if="row.blockchain_name">{{ row.blockchain_name }}</span>
            <span v-else>--</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('订单状态')" prop="state">
          <template slot-scope="{row}">
            <el-tag v-if="row.state==0" class="r1 chulizhi">{{
                $t('处理中')
              }}
            </el-tag>
            <el-tag v-if="row.state==1" type="success" class="r1 chenggong">{{
                $t('成功')
              }}
            </el-tag>
            <el-tag v-if="row.state==2" type="danger" class="r1 shibai">{{ $t('失败') }}</el-tag>
          </template>
        </el-table-column>
        <!--    点击查看按钮，弹窗展示支付凭证图片    -->
        <el-table-column :label="$t('支付/凭证')" prop="state">
          <template slot-scope="{row}">
            <template v-if="row.isThirdParty===1">
              <el-button size="mini" type="text" v-if="row.state===0" style="position: relative;"
                         @click="openPageWindow(row.payUrl)">{{ $t('继续支付') }}
              </el-button>
              <span v-else>--</span>
            </template>
            <el-button size="mini" type="text" v-else-if="row.img" style="position: relative;">{{ $t('查看') }}
              <el-image class="image-mini" :src="row.img" lazy :preview-src-list="[row.img]"
                        style="position: absolute;left: 0;top: 0;width: 100%;height: 100%;"></el-image>
            </el-button>
            <span v-else>--</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('实际到账')" prop="amount">
          <template slot-scope="{row}">
            <template v-if="row.state==1">
              <FormatNumberShow :data="(row.amount - row.fee)" style="color:#67C23A" :decimalPlaces="6"/>
              <el-tag size="mini" :type="row.isThirdParty===1?'warning':''" style="margin-left: 6px">USDT</el-tag>
            </template>
            <span v-else>--</span>
          </template>

        </el-table-column>
        <el-table-column :label="$t('到账地址')" prop="channel_address">
          <template slot-scope="{row}">
            <span v-if="row.channel_address">{{ row.channel_address }}</span>
            <span v-else>--</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('通过时间')" prop="reviewTime">
          <template slot-scope="{row}">
            <span>{{ row.reviewTime | formatZoneDate }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('创建时间')" prop="createTime">
          <template slot-scope="{row}">
            <span>{{ row.createTime |formatZoneDate }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('备注')" prop="failure_msg">
          <template slot-scope="{row}">
            <span>{{ row.failure_msg }}</span>
          </template>
        </el-table-column>
      </el-table>
      <!--  提现表格    -->
      <el-table :data="tableData" border class="text-center" style="width: 100%" v-if="type === 'withdraw'">
        <el-table-column type="selection" width="55">
        </el-table-column>
        <el-table-column :label="$t('订单号')" prop="order_no">
        </el-table-column>
        <el-table-column :label="$t('提现数量')" prop="amount">
          <template slot-scope="{row}">
            <FormatNumberShow :data="row.volume" style="color:#67C23A" :decimalPlaces="6"/>
            <el-tag size="mini" :type="row.isThirdParty===1?'warning':''" style="margin-left: 6px">{{
                row.coin
              }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('币种协议')" prop="coin_blockchain">
          <template slot-scope="{row}">
            <span v-if="row.coin_blockchain">{{ row.coin_blockchain }}</span>
            <span v-else>--</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('订单状态')" prop="state">
          <template slot-scope="{row}">
            <el-tag v-if="row.state==0" class="r1 chulizhi">{{
                $t('处理中')
              }}
            </el-tag>
            <el-tag v-if="row.state==1" type="success" class="r1 chenggong">{{
                $t('成功')
              }}
            </el-tag>
            <el-tag v-if="row.state==2" type="danger" class="r1 shibai">{{ $t('失败') }}</el-tag>
          </template>
        </el-table-column>
        <!--    手续费    -->
        <el-table-column :label="$t('手续费')" prop="fee">
          <template slot-scope="{row}">
            <FormatNumberShow :data="feeFunc(row.volume,row.amount)" style="color:#67C23A" :decimalPlaces="6"/>
            <el-tag size="mini" :type="row.isThirdParty===1?'warning':''" style="margin-left: 6px">{{
                row.coin
              }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('实际到账')" prop="amount">
          <template slot-scope="{row}">
            <template v-if="row.state==1">
              <FormatNumberShow :data="row.amount" style="color:#67C23A" :decimalPlaces="6"/>
              <el-tag size="mini" :type="row.isThirdParty===1?'warning':''" style="margin-left: 6px">{{
                  row.coin
                }}
              </el-tag>
            </template>
            <span v-else>--</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('创建时间')" prop="createTime">
          <template slot-scope="{row}">
            <span>{{ row.createTime | formatZoneDate }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('到账地址')" prop="to">
          <template slot-scope="{row}">
            <span>{{ row.to }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('备注')" prop="failure_msg">
          <template slot-scope="{row}">
            <span>{{ row.failure_msg }}</span>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 20px; text-align: center">
        <el-pagination
            :current-page.sync="pageNum"
            :page-size="pageSize"
            :total="totalElements"
            background
            layout="total, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
        </el-pagination>
      </div>
    </el-card>
    <PayModal v-model="payModalShow" :payCallback="payCallback" @changeShowModel="changeShowModel" :onlySetting="true"/>
    <!--    弹窗展示支付凭证图片-->
    <el-dialog :title="$t('支付凭证')" :visible.sync="dialogVisible" width="80%">
      <el-image fit="contain" :src="imgUrl" alt="" style="width: 100%;min-height: 350px;border:solid 1px #e3e3e3;">
        <div slot="error" class="image-slot">
          <i class="el-icon-picture-outline"></i>
        </div>
      </el-image>
    </el-dialog>
  </div>
</template>

<script>
import PayModal from '@/components/payModal/index.vue'
import SwitchRoles from './components/SwitchRoles'
import settings from "@/settings";
import InviteFriends from "@/views/permission/inviteFriends.vue";

import {
  beforeReceiveBonus,
  getRechargeRecord,
  getSyspara,
  getUserBalance,
  getWithdrawalRecords,
  receiveBonus,
  receiveInviteRewards,
  seller_info_action_post
} from "@/api/user";
import FormatNumberShow from "@/components/FormatNumberShow/index.vue";
import {mapGetters} from 'vuex'
import {getOrigin} from "@/utils/utis";
import openWindow from "@/utils/open-window";
import inviteBg from '@/assets/active/invite_bg.png'
import Toast from "@/utils/toast";

export default {
  name: 'PagePermission',
  data() {
    return {
      inviteBg,
      type: 'recharge',
      currentPage4: 0,
      tableData: [],
      nextPageNumber: 0,
      previousPageNumber: 0,
      lastPage: true,
      settings,
      huoquyue: {},
      payModalShow: false,
      pageNum: 1,
      pageSize: 10,
      totalElements: 0,
      dialogVisible: false,
      imgUrl: '',
      intoUrl: '',
      syspara: {},
      showReceiveBtn: false,
      showInvitePop: false,
      inviteFriends: [],
      currentSlide: 0, // 当前幻灯片索引
      slides: [], // 幻灯片数量，用于生成小圆点导航
    }
  },
  components: {FormatNumberShow, SwitchRoles, PayModal, InviteFriends},
  computed: {
    userInfo: () => this.$store.getters.userInfo,
    ...mapGetters(['merchantInfo', 'userInfo'])
  },
  watch: {
    $route(val) {
      if (val.path === '/wallet/index') {
        this.getUserBalance()
        this.getRechargeRecord()
      }
    }
  },
  created() {
    // getInfo().then(res => {
    //   this.$store.commit('user/CHANGE_USER_INFO', res)
    // })
    // window.addEventListener('storage', this.afterQRScan)
    this.getUserBalance()
    // this.getRechargeRecord()
    this.$route.query.type && (this.type = this.$route.query.type)
    this.changeTab(this.type)
    this.beforeReceiveBonus()
  },
  methods: {
    openWindow,
    changeShowInvitePop(val) {
      this.showInvitePop = val
    },
    getInviteReward() {
      receiveInviteRewards().then((res) => {
        Toast.success(this.$t('领取成功'))
      })
    },
    inviteFun() {
      if (this.userInfo.kyc_status !== 2) {
        this.$confirm(this.$t('您还没有通过商家认证，无法参与活动。'), this.$t('提示'), {
          confirmButtonText: this.$t('查看认证进度'),
          cancelButtonText: this.$t('取消'),
          type: 'warning'
        }).then(() => {
          localStorage.setItem("show_kyc", 1)
          this.$router.push('/other/shopSetting')
        })
      } else {
        this.showInvitePop = true
      }
    },
    highlight(text) {
      return text.replace(/<span class="highlight">(.*?)<\/span>/g, "<span class='highlight'>$1</span>");
    },
    goToSlide(index) {
      // 点击小圆点导航时跳转到对应的幻灯片
      this.currentSlide = index;
    },
    feeFunc(a, b) {
      return this.$bigDecimal.subtract(a, b)
    },
    openPageWindow(url) {
      //打开新窗口，不显示地址栏
      window.open(url);
    },
    intoPage() {
      //打开新窗口，不显示地址栏
      window.open(getOrigin() + "/#/credit?storeId=" + this.$store.getters.merchantInfo.id + '&lang=' + this.$store.getters.lang);
    },
    receiveBonus() {
      receiveBonus({sellerId: this.merchantInfo.id}).then(res => {
        this.$message.success(this.$t('领取成功'))
        //展示已领取按钮
        this.showReceiveBtn = true
        this.getUserBalance()
      })
    },
    beforeReceiveBonus() {
      beforeReceiveBonus().then(res => {
        this.seller_info_action()
      })
    },
    seller_info_action() {
      seller_info_action_post({}).then((res) => {
        this.$store.commit('user/CHANGE_MERCHANT_INFO', res.data)
        this.getSyspara()
      })
    },
    getSyspara() {
      getSyspara({code: 'mall_first_recharge_rewards,mall_first_invite_recharge_rewards'}).then(res => {
        this.syspara = res.data.mall_first_recharge_rewards ? JSON.parse(res.data.mall_first_recharge_rewards) : [] //[[100,10]]//
        this.merchantInfo.rechargeBonusStatus = 1
        this.syspara.forEach(item => {
          item.content = this.$t("存{_$1}赠送{_$2}", {_$1: item[1], _$2: item[0]})
        })

        this.inviteFriends = res.data.mall_first_invite_recharge_rewards ? JSON.parse(res.data.mall_first_invite_recharge_rewards) : []
        if (this.userInfo.kyc_status === 2) { //是否认证
          if (this.syspara && this.syspara.length > 0 && ([0, 1].indexOf(this.merchantInfo.rechargeBonusStatus) >= 0)) {
            this.slides.push(this.slides.length)
          }
          if (this.inviteFriends && this.inviteFriends.length > 0) {
            this.slides.push(this.slides.length)
          }
        }
        if (this.slides.length > 1) {
          setInterval(this.nextSlide, 5000)
        }
      })
    },
    nextSlide() {
      // 切换到下一张幻灯片，如果当前是最后一张，则回到第一张
      this.currentSlide = (this.currentSlide + 1) % this.slides.length;
    },
    lookImg(url) {
      this.dialogVisible = true
      this.imgUrl = url
    },
    fenye(x) {
      if (x == 'a') {
        this.pageNum++
      }
      if (x == 'b') {
        console.log(this.pageNum)
        // if (this.pageNum=='1'){
        //   return
        // }
        this.pageNum--
      }
      // this.getAllData()
      if (this.type == 'recharge') {
        this.getRechargeRecord()
      } else {
        this.getWithdrawalRecords()
      }
    },
    handleSizeChange(val) {
      console.log(`每页 ${val} 条`);
      this.pageSize = val
      if (this.type === 'recharge') {
        this.getRechargeRecord()
      } else {
        this.getWithdrawalRecords()
      }

    },
    // TODO: 当前第几页,去请求获取数据
    handleCurrentChange(val) {
      console.log(`当前页: ${val}`);
      this.pageNum = val
      if (this.type === 'recharge') {
        this.getRechargeRecord()
      } else {
        this.getWithdrawalRecords()
      }
    },
    changeShowModel(type) {
      if (type === 'success') {
        this.$notify({
          title: this.$t('成功'),
          message: this.$t('设置成功'),
          type: 'success'
        });
      }
      this.payModalShow = !this.payModalShow
    },
    payCallback() {
      this.payModalShow = false
      this.getUserBalance()
      this.getRechargeRecord()
      if (this.intoUrl) {
        this.$router.push(this.intoUrl)
      }
    },
    rechargeEvent() {
      if (this.userInfo?.kyc_status == 2) {
        if (this.$store.getters.userInfo.safeword === 0) {
          this.settingSafeWord()
          this.intoUrl = '/wallet/Recharge'
        } else {
          this.$router.push('/wallet/Recharge')
        }
      } else {
        this.$confirm(this.$t('您还没有通过商家认证，无法参与活动。'), this.$t('提示'), {
          confirmButtonText: this.$t('查看认证进度'),
          cancelButtonText: this.$t('取消'),
          type: 'warning'
        }).then(() => {
          localStorage.setItem("show_kyc", 1)
          this.$router.push('/other/shopSetting')
        }).catch(() => {
        });
      }
    },
    withdrawEvent() {
      if (this.$store.getters.userInfo.safeword === 0) {
        this.settingSafeWord()
        this.intoUrl = '/wallet/withdraw'
      } else {
        this.$router.push('/wallet/withdraw')
      }
    },
    settingSafeWord() {
      this.payModalShow = true
      this.$nextTick(() => {
        setTimeout(() => {
          this.$notify({
            message: this.$t('请先设置支付密码'),
            type: 'warning'
          })
        }, 100)
      })
    },
    getRechargeRecord() {
      const params = {
        page_no: this.pageNum,
        pageSize: this.pageSize
      }
      getRechargeRecord(params).then((e) => {
        this.tableData = e.data.elements;
        this.previousPageNumber = e.data.previousPageNumber;
        this.nextPageNumber = e.data.nextPageNumber;
        this.lastPage = e.data.lastPage;
        this.pageNum = e.data.nextPageNumber - 1
        this.pageSize = e.data.pageSize
        this.totalElements = e.data.totalElements
      })
    },
    getWithdrawalRecords() {
      const params = {
        page_no: this.pageNum,
        pageSize: this.pageSize
      }
      getWithdrawalRecords(params).then((e) => {
        console.log(e)
        // this.tableData = e.data
        this.tableData = e.data.elements;
        this.previousPageNumber = e.data.previousPageNumber;
        this.nextPageNumber = e.data.nextPageNumber;
        this.lastPage = e.data.lastPage;
        this.pageNum = e.data.nextPageNumber - 1
        this.pageSize = e.data.pageSize
        this.totalElements = e.data.totalElements
      })
    },
    changeTab(e) {
      this.type = e
      this.pageNum = 1
      if (this.type == 'recharge') {
        this.getRechargeRecord()
      } else {
        this.getWithdrawalRecords()
      }
    },
    getUserBalance() {
      getUserBalance({}).then((e) => {
        console.log(e)
        this.huoquyue = e.data
      })
    },
    handleRolesChange() {
      this.$router.push({path: '/permission/index?' + +new Date()})
    },
    fullColor(text) {
      if (text === '处理中') return '#F99746'
      if (text === '成功') return '#0ECB81'
      if (text === '失败') return '#E23939'
    }
  }
}
</script>

<style lang="scss" scoped>
.swiper-container {
  width: 100%;
  overflow: hidden;
}

.swiper-wrapper {
  display: flex;
  transition: transform 0.3s ease; /* 切换效果 */
}

.swiper-slide {
  flex: 0 0 100%; /* 幻灯片宽度 */
  box-sizing: border-box;
  text-align: center;
}

.swiper-pagination {
  text-align: center;
  margin-bottom: 12px;
}

.swiper-pagination-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  background-color: #ccc;
  border-radius: 50%;
  margin: 0 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.swiper-pagination-dot.active {
  background-color: #f00; /* 高亮显示当前页的颜色 */
}

.first-charge {
  margin-bottom: 12px;
  border-radius: 4px;
  overflow: hidden;
  height: 158px;
  width: 100%;
  position: relative;

  .first-charge-content {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    color: #fff;
    padding: 12px 50px 12px 12px;
    box-sizing: border-box;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .first-charge-text {
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;
      flex: 1;
      width: 100%;
      padding: 0 50px;

      .first-charge-title {
        font-family: 'Roboto';
        font-style: normal;
        font-weight: 700;
        font-size: 32px;
        line-height: 38px;
        /* identical to box height */
        text-align: center;
        margin-bottom: 18px;

        .yellow {
          color: #FECC1C;
        }
      }

      .first-charge-desc {
        font-family: 'Roboto';
        font-style: normal;
        font-weight: 400;
        font-size: 32px;
        line-height: 32px;
        /* identical to box height */
        color: #FFFFFF;
        text-align: center;
      }
    }

    .first-charge-btn {
      width: 100%;
      height: 40px;
      text-align: center;
      border-radius: 40px;
      background: #fff;
      color: #1552f0;
      min-width: 150px;
      font-family: 'Roboto';
      font-style: normal;
      font-weight: 700;
      font-size: 20px;
      border: none;
    }

    .first-charge-image {
      position: absolute;
      top: 0;
      left: 0;
    }
  }
}


::v-deep .image-mini {
  .el-image__inner {
    opacity: 0;
  }
}

.permission-icon {
  width: 86px;
  height: 86px;
  margin: 12px auto;
}

.button-item {
  cursor: pointer;
}

.border-item {
  border-style: solid;
  border-width: 1px;
  border-color: transparent;
}

.active {
  border-color: #1552f0;
  background: #fff !important;
  color: #1552f0;
}

.app-container {
  height: 100%;
  background: rgb(236, 239, 242);
}

::v-deep {
  .el-table__header, .el-table__body {
    width: 100% !important;
  }

  .cell {
    //margin: 0 20px;
    padding: 0;
    font-size: 14px;
    text-align: center;
  }

  .el-carousel__arrow {
    background: rgba(0, 0, 0, 0.5);
    font-size: 16px;
    font-weight: bold;
    box-shadow: 0 0 4px rgba(255, 255, 255, 0.5);

    &:hover {
      background: rgba(0, 0, 0, 0.7);
    }
  }
}

</style>
