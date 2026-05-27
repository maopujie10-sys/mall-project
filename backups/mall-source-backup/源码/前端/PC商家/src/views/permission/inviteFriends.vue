<script>
import inviteBg from '@/assets/active/invite_bg.png'
import invitePop from '@/assets/active/invite_pop.png'
import clipboard from "@/directive/clipboard";
import {getSyspara, promotional_post, receiveInviteBonus, seller_info_action_post} from "@/api/user";
import {mapGetters} from "vuex";

export default {
  name: "InviteFriends",
  data() {
    return {
      inviteBg,
      invitePop,
      sysparaList: [],
      inviteCondition: 0,
      inviteHref: ''
    }
  },
  props: {
    showInvitePop: {
      type: Boolean,
      default: false,
    }
  },
  directives: {
    clipboard
  },
  computed: {
    ...mapGetters(['userInfo', 'merchantInfo']),
  },
  mounted() {
    this.getInviteRange()
    this.getInviteCondition()
    this.getInviteHref()
  },
  methods: {
    highlight(text) {
      return text.replace(/<span class="highlight">(.*?)<\/span>/g, "<span class='highlight'>$1</span>");
    },
    clipboardSuccess() {
      this.$notify({
        title: this.$t('成功'),
        message: this.$t('复制成功'),
        type: 'success',
        duration: 1500
      });
    },
    // 获取系统参数
    getSyspara(code, cb) {
      getSyspara({code}).then(res => {
        cb(res)
      })
    },
    //获取邀请区间
    getInviteRange() {
      this.getSyspara('mall_first_invite_recharge_rewards', res => {
        const syspara = res.data.mall_first_invite_recharge_rewards ? JSON.parse(res.data.mall_first_invite_recharge_rewards) : []
        this.sysparaList = []
        for (let i = 0; i < syspara.length; i++) {
          this.sysparaList.push({
            reward: syspara[i][0],
            inviteMin: syspara[i][1],
            inviteMax: i + 1 < syspara.length ? ((syspara[i + 1][1]) - 1) : ''
          })
        }
      })
    },
    //获取参与条件
    getInviteCondition() {
      this.getSyspara('valid_recharge_amount_for_first_recharge_bonus', res => {
        this.inviteCondition = res.data.valid_recharge_amount_for_first_recharge_bonus || 0
      })
    },
    //获取邀请链接
    getInviteHref() {
      promotional_post().then(res => {
        const promotional = res.data
        this.inviteHref = promotional.download + '/#/?usercode=' + promotional.code
      })
    },
    //领取奖励
    getInviteReward() {
      receiveInviteBonus().then(() => {
        this.$message({
          message: this.$t('领取成功'),
          type: 'success',
          duration: 1500,
        })
        this.seller_info_action()
      })
    },
    seller_info_action() {
      seller_info_action_post({}).then((res) => {
        this.$store.commit('user/CHANGE_MERCHANT_INFO', res.data)
      })
    },
    changeShowInvitePop(val) {
      this.$emit('changeShowInvitePop', val)
    },

  }
}
</script>

