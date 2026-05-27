<template>
  <div class="merchandise">
    <SetBootSteps/>
    <el-card class="main">
      <h1 style="font-size: 30px; margin: 60px 0 120px">{{ $t('店铺升级套餐列表') }}</h1>
      <div class="main-l">
        <el-card v-for="(item, index) in data" :key="index" class="main-b">
          <img :src="item.icon" alt="" style="width: 72px; height: 72px"/>
          <p class="title">{{ item.name }}</p>
          <p>{{ $t('可推广产品数') }}
            <span style="margin-left: 6px;font-weight: 600;color: #2C78F8;">{{ item.count }}</span>
          </p>
          <div style="text-align: center">
            <p>{{ item.desc1 }}</p>
          </div>
          <div class="prize">
            <span style="font-size: 28px; color: #d9001b">${{ item.prize }} /
            </span>
            <span style="font-size: 18px; color: #aaa">{{ item.per }}</span>
            <span style="font-size: 18px; color: #aaa">{{ $t('日') }}</span>
          </div>
          <el-button type="primary" @click="rechargeEvent(item.id)">{{ $t('购买套餐') }}</el-button>
        </el-card>
      </div>
    </el-card>
    <PayModal v-model="payModalShow" :payCallback="payCallback"/>

  </div>
</template>

<script>
import {zhitongche_goumai_post, zhitongche_post} from "@/api/user";
import PayModal from '@/components/payModal'
import {Notification} from 'element-ui'

export default {
  name: "car",
  data() {
    return {
      data: {},
      payModalShow: false,
      show: false,
      id: ''
    };
  },
  components: {PayModal},
  mounted() {
    this.zhitongche_post_edit();
  },
  methods: {
    rechargeEvent(e) {
      this.id = e
      if (this.$store.getters.userInfo.safeword === 0) {
        this.settingSafeWord()
      } else {
        this.payModalShow = true
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
    payCallback(password) {
      this.zhitongche_goumai(password)
    },
    onInput(index) {
      // index < 5 ，如果是第6格，不触发光标移动至下一个输入框。
      if (this.digits[index].value && index < 5) {
        this.$refs["ref" + (index + 1)][0].focus();
      }
    },
    onDelete(index) {
      // 如果是第1格，不触发光标移动至上一个输入框
      if (index > 0) {
        this.$refs["ref" + (index - 1)][0].focus();
      }
    },
    zhitongche_post_edit() {
      zhitongche_post()
          .then((res) => {
            this.data = res.data.line;
          })
          .catch(function (err) {
          });
    },
    zhitongche_goumai(password) {
      zhitongche_goumai_post({id: this.id, safeword: password}).then((res) => {
        this.payModalShow = false
        Notification({
          title: this.$t('成功'),
          message: this.$t('购买成功'),
          type: 'success'
        })
      }).catch((err) => {
        this.payModalShow = false;
      });
    },
  },
};
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
</style>
