<template>
  <div class="bg-gray-200 my-content">
    <div class="bg" :style="{ 'background-image': 'url(' + bgImg + ')' }"></div>
    <div class="content">
      <div class="flex items-center info">
        <div class="flex items-center userinfo-content">
          <div
            class="avatar-content"
            :class="isArLang ? 'ml-4' : 'mr-4'"
            @click="() => router.push('/changeAvatar')"
          >
            <img :src="defaultAvatar.avatar" alt="" />
          </div>
          <div class="text-white">
            <div class="font-bold text-lg">{{ userInfo.username }}</div>
            <div class="flex items-center">
              <div class="text-sm" :class="isArLang ? 'ml-1' : 'mr-1'">
                ID: {{ userInfo.usercode }}
              </div>
              <i class="iconfont icon-fuzhi" @click="copy"></i>
            </div>
          </div>
        </div>
        <div v-if="currentLevelObj" class="level-info">
          <img :src="currentLevelObj.icon" alt="">
          <div v-if="currentLevelObj.name" :class="currentLevelObj.name" class="txt">{{ `${t('等级')} ${currentLevelObj.name}` }}</div>
        </div>
      </div>
      <div v-if="nextLevelObj" class="level-progress">
        <div v-if="currentLevelObj.name" class="name" :style="{ 'background-image': 'url(' + getLevelIconImg(currentLevelObj.name) + ')' }">{{ currentLevelObj.name }}</div>
        <div class="progress">
          <div class="txt" :style="{'left': gapProgress}">{{ gapProgress }}</div>
          <div class="line" :style="{'width': gapProgress}"></div>
        </div>
        <div class="name" :style="{ 'background-image': 'url(' + getLevelIconImg(nextLevelObj.name) + ')' }">{{ nextLevelObj.name }}</div>
      </div>
      <div class="level-number-content">
        <p v-if="nextLevelObj" v-html="t('当前运行资金，距离等级还需', {money: numberStrFormat(storeMoneyRechargeAcc), level: nextLevelObj.name, money1: numberStrFormat(Number(nextLevelObj.rechargeAmountCnd) - Number(storeMoneyRechargeAcc))})"></p>
        <div v-if="currentLevelObj" @click="openPage('/sellerLevel')">
          <p>
            {{ t('当前分店人数') }}<span>{{ currentChildNum }}</span><span v-if="currentLevelObj.popularizeUserCountCnd" class="em">/{{ currentLevelObj.popularizeUserCountCnd }}</span>,
            {{ t('当前团队人数') }}<span>{{ currentTeamNum }}</span><span v-if="currentLevelObj.teamNum" class="em">/{{ currentLevelObj.teamNum }}</span>,
            {{ t('当前采购优惠') }}<span>{{ currentLevelObj.sellerDiscount }}</span>
          </p>
          <van-icon name="arrow" color="#ffffff" />
        </div>
      </div>
      <van-cell-group inset>
        <van-cell>
          <template #title>
            <div
              class="flex justify-between items-center"
              style="flex-wrap: wrap"
            >
              <div>
                <div class="flex items-center freeze-total-content">
                  <div class="font-bold text-xl" :class="isArLang ? 'ml-3' : 'mr-3'">
                    {{ showWalletNum ? `$${numberStrFormat(userInfo.money)}` : '*****' }}
                  </div>
                  <i v-if="showWalletNum" class="iconfont icon-denglu-mimakejian" @click="showWalletNum = false"></i>
                  <i v-if="!showWalletNum" class="iconfont icon-denglu-mimabukejian" @click="showWalletNum = true"></i>
                  <i class="iconfont icon-shuaxin" @click="refresh"></i>
                </div>
                <div class="freeze-num-content">
                  {{ t('balance') }}
                  <p v-if="Number(userInfo.frozenMoney)">(<span>{{ t('冻结余额') }} {{ showWalletNum ? `$${numberStrFormat(userInfo.frozenMoney)}` : '*****' }}</span>)</p>
                </div>
              </div>
            </div>
          </template>
        </van-cell>

        <van-cell>
          <template #title>
            <div class="color-333"
              >{{ t('commissions') }}: ${{
                showWalletNum ? numberStrFormat(userInfo.rebate) : '*****'
              }}</div
            >
            <div class="freeze-btn-content">
              <van-button
                  plain
                  size="small"
                  type="primary"
                  class="btn-content"
                  @click="handleWithdraw"
                  >{{
                    isHive && ['cn', 'tw'].includes(locale)
                      ? t('提领')
                      : t('withdrawal')
                  }}</van-button
                >
                <van-button
                  size="small"
                  type="primary"
                  class="btn-content block"
                  @click="handleRechargeBefore"
                  >{{
                    isHive && ['cn', 'tw'].includes(locale)
                      ? t('加值')
                      : t('recharge')
                  }}</van-button
                >
            </div>
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 首冲奖励、邀请送礼金活动 -->
      <div v-if="showRward || showInvite" class="award-content">
        <van-swipe class="my-swipe" :autoplay="5000" indicator-color="white">
          <van-swipe-item v-if="showRward && rwardsInfo.length">
            <div class="first-content">
              <h2>{{ t('首充活动奖励') }}</h2>
              <div class="info">
                <p
                  v-if="rwardsInfo[0]"
                  class="info-txt"
                  v-html="
                    t('mall_first_recharge_rewards', {
                      recharge: rwardsInfo[0][1],
                      rewards: rwardsInfo[0][0]
                    })
                  "
                ></p>
                <span v-if="rwardsInfo[1]">. </span>
                <p
                  v-if="rwardsInfo[1]"
                  class="info-txt"
                  v-html="
                    t('mall_first_recharge_rewards', {
                      recharge: rwardsInfo[1][1],
                      rewards: rwardsInfo[1][0]
                    })
                  "
                ></p>
              </div>
              <p
                v-if="rwardsInfo[2]"
                class="info-txt"
                v-html="
                  t('mall_first_recharge_rewards', {
                    recharge: rwardsInfo[2][1],
                    rewards: rwardsInfo[2][0]
                  })
                "
              ></p>
              <div
                v-if="rechargeBonusStatus === 0"
                class="btn"
                @click="handleRecharge"
              >
                {{ t('去充值') }}
              </div>
              <div v-if="rechargeBonusStatus && showRawrdBtn" class="btn get" @click="rawrdHandle">{{ t('领取') }}</div>
            </div>
          </van-swipe-item>
          <van-swipe-item v-if="showInvite">
            <div
              class="invite-content"
              @click.stop="openPage('/invitation-activity')"
            >
              <h3
                v-html="t('myInviteTitle')"
                :class="{ 'not-cn': notCnLang }"
              ></h3>
              <p
                v-html="
                  t('myInviteInfo', {
                    total: inviteReceivedReward,
                    bonus: inviteAmountReward
                  })
                "
                :class="{ 'not-cn': notCnLang }"
              ></p>
              <div
                :class="{ 'not-cn': notCnLang, 'is-ar': isArLang }"
                class="btn"
                @click.stop="inviteHandle"
              >
                {{ inviteAmountReward ? t('领取') : t('邀请') }}
              </div>
            </div>
          </van-swipe-item>
        </van-swipe>
      </div>

      <!-- 贷款申请 -->
      <div v-if="loanShow" class="single-banner-content mt-4">
        <div
          :style="{ 'background-image': 'url(' + loanImg.bg + ')' }"
          class="banner-content"
          @click="goToLoan"
        >
          <div class="info">
            <img :src="loanImg.icon" alt="" />
            <p>{{ t('贷款申请') }}</p>
          </div>
          <van-icon name="arrow" />
        </div>
      </div>

      <div class="mt-4" :class="{ 'is-ar-cell-group': isArLang }">
        <van-cell-group inset>
          <van-cell is-link to="/personalInfo">
            <template #title>
              <div class="flex items-center">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 20 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M7.19036 5.44135C7.19036 3.89024 8.44778 2.63281 9.9989 2.63281C11.55 2.63281 12.8074 3.89024 12.8074 5.44135C12.8074 6.99247 11.55 8.24989 9.9989 8.24989C8.44778 8.24989 7.19036 6.99247 7.19036 5.44135ZM9.9989 1.13281C7.61935 1.13281 5.69036 3.06181 5.69036 5.44135C5.69036 7.82089 7.61935 9.74989 9.9989 9.74989C12.3784 9.74989 14.3074 7.82089 14.3074 5.44135C14.3074 3.06181 12.3784 1.13281 9.9989 1.13281ZM6.44135 11.8083C5.29866 11.8083 4.20276 12.2623 3.39475 13.0703C2.58675 13.8783 2.13281 14.9742 2.13281 16.1169V17.8961C2.13281 18.3103 2.4686 18.6461 2.88281 18.6461C3.29703 18.6461 3.63281 18.3103 3.63281 17.8961V16.1169C3.63281 15.372 3.92871 14.6576 4.45542 14.1309C4.98212 13.6042 5.69648 13.3083 6.44135 13.3083H13.5584C14.3033 13.3083 15.0177 13.6042 15.5444 14.1309C16.0711 14.6576 16.367 15.372 16.367 16.1169V17.8961C16.367 18.3103 16.7028 18.6461 17.117 18.6461C17.5312 18.6461 17.867 18.3103 17.867 17.8961V16.1169C17.867 14.9742 17.413 13.8783 16.605 13.0703C15.797 12.2622 14.7011 11.8083 13.5584 11.8083H6.44135Z"
                    fill="black"
                  />
                </svg>
                <div class="color-333" :class="isArLang ? 'mr-2' : 'ml-2'">
                  {{ t('personalInformation') }}
                </div>
              </div>
            </template>
          </van-cell>
          <van-cell is-link :value="currentLang" to="/language">
            <template #title>
              <div class="flex items-center">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 20 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M2.50181 9.76243C2.57523 6.41014 4.86937 3.60518 7.97153 2.76023C7.81487 3.11595 7.67631 3.51349 7.55469 3.93914C7.11853 5.46573 6.85432 7.51919 6.84189 9.76243H2.50181ZM2.61948 11.2624C3.1313 14.0847 5.23763 16.3516 7.97153 17.0963C7.81487 16.7406 7.67631 16.343 7.55469 15.9174C7.19552 14.6603 6.95295 13.0459 6.87157 11.2624H2.61948ZM8.37321 11.2624C8.45342 12.9266 8.68044 14.3974 8.99698 15.5053C9.19785 16.2083 9.42294 16.7228 9.64008 17.0442C9.79178 17.2688 9.89191 17.3336 9.92814 17.3514C9.96438 17.3336 10.0645 17.2688 10.2162 17.0442C10.4333 16.7228 10.6584 16.2083 10.8593 15.5053C11.1758 14.3974 11.4029 12.9266 11.4831 11.2624H8.37321ZM12.9847 11.2624C12.9033 13.0459 12.6608 14.6603 12.3016 15.9174C12.18 16.3431 12.0414 16.7407 11.8847 17.0965C14.619 16.3521 16.7256 14.085 17.2375 11.2624H12.9847ZM17.3552 9.76243H13.0144C13.002 7.51919 12.7378 5.46573 12.3016 3.93914C12.18 3.5134 12.0414 3.11578 11.8847 2.76001C14.9872 3.60469 17.2818 6.40985 17.3552 9.76243ZM11.5144 9.76243H8.34191C8.3544 7.62057 8.60815 5.71211 8.99698 4.35122C9.19785 3.64816 9.42294 3.13373 9.64008 2.81228C9.79179 2.5877 9.89191 2.52286 9.92814 2.50509C9.96438 2.52286 10.0645 2.5877 10.2162 2.81228C10.4333 3.13373 10.6584 3.64816 10.8593 4.35122C11.2481 5.71211 11.5019 7.62057 11.5144 9.76243ZM9.9285 18.8568H9.92814L9.92402 18.8568C4.99501 18.8543 1 14.8578 1 9.92825C1 4.99718 4.99742 0.999756 9.9285 0.999756C14.8596 0.999756 18.857 4.99718 18.857 9.92825C18.857 14.8593 14.8596 18.8568 9.9285 18.8568Z"
                    fill="#333333"
                  />
                </svg>
                <div class="color-333" :class="isArLang ? 'mr-2' : 'ml-2'">
                  {{ t('language') }}
                </div>
              </div>
            </template>
          </van-cell>
          <van-cell is-link to="/refundRequest">
            <template #title>
              <div class="flex items-center">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 20 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M10.7282 9.26364C9.27182 8.78091 8.56818 8.47818 8.56818 7.70909C8.56818 6.87455 9.47637 6.57182 10.0491 6.57182C11.1209 6.57182 11.5136 7.38182 11.6036 7.66818L12.8964 7.12C12.7736 6.75182 12.2255 5.54909 10.8182 5.28727V4.27273H9.18182V5.30364C7.15273 5.76182 7.14455 7.64364 7.14455 7.72546C7.14455 9.58273 8.98546 10.1064 9.88546 10.4336C11.1782 10.8918 11.7509 11.3091 11.7509 12.0945C11.7509 13.0191 10.8918 13.4118 10.1309 13.4118C8.64182 13.4118 8.21637 11.8818 8.16727 11.7018L6.80909 12.25C7.32455 14.0418 8.67455 14.5245 9.18182 14.6718V15.7273H10.8182V14.7127C11.1455 14.6391 13.1909 14.23 13.1909 12.0782C13.1909 10.9409 12.6918 9.94273 10.7282 9.26364ZM2.63636 17.3636H1V12.4545H5.90909V14.0909H3.88C5.19727 16.0627 7.44727 17.3636 10 17.3636C11.953 17.3636 13.8259 16.5878 15.2069 15.2069C16.5878 13.8259 17.3636 11.953 17.3636 10H19C19 14.9745 14.9745 19 10 19C6.95637 19 4.26455 17.4864 2.63636 15.1791V17.3636ZM1 10C1 5.02546 5.02546 1 10 1C13.0436 1 15.7355 2.51364 17.3636 4.82091V2.63636H19V7.54546H14.0909V5.90909H16.12C14.8027 3.93727 12.5527 2.63636 10 2.63636C8.04704 2.63636 6.17407 3.41217 4.79312 4.79312C3.41217 6.17407 2.63636 8.04704 2.63636 10H1Z"
                    fill="black"
                  />
                </svg>
                <div class="color-333" :class="isArLang ? 'mr-2' : 'ml-2'">
                  {{ t('refundRequest') }}
                </div>
              </div>
            </template>
          </van-cell>
        </van-cell-group>
      </div>

      <div class="mt-4">
        <van-cell-group inset>
          <van-cell is-link to="/fundsRecords">
            <template #title>
              <div class="flex items-center">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 20 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M2.5 10.0629C2.5 5.88615 5.8859 2.50024 10.0626 2.50024C14.2393 2.50024 17.6253 5.88615 17.6253 10.0629C17.6253 14.2396 14.2393 17.6255 10.0626 17.6255C5.8859 17.6255 2.5 14.2396 2.5 10.0629ZM10.0626 1.00024C5.05748 1.00024 1 5.05772 1 10.0629C1 15.068 5.05748 19.1255 10.0626 19.1255C15.0678 19.1255 19.1253 15.068 19.1253 10.0629C19.1253 5.05772 15.0678 1.00024 10.0626 1.00024ZM9.03386 5.8957C9.32676 6.18859 9.32676 6.66346 9.03386 6.95636L8.23604 7.75418H13.6989C14.1131 7.75418 14.4489 8.08997 14.4489 8.50418C14.4489 8.9184 14.1131 9.25418 13.6989 9.25418H6.42538C6.12203 9.25418 5.84855 9.07145 5.73247 8.7912C5.61638 8.51094 5.68055 8.18835 5.89505 7.97385L7.9732 5.8957C8.2661 5.6028 8.74097 5.6028 9.03386 5.8957ZM11.0907 14.2297C10.7978 13.9368 10.7978 13.462 11.0907 13.1691L11.8885 12.3712H6.42565C6.01144 12.3712 5.67565 12.0355 5.67565 11.6212C5.67565 11.207 6.01144 10.8712 6.42565 10.8712H13.6992C14.0025 10.8712 14.276 11.054 14.3921 11.3342C14.5082 11.6145 14.444 11.9371 14.2295 12.1516L12.1514 14.2297C11.8585 14.5226 11.3836 14.5226 11.0907 14.2297Z"
                    fill="#333333"
                  />
                </svg>
                <div class="color-333" :class="isArLang ? 'mr-2' : 'ml-2'">
                  {{ t('fundingRecords') }}
                </div>
              </div>
            </template>
          </van-cell>
          <van-cell is-link to="/finance">
            <template #title>
              <div class="flex items-center">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 20 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <g clip-path="url(#clip0_229_4452)">
                    <path
                      d="M2 2V18H18"
                      stroke="#333333"
                      stroke-width="1.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M5 11.82L8.84 7.98L12.68 11.82L17 7.5"
                      stroke="#333333"
                      stroke-width="1.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </g>
                  <defs>
                    <clipPath id="clip0_229_4452">
                      <rect width="20" height="20" fill="white" />
                    </clipPath>
                  </defs>
                </svg>

                <div class="color-333" :class="isArLang ? 'mr-2' : 'ml-2'">
                  {{ t('financialStatement') }}
                </div>
              </div>
            </template>
          </van-cell>
          <van-cell v-if="promotionShow" is-link to="/shop/promotion">
            <template #title>
              <div class="flex items-center">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 20 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M12.9361 2.5C12.0096 2.5 11.2585 3.25109 11.2585 4.1776C11.2585 4.47097 11.3338 4.74675 11.4661 4.98667C11.4736 4.99793 11.4807 5.00946 11.4876 5.02124C11.4944 5.033 11.5009 5.04487 11.5071 5.05684C11.8025 5.53589 12.332 5.8552 12.9361 5.8552C13.8626 5.8552 14.6137 5.10411 14.6137 4.1776C14.6137 3.25109 13.8626 2.5 12.9361 2.5ZM10.6462 6.38063C11.2243 6.98139 12.0365 7.3552 12.9361 7.3552C14.691 7.3552 16.1137 5.93254 16.1137 4.1776C16.1137 2.42266 14.691 1 12.9361 1C11.1812 1 9.75851 2.42266 9.75851 4.1776C9.75851 4.49296 9.80445 4.7976 9.89001 5.08517L5.51476 7.63847C4.9367 7.03809 4.1247 6.66455 3.22545 6.66455C1.47051 6.66455 0.0478516 8.08721 0.0478516 9.84215C0.0478516 11.5971 1.47051 13.0197 3.22545 13.0197C4.12505 13.0197 4.93734 12.6459 5.51544 12.0451L9.89113 14.5949C9.80485 14.8836 9.75851 15.1895 9.75851 15.5063C9.75851 17.2612 11.1812 18.6839 12.9361 18.6839C14.691 18.6839 16.1137 17.2612 16.1137 15.5063C16.1137 13.7513 14.691 12.3287 12.9361 12.3287C12.0379 12.3287 11.2268 12.7013 10.6489 13.3004L6.27158 10.7496C6.35712 10.4621 6.40305 10.1575 6.40305 9.84215C6.40305 9.52647 6.35702 9.22154 6.2713 8.93371L10.6462 6.38063ZM4.65234 8.95949C4.65892 8.97241 4.6659 8.98521 4.6733 8.99789C4.6808 9.01074 4.68862 9.02328 4.69675 9.03552C4.82825 9.27487 4.90305 9.54977 4.90305 9.84215C4.90305 10.1331 4.82898 10.4068 4.69867 10.6453C4.68976 10.6586 4.68122 10.6722 4.67306 10.6862C4.66512 10.6998 4.65765 10.7136 4.65065 10.7275C4.35455 11.2032 3.82697 11.5197 3.22545 11.5197C2.29894 11.5197 1.54785 10.7687 1.54785 9.84215C1.54785 8.91564 2.29894 8.16455 3.22545 8.16455C3.82812 8.16455 4.35656 8.48234 4.65234 8.95949ZM11.2585 15.5063C11.2585 15.2309 11.3249 14.971 11.4424 14.7417C11.4617 14.7167 11.4796 14.6901 11.4959 14.662C11.5116 14.6351 11.5255 14.6075 11.5375 14.5796C11.8379 14.127 12.3522 13.8287 12.9361 13.8287C13.8626 13.8287 14.6137 14.5797 14.6137 15.5063C14.6137 16.4328 13.8626 17.1839 12.9361 17.1839C12.0096 17.1839 11.2585 16.4328 11.2585 15.5063Z"
                    fill="#333333"
                  />
                </svg>

                <div class="color-333" :class="isArLang ? 'mr-2' : 'ml-2'">
                  {{ t('shopPromotion') }}
                </div>
              </div>
            </template>
          </van-cell>
        </van-cell-group>
      </div>

      <div class="mt-4">
        <van-cell-group inset>
          <van-cell is-link to="/setting">
            <template #title>
              <div class="flex items-center">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 20 20"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M10.2759 1.10048C10.0438 0.966506 9.75794 0.966506 9.52589 1.10048L2.375 5.22905C2.14295 5.36303 2 5.61062 2 5.87857V14.1357C2 14.4037 2.14295 14.6513 2.375 14.7852L9.52589 18.9138C9.75794 19.0478 10.0438 19.0478 10.2759 18.9138L17.4268 14.7852C17.6588 14.6513 17.8018 14.4037 17.8018 14.1357V5.87857C17.8018 5.61062 17.6588 5.36303 17.4268 5.22905L10.2759 1.10048ZM3.5 13.7027V6.31158L9.90089 2.61603L16.3018 6.31158V13.7027L9.90089 17.3983L3.5 13.7027ZM7.55418 10.0071C7.55418 8.71123 8.60471 7.6607 9.90061 7.6607C11.1965 7.6607 12.247 8.71123 12.247 10.0071C12.247 11.303 11.1965 12.3536 9.90061 12.3536C8.60471 12.3536 7.55418 11.303 7.55418 10.0071ZM9.90061 6.1607C7.77628 6.1607 6.05418 7.88281 6.05418 10.0071C6.05418 12.1315 7.77628 13.8536 9.90061 13.8536C12.0249 13.8536 13.747 12.1315 13.747 10.0071C13.747 7.88281 12.0249 6.1607 9.90061 6.1607Z"
                    fill="#333333"
                  />
                </svg>
                <div class="color-333" :class="isArLang ? 'mr-2' : 'ml-2'">
                  {{ t('setting') }}
                </div>
              </div>
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </div>
    <div class="safe-area-inset-bottom"></div>
  </div>
