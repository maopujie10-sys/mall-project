<template>
  <div class="dialog-content">
    <van-action-sheet v-model="visible" :title="$t('提醒发货')" :round="false">
      <div class="remind-content">
        <p>{{ $t('提醒发货后，商家会收到提醒') }}</p>
        <p>{{ $t('只能提醒1次哟~') }}</p>
      </div>
      <div class="btn-content">
        <div class="btn" @click="submitHandle">{{ $t('提醒商家') }}</div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script>
import { ActionSheet, Toast } from 'vant'
export default {
  name: 'RemindDialog',
  components:{
    [ActionSheet.name]:ActionSheet,
    [Toast.name]:Toast
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
  methods: {
    submitHandle() {
      Toast.loading({
        duration: 0,
        message: this.$t('提交中'),
        forbidClick: true
      })

      const data = localStorage.getItem('remindStore') ? JSON.parse(localStorage.getItem('remindStore')): []
      if (!data.includes(this.dialogData.id)) {
        data.push(this.dialogData.id)
      }
      
      localStorage.setItem('remindStore', JSON.stringify(data))

      setTimeout(() => {
        Toast.clear()
        this.$emit('update:dialogShow', false)
        this.$emit('done', false)
      }, 1000);
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
    .remind-content {
      padding: 30px 20px;
      padding-top: 10px;
      > p {
        font-size: 14px;
        color: #000;
        line-height: 21px;
        text-align: center;
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
        background-color: var(--main-color);
        font-size: 16px;
        color: #fff;
      }
    }
  }
</style>
