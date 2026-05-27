<template>
  <div class="merchandise">
    <el-card>
      <el-form ref="destroyAccountForm" :model="destroyAccountForm" style="width: 600px" label-position="top"
               :rules="rules">
        <el-form-item :label="$t('账号')" prop="account">
          <el-input v-model="destroyAccountForm.account" disabled></el-input>
        </el-form-item>
        <el-form-item :label="$t('原因')" prop="reason">
          <el-input maxlength="200" v-model="destroyAccountForm.reason" type="textarea"
                    :placeholder="$t('请输入注销原因')"></el-input>
          <div class="introduce">
            {{ $t("最多200字") }}
          </div>
        </el-form-item>
        <el-form-item>
          <el-button style="width: 100%" type="danger" @click="destroyAccount">{{ $t('注销账号') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <PayModal v-model="payModalShow" :payCallback="payCallback" @changeShowModel="changeShowModel"/>
  </div>
</template>

<script>
import {mapGetters} from "vuex";
import {destroyAccount, getUserBalance} from "@/api/user";
import {Notification} from "element-ui";
import {i18n} from "@/lang";
import PayModal from '@/components/payModal'
import {removeToken} from "@/utils/auth";

export default {
  name: "destroyAccount",
  components: {PayModal},
  data() {
    return {
      payModalShow: false,
      destroyAccountForm: {
        account: "",
        //原因
        reason: "",
      },
      rules: {
        account: [
          {required: true, message: '', trigger: 'blur'},
        ],
        reason: [
          {required: true, message: this.$t('请输入注销原因'), trigger: 'blur'},
        ],
      },
    };
  },
  computed: {
    ...mapGetters(['userInfo']),
    columnWidth() {
      let width = 120;
      switch (this.$i18n.locale) {
        case 'en':
          width = 180;
          break;
        case 'cn':
          width = 90;
          break;
        case 'tw':
          width = 90;
          break;
        case 'de':
          width = 160;
          break;
        case 'fr':
          width = 200;
          break;
        case 'ja':
          width = 160;
          break;
        case 'ko':
          width = 170;
          break;
        case 'ms':
          width = 180;
          break;
        case 'th':
          width = 160;
          break;
        case 'pt':
          width = 180;
          break;
        case 'es':
          width = 220;
          break;
        case 'ru':
          width = 220;
          break;
        case 'el':
          width = 220;
          break;
        case 'it':
          width = 180;
          break;
        case 'tr':
          width = 180;
          break;
        case 'af':
          width = 180;
          break;
        case 'ph':
          width = 180;
          break;
        case 'ar':
          width = 160;
          break;
        case 'vi':
          width = 250;
          break;
        case 'id':
          width = 250;
          break;
        case 'hi':
          width = 180;
          break;
      }
      return width + 'px';
    },
  },
  mounted() {
    this.destroyAccountForm.account = this.userInfo.username;
  },
  methods: {
    changeShowModel(e) {
      this.payModalShow = e
    },
    payCallback(cashPassword) {
      const params = {
        account: this.destroyAccountForm.account,
        reason: this.destroyAccountForm.reason,
        cashPassword,
      };
      destroyAccount(params).then((res) => {
        Notification.success({
          title: i18n.t('成功'),
          message: i18n.t('注销账号成功！'),
        });
        this.logout();
      }).catch((err) => {
        this.payModalShow = false;
      })
    },
    destroyAccount() {
      this.$refs.destroyAccountForm.validate(async (valid) => {
        if (valid) {
          const balance = await this.getUserBalance();
          if (balance > 0) {
            Notification.error({
              title: i18n.t('错误'),
              message: i18n.t('该账号存在可用余额，不可注销！'),
            });

          } else {
            this.$confirm(i18n.t('警告！请谨慎操作注销账户，如果您不再使用该账号，可点击【同意注销】，注销后可能几天内无法注册。'), i18n.t('您确认要注销吗？'), {
              confirmButtonText: i18n.t('同意注销'),
              cancelButtonText: i18n.t('取消'),
              type: 'warning'
            }).then(() => {
              this.payModalShow = true;
            })
          }
        } else {
          return false;
        }
      });

    },
    //查询余额
    getUserBalance() {
      return new Promise((resolve, reject) => {
        getUserBalance().then((res) => {
          resolve(res.data.money || 0);
        }).catch((err) => {
          reject(err);
        })
      });
    },
    // 退出登录
    async logout() {
      // await this.$store.dispatch("user/logout");
      this.$store.commit('chat/DELETE_CHAT_INTERVAL')
      this.$store.commit('chat/DELETE_MASSAGE_INTERVAL')
      removeToken()
      this.$router.push(`/login?redirect=${this.$route.fullPath}`);
    },
  }
}
</script>

<style scoped lang="scss">
.introduce {
  font-size: 12px;
}

.merchandise {
  background-color: #f0f2f5;
  padding: 20px;
}

</style>
