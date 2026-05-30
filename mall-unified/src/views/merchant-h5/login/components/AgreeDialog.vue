<template>
  <div :class="{'active': modelValue}" class="area-code-dialog">
    <div class="code-content">
      <div class="title">{{ t('用户协议') }}</div>
      <div class="scroll-content">
        <login-agreement />
      </div>
      <div class="btn">
        <van-button type="custom" size="small" @click="doneHandle">{{ t('我已阅读') }}</van-button>
      </div>
    </div>
    <div class="code-bg" @click="closeDialog" />
  </div>
</template>

<script setup name="AgreeDialog">
import { useI18n } from 'vue-i18n'
import LoginAgreement from '@/views/login-agreement/index.vue'

const { t } = useI18n()
const $emit = defineEmits(['update:modelValue', 'done'])
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const closeDialog = () => {
	$emit('update:modelValue', false)
}

const doneHandle = () => {
  $emit('done')
  $emit('update:modelValue', false)
}

</script>

<style lang="scss" scoped>
	.area-code-dialog {
		width: 100%;
		height: 100vh;
		pointer-events: none;
		position: fixed;
		top: 0;
		left: 0;
		z-index: 999998;
		opacity: 0;
		> div {
			position: fixed;
			left: 0;
			&.code-content {
				width: calc(100vw - 30px);
				height: 80vh;
				bottom: 10vh;
        left: 15px;
				background-color: #fff;
				border-radius: 16px;
				z-index: 999999;
				animation-duration: .75s;
				> .title {
					width: 100%;
					height: 60px;
					text-align: center;
					line-height: 60px;
          color: #000;
          font-size: 18px;
				}
				> .scroll-content {
					height: calc(80vh - 119px);
          overflow-y: scroll;
				}
        > .btn {
          display: flex;
          justify-content: center;
          padding-top: 15px;
          .van-button--custom {
            color: #fff;
            background: #1552f0 !important;
            padding: 10px 20px !important;
            border-radius: 4px;
          }
        }
			}
			&.code-bg {
				top: 0;
				width: 100%;
				height: 100vh;
				background-color: rgba(0, 0, 0, .4);
				z-index: 999998;
				opacity: 0;
				transition: all 0.3s ease;
			}
		}
		&.active {
			pointer-events: auto;
			opacity: 1;
			> .code-content {
				animation-name: bounceInUp;
			}
			> .code-bg {
				opacity: 1;
			}
		}
	}
</style>
