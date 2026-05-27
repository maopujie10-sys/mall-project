<template>
  <div class="merchandise">
    <SetBootSteps/>
    <el-card class="main">
      <div class="seller-level-content">
        <div class="left">
          <el-image :src="sellerLevelImage" style="width: 312px;height: 348px;"/>
        </div>
        <div class="right">
          <div class="title">
            {{ $t('升级') }}<b>{{ $t('销量扶持') }}</b>
            &nbsp;&nbsp;{{ $t('轻松') }}<b>{{ $t('月入过万') }}</b>
          </div>
          <div style="display: flex;justify-content: flex-start;">
            <div style="color: #333333;font-size: 20px;margin-right: 24px;" v-if="merchantInfo.childNum">
              {{ $t('当前分店人数：') }}{{ merchantInfo.childNum || 0 }}
            </div>
            <div style="color: #333333;font-size: 20px" v-if="merchantInfo.teamNum">
              {{ $t('当前团队人数：') }}{{ merchantInfo.teamNum || 0 }}
            </div>
          </div>
          <div>
            <div>1.{{ $t('卖家等级介绍') }}</div>
            <span>
            {{
                $t('平台为鼓励广大创业者，为创业者提供更大的商业机会，让您与我与我们一同成长，助您在销售中获得更大的成功，创业过程中为您准备了丰厚的升级奖励和销售利润比例提升，无论您是新手还是经验丰富的销售员，我们都鼓励您参与升级计划，并诚挚的邀请您加入我们，实现您的销售梦想！')
              }}
            </span>
          </div>
          <div>
            <div>2.{{ $t('会员升级说明') }}</div>
            <span>
              <b>{{ $t('会员升级') }}：</b>
              {{
                ["Shop2U"].includes(defaultSettings.projectTitle) ? $t('会员升级是通过直属推分店数决会员级别，分店数越高，系统将自动升级。') : $t('会员升级是通过直属推分店数决会员级别，分店数越高或运行资金满足条件，系统将自动升级。')
              }}
            </span>
            <br/>
            <span>
            <b>{{ $t('分店人数') }}：</b>{{
                $t("直属下级中，累计充值金额超过{_$1}将视为有效人数", {_$1: '$' + (limitRechargeAmount * 1).toFloor(2)})
              }}
            </span><br/>
            <span>
            <b>{{ $t('团队人数') }}：</b>{{
                $t("所有下级中，累计充值金额超过{_$1}视为有效团队人数", {_$1: '$' + (teamRechargeAmount * 1).toFloor(2)})
              }}
            </span><br/>
            <span>
            <b>{{ $t('销售利润比例') }}：</b>{{ $t('等级越高，获得销售利润越高') }}
            </span><br/>
            <span>
            <b>{{ $t('平台流量扶持') }}：</b>{{ $t('系统将优先为您提供一定商品流量曝光，创造更多的销售机会') }}
            </span><br/>
            <span v-if="!['Inchoi'].includes(defaultSettings.projectTitle)">
            <b>{{ $t('升级礼金') }}：</b>{{ $t('每升级成功，系统将自动发放升级礼金') }}
            </span>
          </div>
          <div>
            <div>3.{{ $t('成长规则') }}</div>
            <span>
            {{ $t('会员等级从升级那一刻开始计算，等级身份将终生有效；') }}
            </span>
          </div>
        </div>
      </div>
    </el-card>
    <el-card>
      <el-table :data="sellerLevelList" style="width: 100%">
        <el-table-column prop="level" :label="$t('卖家等级')" align="center">
          <template slot-scope="scope">
            <div style="display: flex;justify-content: center;align-items: center;">
              <el-image :src="getLevelIcon(scope.row.level)" style="height: 20px;margin-right: 6px;"/>
              <span style="line-height: 20px;">{{ scope.row.level }}&nbsp;{{ $t('级') }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column v-if="!['Shop2U'].includes(defaultSettings.projectTitle)" prop="rechargeAmountCnd"
                         :label="$t('运行资金')" align="center"></el-table-column>
        <el-table-column prop="popularizeUserCountCnd" :label="$t('分店数')" align="center"></el-table-column>
        <el-table-column prop="recommendAtFirstPage" :label="$t('团队人数')" align="center" v-if="showTeamNum">
          <template slot-scope="scope">
            <span>{{ scope.row.teamNum }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="profitRationMin" :label="$t('销售利润比')" align="center">
          <template slot-scope="scope">
            <span>{{
                (scope.row.profitRationMin * 100).toFloor(2)
              }}%</span>-<span>{{ (scope.row.profitRationMax * 100).toFloor(2) }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="promoteViewDaily" :label="$t('平台流量扶持量（每日）')" align="center"></el-table-column>
        <el-table-column prop="deliveryDays" :label="$t('全球到货时间')" align="center"></el-table-column>
        <el-table-column prop="sellerDiscount" :label="$t('采购优惠')" align="center">
          <template slot-scope="scope">
            <span>{{ (scope.row.sellerDiscount * 100).toFloor(2) }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="upgradeCash" :label="$t('升级礼金')" align="center"
                         v-if="!['Inchoi'].includes(defaultSettings.projectTitle)">
          <template slot-scope="scope">
           <span v-if="scope.row.upgradeCash">
              <FormatNumberShow :data="scope.row.upgradeCash" :currency="true"/>
            </span>
            <span v-else>
              <el-image :src="e" style="height: 14px;"/>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="hasExclusiveService" :label="$t('专属服务')" align="center">
          <template slot-scope="scope">
            <span v-if="scope.row.hasExclusiveService">
              <el-image :src="r" style="height: 14px;"/>
            </span>
            <span v-else>
              <el-image :src="e" style="height: 14px;"/>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="recommendAtFirstPage" :label="$t('首页推荐')" align="center">
          <template slot-scope="scope">
            <span v-if="scope.row.recommendAtFirstPage">
              <el-image :src="r" style="height: 14px;"/>
            </span>
            <span v-else>
              <el-image :src="e" style="height: 14px;"/>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="recommendAtFirstPage" :label="$t('成为供货商')" align="center"
                         v-if="['FamilyShop'].includes(defaultSettings.projectTitle)">
          <template slot-scope="scope">
            <span v-if="scope.row.level==='SS'">
              <el-image :src="r" style="height: 14px;"/>
            </span>
            <span v-else>
              <el-image :src="e" style="height: 14px;"/>
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import sellerLevelImage from '@/assets/seller-level-image.png'
import {getSellerLevelList, getSysParaService} from "@/api/user";
import levela from '@/assets/level/a.png'
import levelb from '@/assets/level/b.png'
import levelc from '@/assets/level/c.png'
import levelo from '@/assets/level/o.png'
import levels from '@/assets/level/s.png'
import levelss from '@/assets/level/ss.png'
import levelsss from '@/assets/level/sss.png'
import e from '@/assets/level/e.png'
import r from '@/assets/level/r.png'
import FormatNumberShow from "@/components/FormatNumberShow/index.vue";
import defaultSettings from "@/settings";
import {mapGetters} from "vuex";

export default {
  name: 'SellerLevel',
  components: {FormatNumberShow},
  data() {
    return {
      defaultSettings,
      sellerLevelImage,
      sellerLevelList: [],
      showTeamNum: false,
      levela,
      levelb,
      levelc,
      levelo,
      levels,
      levelss,
      levelsss,
      e,
      r,
      limitRechargeAmount: 0,
      teamRechargeAmount: 0
    }
  },
  mounted() {
    this.getSellerLevelList()
    this.getSysPara()
  },
  computed: {
    ...mapGetters(['merchantInfo']),
  },
  methods: {
    getLevelIcon(level) {
      switch (level) {
        case 'A':
          return this.levela
        case 'B':
          return this.levelb
        case 'C':
          return this.levelc
        case 'O':
          return this.levelo
        case 'S':
          return this.levels
        case 'SS':
          return this.levelss
        case 'SSS':
          return this.levelsss
        default:
          return this.levelo
      }
    },
    getSellerLevelList() {
      getSellerLevelList().then(res => {
        this.sellerLevelList = res.data.result
        this.showTeamNum = !!this.sellerLevelList.find(item => item.teamNum > 0)
        if (['Shop2U'].includes(defaultSettings.projectTitle)) {
          //upgradeCash 写死
          this.sellerLevelList.forEach(item => {
            item.upgradeCash = this.webShowUpgradeCash(item.level)
          })
        }
      })
    },
    webShowUpgradeCash(level) {
      switch (level) {
        case 'A':
          return 700
        case 'B':
          return 500
        case 'C':
          return 100
        case 'O':
          return 0
        case 'S':
          return 1000
        case 'SS':
          return 1500
        case 'SSS':
          return 2000
        default:
          return 0
      }
    },
    getSysPara() {
      getSysParaService({code: 'valid_recharge_amount_for_seller_upgrade,valid_recharge_amount_for_team_num'}).then(res => {
        this.limitRechargeAmount = res.data.valid_recharge_amount_for_seller_upgrade
        this.teamRechargeAmount = res.data.valid_recharge_amount_for_team_num
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.merchandise {
  background-color: #f0f2f5;
  padding: 20px;
  height: 100%;

  .main {
    height: 100%;
    padding: 20px;
    background-color: #fff;
    text-align: center;

    .prize {
      width: 224px;
      text-align: left;
      margin-left: 60px;
      font-weight: bold;
      margin-bottom: 20px;
    }

    .main-l {
      display: grid;
      grid-template-columns: repeat(3, 313px);
      column-gap: 2%;
      row-gap: 3%;
      justify-content: center;
      margin-bottom: 30px;

      .main-b {
        box-sizing: border-box;
        color: #666666;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        text-align: center;

        p {
          font-size: 14px;
          margin-bottom: 10px;
        }

        .title {
          width: 100%;
          font-weight: bold;
          font-size: 18px;
          margin: 25px 0 15px;
          text-align: center;
        }
      }
    }
  }

  .six-digit-wrapper {
    width: 100%;
    display: flex;
    justify-content: center;
    flex-direction: row;
    margin-top: 30px;

    .input {
      display: flex;
      width: 35px;
      margin-left: 10px;
      height: 44px;
      font-size: 18px;
      color: #333333;
      background-color: #f2f2f2;
      text-align: center;
      outline: none; // 去除选中状态边框
      border: solid 1px #d2d2d2;
      border-top: 0px;
      border-left: 0px;
      border-right: 0px;
    }
  }

  .wrapper {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
  }
}

.seller-level-content {
  display: flex;
  justify-content: flex-start;

  .left {
    position: relative;

    .image-content {
      position: absolute;
      left: 0;
      top: 0;
      font-family: 'Roboto';
      font-style: normal;
      font-weight: 700;
      font-size: 36px;
      line-height: 133.69%;
      color: #FFFFFF;
      display: flex;
      justify-content: center;
      flex-direction: column;
      width: 100%;
      padding-top: 24px;

      span {
        color: #FFCD21;
      }
    }
  }

  .right {
    padding: 0 0 0 25px;
    box-sizing: border-box;

    .title {
      font-family: 'Roboto';
      font-style: normal;
      font-weight: 700;
      font-size: 24px;
      line-height: 133.69%;
      color: #333333;

      > b {
        color: #1552F0;
        font-family: 'Roboto';
        font-style: normal;
        font-weight: 700;
        font-size: 24px;
        line-height: 133.69%;
      }
    }

    > div {
      text-align: left;
      margin-bottom: 12px;

      > div {
        margin-bottom: 12px;
        font-family: 'Roboto';
        font-style: normal;
        font-weight: 600;
        font-size: 14px;
        line-height: 16px;

        color: #1552F0;
      }

      > span {
        font-family: 'Roboto';
        font-style: normal;
        font-weight: 400;
        font-size: 14px;
        line-height: 19px;

        color: #333333;

        b {
          font-family: 'Roboto';
          font-style: normal;
          font-weight: 600;
          font-size: 14px;
          line-height: 16px;

          color: #333333;
        }

        &:nth-child(1) {
          font-size: 18px;
          font-weight: bold;
          margin-right: 20px;

        }
      }
    }
  }
}
</style>