<template>
  <div>

    <div class="invite-pop" v-if="showInvitePop">
      <div class="invite-pop-content">
        <el-image :src="invitePop"
                  fit="cover" class="invite-pop-content-image"></el-image>
        <div class="icon-close">
          <i class="el-icon-close"
             @click="changeShowInvitePop(false)"></i>
        </div>
        <div class="invite-pop-main">
          <div class="invite-pop-title">
            <span
                v-html='highlight($t("邀请好友 <span class=highlight>得现金</span>"))'>
            </span>
            <span class="invite-pop-title-des"
                  v-html='highlight($t("邀请好友瓜分$100,000现金"))'>
            </span>
          </div>
          <div class="invite-pop-rule">
            <div class="invite-pop-rule-title">
              <el-image :src="require('@/assets/active/invite_title_icon.png')"
                        style="width: 16px;height: 12px;margin: 0 12px;" fit="fill"/>
              <span>{{ $t("活动规则") }}</span>
              <el-image :src="require('@/assets/active/invite_title_icon.png')"
                        style="width: 16px;height: 12px;margin: 0 12px;transform: rotate(180deg)" fit="fill"/>
            </div>
            <div class="invite-pop-text mt-24 mb-12">
              {{ $t("活动期间，你每成功邀请一个新用户注册并激活店铺都将得到奖金,达到邀请人数之后奖金提升如下：") }}
            </div>
            <div class="invite-table">
              <div class="invite-table-header">
                <div>{{ $t("邀请人数") }}</div>
                <div>{{ $t("每人奖励") }}</div>
              </div>
              <div class="invite-table-row" v-for="(item,index) in sysparaList" :key="index">
                <div>{{ item.inviteMin }}{{ item.inviteMax ? ' - ' + item.inviteMax : ' +' }}</div>
                <div class="blue">${{ item.reward }}</div>
              </div>
            </div>
            <div class="invite-pop-text mt-18">
              {{ $t("邀请越多，奖励越多，先到先得，数量有限！") }}
            </div>
            <div class="invite-pop-text mt-10">
              {{ $t("注意：好友开店首次充值金额满足≥ ${_$1}", {_$1: inviteCondition}) }}
            </div>
          </div>
          <div class="invite-history">
            <div class="invite-history-title">
              <el-image :src="require('@/assets/active/invite_title_icon.png')"
                        style="width: 16px;height: 12px;margin: 0 12px;" fit="fill"/>
              <span>{{ $t("我的邀请记录") }}</span>
              <el-image :src="require('@/assets/active/invite_title_icon.png')"
                        style="width: 16px;height: 12px;margin: 0 12px;transform: rotate(180deg)" fit="fill"/>
            </div>
            <div class="invite-history-content">
              <div class="invite-history-content-item">
                <div class="invite-history-content-number">{{ merchantInfo.inviteNum || 0 }}</div>
                <div class="invite-pop-text">{{ $t("成功邀请(人)") }}</div>
              </div>
              <div class="invite-history-content-item">
                <div class="invite-history-content-number">{{ merchantInfo.inviteReceivedReward || 0 }}</div>
                <div class="invite-pop-text">{{ $t("累计返现($)") }}</div>
              </div>
            </div>
            <div class="invite-href">
              <div class="invite-href-content">
                <div class="invite-href-text">{{ inviteHref }}</div>
                <div class="invite-href-button"
                     v-clipboard:copy="inviteHref"
                     v-clipboard:success="clipboardSuccess">{{ $t("复制链接") }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.invite-pop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 99999;

  .invite-pop-text {
    color: #333;
    font-family: Roboto;
    font-size: 14px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
  }

  &::after {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    backdrop-filter: blur(10px);
    background: rgba(0, 0, 0, .5);
  }

  .invite-pop-content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: #fff;
    overflow: hidden;
    border-radius: 10px;
    z-index: 9;
    width: 476px;
    height: auto;
    flex-shrink: 0;

    .icon-close {
      position: absolute;
      top: 12px;
      right: 12px;
      cursor: pointer;
      z-index: 9;

      .el-icon-close {
        color: #fff;
        font-size: 24px;
        border: solid 1px #fff;
        border-radius: 50%;
      }
    }

    .invite-pop-content-image {
      position: absolute;
      top: 0;
      left: 0;
      width: 476px;
    }

    .invite-pop-main {
      width: 100%;
      height: 100%;
      padding: 12px;
      box-sizing: border-box;
      position: relative;
      z-index: 1;

      .invite-pop-title {
        display: flex;
        justify-content: center;
        align-items: self-start;
        flex-direction: column;
        color: #FFF;
        font-family: PingFang SC;
        font-size: 20px;
        font-weight: 600;
        height: 120px;
        width: 220px;
        position: relative;
        line-height: 26px;
        left: 56px;
        top: 12px;

        .invite-pop-title-des {
          color: #D6EFFF;
          width: 100%;
          font-family: PingFang SC;
          font-size: 16px;
          font-weight: 400;
          line-height: 16px;
        }
      }

      .invite-pop-rule {
        border-radius: 6px;
        background: #E2EAFF;
        padding: 18px;
        margin-bottom: 12px;
        margin-top: 24px;

        .invite-pop-rule-title {
          color: var(--zhuce, #1552F0);
          text-align: center;
          font-family: Roboto;
          font-size: 20px;
          font-style: normal;
          font-weight: 600;
          line-height: normal;
        }

        .invite-table {
          border-radius: 6px;
          overflow: hidden;
          margin: 12px 0;

          .invite-table-header {
            background: #C3D4FF;
            display: flex;
            justify-content: space-between;

            > div {
              width: 50%;
              height: 34px;
              line-height: 34px;
              text-align: center;

              &:first-child {
                border-right: 1px solid #ffffff;
              }
            }
          }

          .invite-table-row {
            background: #F1F5FF;
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #ffffff;
            height: 35px;
            color: #000;
            font-family: Roboto;
            font-size: 13px;
            font-style: normal;
            font-weight: 500;

            .blue {
              color: #1552F0;
              font-family: Roboto;
              font-size: 13px;
              font-style: normal;
              font-weight: 500;
            }

            &:last-child {
              border-bottom: none;
              height: 34px;
            }

            > div {
              width: 50%;
              line-height: 34px;
              text-align: center;

              &:first-child {
                border-right: 1px solid #ffffff;
              }
            }
          }
        }
      }

      .invite-history {
        border-radius: 6px;
        background: #E2EAFF;
        padding: 18px;

        .invite-history-title {
          color: var(--zhuce, #1552F0);
          text-align: center;
          font-family: Roboto;
          font-size: 20px;
          font-style: normal;
          font-weight: 600;
          line-height: normal;
        }

        .invite-history-content {
          display: flex;
          justify-content: space-between;

          .invite-history-content-item {
            width: 50%;
            text-align: center;
            margin: 12px 0;
            position: relative;

            &:first-child::after {
              content: "";
              position: absolute;
              top: 0;
              right: 0;
              width: 1px;
              height: 26px;
              background: #B0C1ED;
              transform: translateY(50%);
            }

            .invite-history-content-number {
              color: #1552F0;
              font-family: Roboto;
              font-size: 24px;
              font-style: normal;
              font-weight: 500;
              line-height: normal;
            }
          }
        }

        .invite-href {
          margin-top: 12px;

          .invite-href-content {
            height: 42px;
            border-radius: 6px;
            background: #F1F5FF;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px;

            .invite-href-text {
              color: #000;
              font-family: PingFang SC;
              font-size: 12px;
              font-style: normal;
              font-weight: 400;
              line-height: 16px;
              padding-left: 6px;
            }

            .invite-href-button {
              height: 32px;
              flex-shrink: 0;
              width: auto;
              border-radius: 6px;
              background: #1552F0;
              color: #ffffff;
              font-family: PingFang SC;
              font-size: 14px;
              font-style: normal;
              font-weight: 400;
              line-height: normal;
              display: flex;
              justify-content: center;
              align-items: center;
              flex-direction: column;
              padding: 0 6px;
              cursor: pointer;
            }
          }
        }
      }
    }
  }
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
        text-align: center;
        margin-bottom: 18px;
        text-shadow: 1px 1px 1px #888888;

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
        text-shadow: 1px 1px 1px #888888;
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
      color: #ffffff;
      min-width: 150px;
      font-family: 'Roboto';
      font-style: normal;
      font-weight: 700;
      font-size: 20px;
      border: none;
      background: linear-gradient(180deg, #FF965B 0%, #CE3925 100%);
    }

    .first-charge-image {
      position: absolute;
      top: 0;
      left: 0;
    }
  }
}

::v-deep {
  .highlight {
    color: #FECC1C;
  }
}

</style>
