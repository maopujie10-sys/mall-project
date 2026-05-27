<template>
  <div class="dialog-content">
    <van-action-sheet v-model="visible" :title="$t('请选择订单取消原因')" :round="false">
      <div class="cancel-content">
        <div class="item" v-for="(item, index) in reasonData" :key="index" :class="{'active': currentIndex === index}" @click="currentIndex = index">{{ item.txt }} <img v-if="currentIndex === index" :src="checkIcon" alt="" /></div>
      </div>
      <div class="btn-content">
        <div class="btn" :class="{'active': currentIndex !== null}" @click="cancelHandle">{{ $t('确认取消') }}</div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script>
import { ActionSheet, Dialog, Toast } from 'vant'
import {
  orderCancel
} from '@/API/user'
export default {
  name: 'CancelDialog',
  components:{
    [ActionSheet.name]:ActionSheet,
    [Dialog.name]:Dialog
  },
  props: {
    dialogShow: {
      type: Boolean,
      required: true,
      default: false
    },
    dialogData: {
      type: Object,
      required: true,
      default: () => {}
    }
  },
  computed: {
    visible: {
      get() {
        return this.dialogShow
      },
      set() {
        this.$emit('update:dialogShow', false)
      }
    }
  },
  watch: {
    visible(val) {
      if (!val) {
        this.currentIndex = null
      }
    }
  },
  data() {
    return {
      checkIcon: require('@/assets/image/me/check1.png'),
      currentIndex: null,
      reasonData: [{
        id: 1,
        txt: this.$t('不想要了')
      }, {
        id: 2,
        txt: this.$t('下错商品')
      }, {
        id: 3,
        txt: this.$t('订单重复')
      }, {
        id: 4,
        txt: this.$t('无法签收')
      }, {
        id: 5,
        txt: this.$t('其他原因')
      }]
    }
  },
  methods: {
    cancelHandle() {
      Dialog.confirm({
        title: this.$t('提示'),
        message: this.$t('确认取消吗？'),
        confirmButtonText: this.$t('确认'),
        cancelButtonText: this.$t('取消')
      }).then(() => {
        Toast.loading({
          duration: 0,
          message: this.$t('提交中'),
          forbidClick: true
        })

        const params = {
          orderId: this.dialogData.id,
          returnReason: this.reasonData[this.currentIndex].id
        }

        orderCancel(params).then(() => {
          Toast.clear()
          this.$emit('update:dialogShow', false)
          this.$emit('done', false)
        }).catch(() => {
          Toast.clear()
        })
      }).catch(() => {
        this.$emit('update:dialogShow', false)
      })
    }
  }
}
</script>

<style lang="scss" scoped>
  .dialog-content {
    * {
      box-sizing: border-box;
    }
    /deep/ .van-action-sheet__close {
      color: #333;
      font-size: 14px;
    }
    .cancel-content {
      padding: 0 10px;
      > .item {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 15px 0;
        color: #999;
        font-size: 16px;
        border-top: 1px solid #eee;
        > img {
          width: 14px;
          height: 14px;
          margin-left: 20px;
        }
        &.active {
        //   color: var(--main-color);
        color: var(--main-color);
        }
      }
    }
    .btn-content {
      padding: 10px 10px 30px 10px;
      > .btn {
        width: 100%;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        background-color: #eee;
        font-size: 16px;
        color: #888CA1;
        pointer-events: none;
        &.active {
          background-color: var(--main-color);
          color: #fff;
          pointer-events: auto;
        }
      }
    }
  }
</style>
