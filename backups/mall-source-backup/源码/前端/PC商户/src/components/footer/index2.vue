<template>
  <div class="footer">
    <div class="app-container">
      <div class="footer-wrapper flex-start">
        <div class="footer-title flex-start">
          <img
            :src="require('@/assets/image/logo_1.png')"
            alt=""
            @click="goHome"
          />
        </div>
        <div class="footer-nav">
          <div
            class="footer-nav-item flex-start"
            v-for="(item, index) in linkNav"
            :key="index"
          >
            <h1>{{ item.title }}</h1>
            <ul class="flex-start">
              <li
                v-for="(childItem, childIndex) in item.nav"
                :key="childIndex"
                @click="childItem.clickEvent"
              >
                {{ childItem.name }}
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>COPYRIGHT© 2019-2022 SHOP PO, LLC. ALL RIGHTS RESERVED.</p>
        <p>
          {{ $t('message.home.footTips') }}
        </p>
      </div>
      <!-- <el-row :gutter="20">
        <el-col :xs="24" :sm="6" :md="4" :lg="4" :xl="4">
          <div class="footer-subscribe">
            <h2>Get your special offers coupons more</h2>
            <el-input
              v-model="email"
              placeholder="Your Email Address"
            ></el-input>
            <el-button plain>Subscribe</el-button>
          </div>
        </el-col>
        <el-col :xs="24" :sm="18" :md="20" :lg="20" :xl="20">
          <div class="footer-nav">
            <div
              class="footer-nav-item flex-start"
              v-for="(item, index) in linkNav"
              :key="index"
            >
              <h1>{{ item.title }}</h1>
              <ul class="flex-start">
                <li
                  v-for="(childItem, childIndex) in item.nav"
                  :key="childIndex"
                >
                  {{ childItem.name }}
                </li>
              </ul>
            </div>
          </div>
        </el-col>
      </el-row> -->
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
export default {
  name: 'EsFooter',
  data() {
    const JumpToLogin = () => {
      if (this.$route.path !== '/login') {
        this.$router.push('/login')
      }
    }

    const JumpTo = (path) => {
      if (this.isLogin) {
        this.$router.push(path)
      } else {
        JumpToLogin()
      }
    }
    return {
      email: '',
      linkNav: [
        {
          title: this.$t('message.home.myAccount' /** 我的帐户*/),
          nav: [
            {
              name: this.$t('message.home.login' /** 登录*/),
              path: '',
              clickEvent: () => JumpToLogin(),
            },
            {
              name: this.$t('message.home.buyHistory' /** 购买记录*/),
              path: '',
              clickEvent: () => JumpTo('/userInfo/my-order'),
            },
            {
              name: this.$t('message.home.wishlist' /** 收藏商品*/),
              path: '',
              clickEvent: () => JumpTo('/userInfo/dashboard'),
            },
            {
              name: this.$t('message.home.trackOrder' /**订单 */),
              path: '',
              clickEvent: () => JumpTo('/userInfo/my-order'),
            },
            {
              name: this.$t('message.home.account' /**账户 */),
              path: '',
              clickEvent: () => JumpTo('/userInfo/dashboard'),
            },
          ],
        },
        {
          title: this.$t('message.home.sellerZone' /**商户专区 */),
          nav: [
            {
              name: this.$t('message.home.beSeller' /**成为商户 */),
              path: '',
              clickEvent: () => {
                window.location.href = window.origin + '/wap/#/merchantSettled'
              },
            },
            {
              name: this.$t('message.home.sellerPanelLogin' /**商户登录 */),
              path: '',
              clickEvent: () => {
                window.location.href =
                  window.origin + '/ww/#/login?redirect=%2Fdashboard'
              },
            },
          ],
        },
      ],
    }
  },
  computed: {
    ...mapGetters(['existToken', 'isLogin']),
  },
  mounted() {
    this.$set(
      this.linkNav[0].nav[0],
      'name',
      this.existToken
        ? this.$t('message.home.userCenter')
        : this.$t('message.home.login' /** 登录*/),
    )
    this.$set(
      this.linkNav[0].nav[0],
      'clickEvent',
      this.existToken
        ? () => this.$router.push('/userInfo/dashboard')
        : () => this.$router.push('/login'),
    )
  },
  methods: {
    goHome() {
      this.$router.push('/')
    },
  },
}
</script>

<style lang="scss">
.footer {
  background-color: var(--color-footer-bg);
  padding: 27px 20px;
  &-title {
    // border-bottom: 1px solid #3f3f3f;
    // padding-bottom: 30px;
    // margin-bottom: 27px;

    img {
      width: 165px;
      height: 44px;
      margin-right: 9px;
      cursor: pointer;
    }
    h1 {
      color: var(--color-white);
      font-size: 20px;
      font-weight: 600;
      margin: 0;
    }
  }

  &-wrapper {
    align-items: flex-start !important;
    border-bottom: 1px solid #3f3f3f;
  }
  &-subscribe {
    margin-bottom: 20px;
    h2 {
      font-size: 14px;
      color: var(--color-main);
      font-weight: 700;
      margin-bottom: 25px;
    }
    .el-input__inner {
      margin-bottom: 18px;
      height: 43px;
      border-radius: 4px;
      max-width: 288px;
    }
    .el-button {
      border-color: var(--color-main);
      color: var(--color-main);
      background-color: transparent;
      &:hover {
        background-color: transparent !important;
      }
    }
  }

  &-nav {
    width: 100%;
    align-items: flex-start !important;
    &-item {
      h1 {
        font-size: 16px;
        font-weight: 700;
        color: var(--color-main);
        width: 110px;
        text-align: left;
        margin: 0 42px;
        margin-bottom: 37px;
      }
      ul {
        list-style: none;
        margin-right: 105px;
        li {
          margin-bottom: 37px;
          font-size: 12px;
          font-weight: 300;
          color: var(--color-white);
          width: 120px;
          cursor: pointer;
          &:hover {
            color: var(--color-main);
          }
        }
      }
    }
  }

  &-bottom {
    font-size: 12px;
    padding: 22px 20px;
    color: #6b6b6b;
  }
}
</style>
