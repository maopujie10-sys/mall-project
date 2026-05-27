<template>
  <div class="shop-item-content">
    <div class="info-content">
      <div class="poster"><img :src="shopInfo.avatar" alt="" /></div>
      <div class="info">
        <div class="name">{{ shopInfo.name }}</div>
        <div class="text"><span>{{ $t('已售') }}：</span> {{ shopInfo.soldNum || '0' }}</div>
        <div class="text"><span>{{ $t('浏览量') }}：</span> {{ shopInfo.viewsNum || '0' }}</div>
        <div class="text"><span>{{ $t('好评率') }}：</span> {{ shopInfo.highOpinion || '0' }}%</div>
      </div>
      <div class="link" @click="openShop(shopInfo.id)">
        {{ $t('进入店铺') }}
        <img :src="arrow" alt="" /> 
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShopItemTwo',
  props: {
    shopInfo: {
      type: Object,
      required: true,
      default: function() {
        return {}
      }
    }
  },
  data () {
    return {
      arrow: require('@/assets/image/me/arrow3.png')
    }
  },
  methods: {
    openShop(id) {
      this.$router.push({
        path: '/shop',
        query: {
          id
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.shop-item-content {
  * {
    box-sizing: border-box;
  }
  margin-top: 10px;
  padding: 15px;
  border: 1px solid #eee;
  > .info-content {
    display: flex;
    align-items: center;
    > .poster {
      width: 63px;
      height: 63px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      > img {
        width: 100%;
        height: auto;
      }
    }
    > .info {
      flex: 1;
      width: 0;
      padding-left: 10px;
      padding-right: 5px;
      > .name {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 14px;
        margin-bottom: 6px;
      }
      > .text {
        font-size: 10px;
        color: #333;
        margin-bottom: 2px;
        &:last-child {
          margin-bottom: 0;
        }
      }
    }
    > .link {
      padding: 0 6px;
      height: 20px;
      align-items: center;
      font-size: 12px;
      color: var(--color-main);
      background: #FCF2E2;
      border: 1px solid var(--color-main);
      border-radius: 20px;
      > img {
        width: 4px;
        height: auto;
      }
    }
  }
  > .number-content {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 10px;
    border-top: 1px solid #eee;
    margin-top: 10px;
    > p {
      font-size: 10px;
      color: #333;
    }
  }
}
</style>