</template>

<script setup name="MyCenter">
import { useRouter } from 'vue-router'
import { computed, watch, reactive, nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import useClipboard from 'vue-clipboard3'
import { useUserStore } from '@/store/user'
import { useSystemStore } from '@/store/system.js'
import { Toast, Dialog } from 'vant'
import { GET_BALANCE } from '@/store/types.store'
import { levelData } from '@/views/sellerLevel/config'
import { langData } from '@/views/language/config'
import cloneDeep from 'lodash.clonedeep'
import { numberStrFormat, openPage, getImg } from '@/utils'
import { needChangeMode } from '@/config'

import {
  receiveBonus,
  beforeReceiveBonus,
  _getIdentify,
  getSysparaAction,
  receiveInviteRewards
} from '@/service/user.api.js'
import { malllevelList, sellerInfo } from '@/service/shop.api.js'
const { toClipboard } = useClipboard()
const { t, locale } = useI18n()
const userStore = useUserStore()
const router = useRouter()

const modeType = import.meta.env.MODE
const colorMode = needChangeMode.includes(modeType) ? modeType : 'main'

const bgImg = getImg(`imgs/me/${colorMode}/bg1.png`)
const defaultAvatar = reactive({
  avatar: new URL('@/assets/imgs/me/defaultAvatar.png', import.meta.url)
})

const currentLang = computed(() => {
  const data = cloneDeep(langData)
  const itemObj = data.find((item) => item.key === locale.value)
  return itemObj ? itemObj.title : locale.value
})

const mode = import.meta.env.MODE
const isHive = mode === 'hive'

const systemStore = useSystemStore()

const isArLang = computed(() => {
  return systemStore.isArLang
})

const notCnLang = computed(() => {
  return systemStore.notCnLang
})


// 商家等级
const currentLevel = ref('')
const currentChildNum = ref(0)
const currentTeamNum = ref(0)
const storeMoneyRechargeAcc = ref(0)
const gapProgress = ref('0')
const currentLevelObj = ref(null)
const nextLevelObj = ref(null)

const levelDataClone = cloneDeep(levelData)
if (['greenMall', 'hive', 'iceland', 'inchoi', 'int', 'mbuy', 'simon', 'tiktok-wholesale', 'tiktokMall'].includes(mode)) {
  const index = levelDataClone.findIndex((item) => item.name === 'SS')
  levelDataClone.splice(index, 1)
}
if (['familyShop', 'greenMall', 'hive', 'iceland', 'inchoi', 'int', 'mbuy', 'simon', 'sm', 'tiktok-wholesale', 'tiktokMall'].includes(mode)) {
  const index = levelDataClone.findIndex((item) => item.name === 'SSS')
  levelDataClone.splice(index, 1)
}
const levelDataRef = ref([...levelDataClone])

// 用户信息
const userInfo = computed(() => {
  let obj = {
    username: '',
    usercode: '',
    money: 0,
    rebate: 0
  }
  if (!userStore.userInfo.token) {
    router.push('/login')
  } else {
    obj = { ...obj, ...userStore.userInfo }
  }
  return obj
})

// 头像
watch(
  userInfo,
  async (val) => {
    if (isNaN(Number(val.avatar))) {
      defaultAvatar.avatar = val.avatar
    } else {
      await import(
        `./../../assets/image/userAvatar/${userStore.userInfo.avatar}.png`
      ).then((res) => {
        defaultAvatar.avatar = res.default
      })
    }
  },
  {
    immediate: true,
    deep: true
  }
)

const handleRechargeBefore = () => {
  const kycStatus = Number(userInfo.value.kyc_status)
  if (kycStatus !== 2) {
    let kycStatusTxt = ''
    switch (kycStatus) {
      case 0:
        kycStatusTxt = '未认证'
        break
      case 1:
        kycStatusTxt = '审核中'
        break
      case 3:
        kycStatusTxt = '审核失败'
        break
    }
    Toast(t(kycStatusTxt))
    setTimeout(() => {
      router.push('/name')
    }, 1500)
  } else {
    handleRecharge()
  }
}

const handleRecharge = () => {
  router.push({ name: 'Recharge' })
}

const handleWithdraw = () => {
  const safeword = Boolean(Number(userStore?.userInfo?.safeword))
  if (safeword) {
    router.push({ name: 'Withdraw' })
  } else {
    Dialog.confirm({
      title: t('dialogTips'),
      message: t('shopSafeWord'),
      cancelButtonText: t('cancel'),
      confirmButtonText: t('gotoSet'),
      confirmButtonColor: '#1552F0',
      cancelButtonColor: '#999'
    })
      .then(() => {
        router.push({ path: '/fundsPasswordSettings' })
      })
      .catch(() => {
        console.log('cancel')
      })
  }
}

const copy = async () => {
  try {
    await toClipboard(userInfo.value.usercode)
    Toast(t('copySuccess'))
  } catch (e) {
    console.error(e)
  }
}
const refresh = async () => {
  Toast.loading({
    forbidClick: true,
    loadingType: 'spinner',
    duration: 0
  })

  await getActivityInfo()

  userStore[GET_BALANCE]().finally(() => {
    Toast.clear()
  })
}

const cerStatus = ref(0)
const showRward = ref(false)
const rwardsInfo = ref([])
const sellerId = ref('')
const rechargeBonusStatus = ref(0)
const showInvite = ref(false)
const inviteAmountReward = ref(0)
const inviteReceivedReward = ref(0)
const getRwardsInfo = async () => {
  await beforeReceiveBonus()

  await _getIdentify().then((res) => {
    cerStatus.value = Number(res.status)
  })

  getActivityInfo()
}

// 请求获取信息
const getActivityInfo = async () => {
  await sellerInfo().then((res) => {
    if (res.id) {
      localStorage.setItem('sellerId', res.id)
    } else {
      localStorage.removeItem('sellerId')
    }
    inviteReceivedReward.value = res.inviteReceivedReward
    inviteAmountReward.value = res.inviteAmountReward
    sellerId.value = res.id
    rechargeBonusStatus.value = Number(res.rechargeBonusStatus)

    currentLevel.value = res.mallLevel
    currentChildNum.value = res.childNum || 0
    currentTeamNum.value = res.teamNum || 0
    storeMoneyRechargeAcc.value = res.storeMoneyRechargeAcc || 0
  })

  // 等级信息
  malllevelList().then((res) => {
    const data = res.result || []
    if (data.length) {
      levelDataRef.value.forEach((item) => {
        data.forEach((_item, _index) => {
          if (item.name === _item.level) {
            item.rechargeAmountCnd = _item.rechargeAmountCnd
            item.popularizeUserCountCnd = _item.popularizeUserCountCnd
            item.teamNum = _item.teamNum || 0
            item.sellerDiscount = _item.sellerDiscount
              ? `${Number(_item.sellerDiscount) * 100}%`
              : 0
          }
        })
      })

      const defaultLevel = {
        icon: getImg(`image/level/level_1.png`),
        rechargeAmountCnd: 0,
        popularizeUserCountCnd: 0,
        teamNum: 0,
        sellerDiscount: 0
      }
      currentLevelObj.value = levelDataRef.value.find(item => item.name === currentLevel.value) || defaultLevel
      const currentLevelObjIndex = levelDataRef.value.findIndex(item => item.name === currentLevel.value)
      if (currentLevelObjIndex + 1 < levelDataRef.value.length) {
        nextLevelObj.value = levelDataRef.value[currentLevelObjIndex + 1]
      }
      if (nextLevelObj.value) {
        gapProgress.value = (Number(storeMoneyRechargeAcc.value) / Number(nextLevelObj.value.rechargeAmountCnd)) > 1 ? '100%' : Number(numberStrFormat((Number(storeMoneyRechargeAcc.value) / Number(nextLevelObj.value.rechargeAmountCnd)) * 100, 2, true)) + '%'
      }
    }
  })


  getSysparaAction(
    'mall_first_invite_recharge_rewards,mall_first_recharge_rewards'
  ).then((res) => {
    const invite = res.mall_first_invite_recharge_rewards || ''
    const recharge = res.mall_first_recharge_rewards || ''

    // 邀请好友活动
    showInvite.value = invite && invite.length > 3

    // 首充活动
    const dataArr = JSON.parse(recharge)
    showRward.value =
      dataArr.length &&
      [0, 1].includes(rechargeBonusStatus.value) &&
      cerStatus.value === 2

    if (showRward.value) {
      rwardsInfo.value = dataArr
    }
  })
}

const rawrdHandle = () => {
  Toast.loading({
    forbidClick: true,
    duration: 0
  })
  receiveBonus({
    sellerId: sellerId.value
  }).then(() => {
    Toast.success(t('领取成功'))
    showRward.value = false
  })
}

// 贷款申请
const loanShow = computed(() => {
  const mode = import.meta.env.MODE
  return ['hive'].includes(mode)
})

const loanImg = {
  icon: new URL('@/assets/imgs/me/loan-icon.png', import.meta.url),
  bg: new URL('@/assets/imgs/me/loan-bg.png', import.meta.url)
}

const goToLoan = () => {
  const { hostname, origin } = window.location
  const href =
    hostname === 'localhost'
      ? 'https://www.catvg.xyz/wap/#/loan'
      : `${origin}/wap/#/loan`
  window.open(`${href}?lang=${locale.value}&token=${userStore.userInfo.token}`)
}

const inviteHandle = () => {
  if (cerStatus.value === 2) {
    if (Number(inviteAmountReward.value)) {
      Toast.loading({
        duration: 0,
        mask: true
      })
      receiveInviteRewards().then((res) => {
        Toast.success(t('领取成功'))
        getActivityInfo()
      })
    } else {
      openPage('/shop/promotion')
    }
  } else {
    openPage('/name')
  }
}

const showWalletNum = ref(true)

const getLevelIconImg = (name) => {
  const obj = levelDataRef.value.find(item => item.name === name)
  return obj.icon.href || ''
}

const promotionShow = computed(() => {
  return !['familyShop'].includes(mode)
})

const showRawrdBtn = computed(() => {
  return ![].includes(mode)
})

nextTick(() => {
  getRwardsInfo()
  userStore.getUserInfo(true)
})
</script>

<style lang="scss" scoped>
.info {
  margin: var(--van-cell-group-inset-padding);
  top: 66px;
  justify-content: space-between;
  .userinfo-content {
    flex: 1;
    .text-white {
      flex: 1;
      padding-right: 5px;
    }
    * {
      word-break: break-all;
    }
  }
  .level-info {
    position: relative;
    height: 70px;
    > img {
      height: 70px;
      width: auto;
    }
    > .txt {
      position: absolute;
      font-size: 12px;
      line-height: 1;
      color: #fff;
      padding: 5px 12px;
      left: 50%;
      transform: translateX(-50%);
      white-space: nowrap;
      bottom: -2px;
      border-radius: 30px;
      &.C {
        background: linear-gradient(180deg, #41b6fb 0%, #0799f0 100%);
      }
      &.B {
        background: linear-gradient(180deg, #fe5f67 0%, #df053a 100%);
      }
      &.A {
        background: linear-gradient(180deg, #b069ff 0%, #8331e9 100%);
      }
      &.S {
        background: linear-gradient(180deg, #FF965B 0%, #CE3925 100%);
      }
      &.SS {
        background: linear-gradient(180deg, #fba800 0%, #ea6300 100%);
      }
      &.SSS {
        background: linear-gradient(180deg, #f68300 0%, #e3321a 100%);
      }
    }
  }
}

::v-deep(.van-button) {
  border-radius: 4px;
}
.avatar-content {
  width: 3.75rem;
  height: 3.75rem;
  border-radius: 50%;
  overflow: hidden;
  > img {
    width: 100%;
    height: auto;
  }
}

.my-content {
  width: 100%;
  padding-top: 50px;
  padding-bottom: 55px;
  position: relative;
  > .content {
    position: relative;
    z-index: 2;
  }
  > .bg {
    width: 100%;
    height: 280px;
    background-repeat: no-repeat;
    background-position: center top;
    background-size: cover;
    position: absolute;
    top: 0;
    left: 0;
    z-index: 1;
  }
}

.award-content {
  margin-top: 1rem;
  padding: 0 16px;
  .first-content {
    width: 100%;
    height: 25.6vw;
    padding-top: 2.4vw;
    padding-left: 8.8vw;
    border-radius: 8px;
    overflow: hidden;
    background-color: #dfe2e5;
    background-image: url('./../../assets/imgs/me/award-bg.png');
    background-size: 100% 100%;
    background-repeat: no-repeat;
    background-position: center top;
    line-height: 1;
    > h2 {
      display: block;
      color: #fecc1c;
      font-size: 5vw;
      font-weight: bold;
      text-shadow: 1px 1px 0 #130052;
    }
    .info {
      margin: 0;
      font-size: 3.2vw;
      color: #fff;
      margin-top: 1.5vw;
      .info-txt {
        display: inline;
      }
    }
    .info-txt {
      font-size: 3.2vw;
      line-height: 3.2vw;
      color: #fff;
      margin-top: 1.5vw;
      text-shadow: 1px 1px 0 #130052;
      ::v-deep(span),
      span {
        color: #fecc1c;
        font-weight: bold;
        font-size: 3.4vw;
      }
    }
    > .btn {
      display: inline-block;
      text-align: center;
      height: 6vw;
      line-height: 6vw;
      border-radius: 6vw;
      padding: 0 15px;
      min-width: 20.5vw;
      background-color: #2e7bf1;
      color: #fff;
      font-size: 2.6vw;
      margin-top: 1.5vw;
      &.get {
        animation: heartBeat 1.5s infinite;
      }
    }
  }
  .invite-content {
    width: 100%;
    height: 25.6vw;
    padding-top: 3vw;
    padding-left: 7vw;
    border-radius: 8px;
    overflow: hidden;
    background-color: #dfe2e5;
    background-image: url('./../../assets/imgs/me/invite-bg.png');
    background-size: 100% 100%;
    background-repeat: no-repeat;
    background-position: center top;
    line-height: 1;
    position: relative;
    > h3 {
      color: #fff;
      font-size: 4.6vw;
      text-shadow: 1px 1px 0 rgba(#000000, 0.4);
      &.not-cn {
        font-size: 4vw;
        padding-right: 20vw;
      }
      :deep(span) {
        color: rgba(255, 223, 111, 1);
      }
    }
    > p {
      font-size: 2.8vw;
      color: rgba(214, 239, 255, 1);
      margin-top: 2vw;
      padding-right: 30vw;
      &.not-cn {
        font-size: 2.4vw;
        margin-top: 1vw;
        line-height: 1.2;
        color: #fecc1c;
      }
    }
    > .btn {
      display: inline-block;
      text-align: center;
      height: 6vw;
      line-height: 6vw;
      border-radius: 6vw;
      padding: 0 15px;
      min-width: 20.5vw;
      background-image: linear-gradient(
        rgba(255, 150, 91, 1),
        rgba(206, 57, 37, 1)
      );
      color: #fff;
      font-size: 2.6vw;
      margin-top: 2.5vw;
      &.not-cn {
        margin-top: 1vw;
      }
      &.is-ar {
        position: absolute;
        left: 7vw;
      }
    }
  }
}

.single-banner-content {
  padding: 0 16px;
  > .banner-content {
    width: 100%;
    height: 45px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: rgba(0, 0, 0, 0.8);
    padding-right: 12px;
    > .info {
      display: flex;
      align-items: center;
      margin: 0 !important;
      > img {
        width: 22px;
        height: 22px;
        margin-left: 9px;
      }
      > p {
        margin-left: 0.45rem;
        color: #fff;
        font-size: var(--van-cell-font-size);
      }
    }
    .van-icon {
      color: #fff;
      font-size: 12px;
    }
  }
}

.is-ar-cell-group {
  :deep(.van-cell__value) {
    text-align: left;
    padding-left: 5px;
  }
}

.btn-content {
  min-width: 70px;
  line-height: 68px;
  border: var(--site-main-color) 1px solid;
  color: var(--site-main-color);
  &.block {
    background-color: var(--site-main-color);
    color: #fff;
  }
}

.freeze-btn-content {
  display: flex;
  align-items: center;
  justify-content: space-around;
  margin-top: 15px;
  padding-bottom: 5px;
  :deep(.btn-content) {
    width: 40%;
  }
}

.freeze-num-content {
  display: flex;
  align-items: center;
  font-size: 12px;
  padding-top: 5px;
  > p {
    color: #999999;
    padding: 0 5px;
  }
  span {
    color: #D93232;
  }
  > i {
    font-size: 14px;
    color: #CCCCCC;
  }
}

.freeze-total-content {
  display: flex;
  align-items: center;
  > i {
    font-size: 14px;
    color: #CCCCCC;
    &.icon-shuaxin {
      color: #000;
      font-size: 16px;
      padding: 0 5px;
    }
  }
}

.level-progress {
  padding: 0 16px;
  display: flex;
  align-items: center;
  margin-top: 25px;
  position: relative;
  > .progress {
    flex: 1;
    background-color: #90A7FF;
    height: 7px;
    border-radius: 7px;
    position: relative;
    > .line {
      width: 0;
      height: 7px;
      border-radius: 7px;
      background-color: #FFEF64;
      transition: all 0.3s ease;
      position: absolute;
      top: 0;
      left: 0;
    }
    > .txt {
      position: absolute;
      background-color: #FFEF64;
      padding: 2px 6px;
      color: #3157EC;
      font-size: 11px;
      line-height: 1;
      top: -26px;
      transform: translateX(-50%);
      &::after {
        content: '';
        display: block;
        width: 0;
        height: 0;
        border-width: 7px 7px 0;
        border-style: solid;
        border-color: #FFEF64 transparent transparent;
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
      }
    }
  }
  > .name {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
    font-size: 11px;
    background-position: top center;
    background-repeat: no-repeat;
    background-size: cover;
    color: #fff;
    text-shadow: 1px 1px 0 rgba(0,0,0,.6);
    &:first-child {
      // background-color: #EFD55E;
      // color: #3157EC;
      margin-right: 5px;
    }
    &:last-child {
      margin-left: 5px;
      color: #fff;
      // background: linear-gradient(180deg, #FFB660 0%, #B80021 100%, #FF0000 100%);
    }
  }
}

.level-number-content {
  padding: 0 16px;
  margin-top: 10px;
  padding-bottom: 10px;
  > p {
    font-size: 12px;
    color: #fff;
    line-height: 1.5;
    :deep(span),
    span {
      color: #EFD55E;
      padding: 0 5px;
    }
  }
  > div {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 5px;
    > p {
      flex: 1;
      font-size: 12px;
      color: #fff;
      padding-right: 15px;
      line-height: 1.5;
      > span {
        color: #EFD55E;
        padding-left: 5px;
        &.em {
          padding: 0;
        }
      }
    }
  }
}

</style>
