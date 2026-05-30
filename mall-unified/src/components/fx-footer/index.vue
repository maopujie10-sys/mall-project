<template>
  <div class="relative z-30 footer">
    <van-tabbar route v-model="active" :active-color="themeColor[colorMode]" fixed safe-area-inset-bottom>
      <van-tabbar-item name="shop" to="/shop">
        <span>{{ t('footerShop') }}</span>
        <template #icon="props">
          <img :src="props.active ? icon.shop.active : icon.shop.inactive" />
        </template>
      </van-tabbar-item>
      <van-tabbar-item name="trade" to="/product">
        <span>{{ t('footerProduct') }}</span>
        <template #icon="props">
          <img :src="props.active ? icon.product.active : icon.product.inactive" />
        </template>
      </van-tabbar-item>
      <van-tabbar-item name="order" to="/order" :badge="badgeNum" :class="{'hide-badge': !badgeNum}">
        <span>{{ t('footerOrder') }}</span>
        <template #icon="props">
          <img :src="props.active ? icon.order.active : icon.order.inactive" />
        </template>
      </van-tabbar-item>
      <van-tabbar-item name="mine" to="/my">
        <span>{{ t('footerMy') }}</span>
        <template #icon="props">
          <img :src="props.active ? icon.home.active : icon.home.inactive" />
        </template>
      </van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { themeColor, needChangeMode } from '@/config'
import { useOrderStore } from "@/store/order.js";
import { getImg } from '@/utils'
const { t } = useI18n()
const active = ref('home')

const orderStore = useOrderStore()

const modeType = import.meta.env.MODE
const colorMode = needChangeMode.includes(modeType) ? modeType : 'main'

const badgeNum = computed(() => {
  const num = Number(orderStore.num)
  return isNaN(num) ? '' : num > 99 ? '99+' : num
})

// 底部列表
const icon = {
  shop: {
    active: getImg(`imgs/footer/${colorMode}/shop-active.png`),
    inactive: getImg('imgs/footer/shop-inactive.png'),
  },
  product: {
    active: getImg(`imgs/footer/${colorMode}/product-active.png`),
    inactive: getImg('imgs/footer/product-inactive.png'),
  },
  order: {
    active: getImg(`imgs/footer/${colorMode}/order-active.png`),
    inactive: getImg('imgs/footer/order-inactive.png'),
  },
  home: {
    active: getImg(`imgs/footer/${colorMode}/home-active.png`),
    inactive: getImg('imgs/footer/home-inactive.png'),
  }
}

</script>

<style lang="scss" scoped>
:deep(.van-tabbar-item__text) {
  font-size: 12px;
}

:deep(.van-tabbar-item) {
  &.hide-badge {
    .van-badge {
      display: none;
    }
  }
}
</style>