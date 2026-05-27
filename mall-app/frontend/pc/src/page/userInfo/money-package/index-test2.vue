<template>

  <div class="money_pacakge_contaner" v-loading="loading">
    <div class="top">
      <div class="title">
        {{ $t('message.home.accountReview') /** 账户总览 */ }}
      </div>
      <div class="content">
        <div style="display:  flex; flex-direction: row;">
          <div class="package_icon">
            <img :src="require('@/assets/image/img_cards.png')" style="height: 36px;width: 36px; " />
          </div>
          <div style="display: flex;flex-direction: column;justify-content: center;">
            <div style="display: flex;flex-direction: row; align-items: center;">
              <span style="font-weight: 700;font-size: 24px;margin-right: 14px;">{{
                moneyEyeOpen? numberFormat(userBalance): "*******"
              }} </span>
              <img @click="() => moneyEyeOpen = !moneyEyeOpen" style="width: 20px;height: 14px; cursor: pointer;"
                :src="require(`@/assets/image/eye-${moneyEyeOpen ? 'open' : 'close'}.png`)" />
            </div>
            <div style="font-weight: 400;font-size: 14px;margin-top: 10px;">{{
              $t('message.home.accountBalance')
              /**账户余额*/
            }} (USDT)</div>
          </div>
        </div>

        <div class="fl_row">
          <el-button @click="e => handelTo(e, 'recharge')" class="button" type="primary">
            {{ $t('message.home.recharge') }}
          </el-button>
          <el-button @click="e => handelTo(e, 'withdraw')" class="button" type="primary" plain>
            {{ $t('message.home.withdraw') }}
          </el-button>
        </div>
      </div>
    </div>

    <div class="fl_col">
      <span>钱包历史</span>
      <div class="fl_row" style="margin-top: 10px;">
        <el-button @click="() => pageInfo.type = 1" class="h_button" :type="pageInfo.type == 1 ? 'primary' : 'info'"
          :plain="pageInfo.type == 2">
          充值
        </el-button>
        <el-button @click="() => pageInfo.type = 2" class="h_button" :type="pageInfo.type == 2 ? 'primary' : 'info'"
          :plain="pageInfo.type == 1">
          提现
        </el-button>
      </div>

      <div class="table_style">
        <RenderTable style="font-size: 10px;"
          :header-cell-style="{ fontWeight: 600, fontSize: '12px', color: '#333333' }" :columns="columns"
          :data="tableData.elements || []"></RenderTable>
      </div>
      <div style="margin-top: 40px; display: flex;width: 100%;  justify-content: center;">
        <el-pagination background layout="prev, pager,next" class="es-pagination"
          :page-size="rechargeRecordList.pageSize" :pager-count="5" :current-page="rechargeRecordList.thisPageNumber"
          :total="rechargeRecordList.totalElements" @current-change="changePage" />
      </div>
    </div>

    <el-dialog :visible.sync="preViewDialog">
      <img width="100%" :src="preViewUrl" alt="">
    </el-dialog>

  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { numberFormat } from '@/util'
import RenderTable from '@/components/RenderTable'
import SpanTenPix from './widget/SpanTenPix.vue'
export default {
  components: {
    RenderTable,
  },

  data() {
    return {
      pageInfo: {
        type: 1,
        pageNum: 1,
        pageSize: 6,
      },
      label:'12122',
      columns: [
        {
          prop: "createTime",
          label: "日期",
          render: (_, { row }) => <SpanTenPix text={row.createTime} />,
          align: 'center',
          width: 135
        }, {
          prop: 'volume',
          label: this.labelVolume /**订单号 */,
          render: (_, { row }) => <SpanTenPix text={row.volume} />,
          align: 'center',
        }
      ],

      moneyEyeOpen: false,
      // tableData: [],

      loading: true,
      preViewDialog: false,
      preViewUrl: ''
    }
  },
  watch: {

  },
  computed: {
    ...mapGetters('user', ['userBalance']),
    ...mapGetters('recharge', ['rechargeRecordList']),
    ...mapGetters("withdraw", ["withdrawRecordList"]),
    tableData() {
      if (this.pageInfo.type == 1) {
        return this.rechargeRecordList
      } else {
        return this.withdrawRecordList
      }
    },
    labelVolume(){
       if(this.pageInfo.type==1){
        return '12'
       }else {
         return '13'
       }
    }
  },
  async mounted() {
    try {
      await Promise.all([this.requestGetUserBalanceList(),
      this.requestRechargeRecordList(),
      this.requestwithdrawRecordList(),
      ])
    } finally {
      this.loading = false
    }
  },
  methods: {
    ...mapActions('user', ['requestGetUserBalanceList']),
    ...mapActions('recharge', ['requestRechargeRecordList']),
    ...mapActions("withdraw", ["requestwithdrawRecordList"]),
    numberFormat,
    handelTo(e, type) {
      e.target.blur();
      this.$router.push({ name: `money-package-${type}` })
    },

    getRechargeWithdrawLabel() {
      console.log(this)
      return this.pageInfo.type == 1 ? '充值数量' : '提现数量'
    },


    changePage(pageNum) {
      console.log(pageNum)
    },
    handlePreview(url) {
      this.preViewDialog = true;
      this.preViewUrl = url;
    }
  },
}

</script>

<style scoped lang="scss">
/deep/.el-table--scrollable-y ::-webkit-scrollbar {
  display: none;
}

.money_pacakge_contaner {



  display: flex;
  flex-direction: column;

  .fl_row {
    display: flex;
    flex-direction: row;

  }



  .fl_col {
    display: flex;
    flex-direction: column;
    padding-top: 24px;
    padding-left: 34px;
  }


  .h_button {
    height: 30px;
    width: 93px;
    display: flex;
    justify-content: center;
    align-items: center;

    .info {
      background: #EEEEEE;
      border: none;
    }
  }

  .table_style {
    width: 863px;
    height: 422px;
    border: 1px solid #EEEEEE;
    border-radius: 4px;
    margin-top: 20px;
  }




  .top {
    display: flex;
    flex-direction: column;
    width: 863px;
    height: 185px;
    border-bottom: 1px solid #EEEEEE;
    padding-top: 24px;
    padding-left: 34px;

    .title {
      font-weight: 500;
      font-size: 14px;
    }

    .content {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
      margin-top: 50px;

      .button {
        width: 127px;
        height: 34px;
        display: flex;
        justify-content: center;
        align-items: center;

      }

      .package_icon {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 56px;
        height: 56px;
        border-radius: 28px;
        border: 1px solid var(--color-main);
        background: linear-gradient(0deg, #FFF7EC, #FFF7EC), #EEEEEE;
        margin-right: 17px;
      }
    }
  }
}
</style>