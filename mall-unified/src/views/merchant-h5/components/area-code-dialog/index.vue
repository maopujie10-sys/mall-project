<template>
  <div :class="{'active': modelValue}" class="area-code-dialog">
    <div :class="{'pc': !isMobile()}" class="code-content">
      <div class="title">{{ t('selectArea') }}</div>
      <div class="search-content">
        <div class="content">
          <input v-model="keywords" type="text" :placeholder="t('entrynational')">
        </div>
      </div>
      <div class="scroll-content">
        <div class="countries-content" :class="{'is-ar': isArLang}">
					<template v-if="countriesData.length">
						<div v-for="item in countriesData" :key="item.code" class="item" @click="choiceHandle(item)">
							<div class="name">{{ item.name }}</div>
							<div class="code">{{ item.dialCode }}</div>
						</div>
					</template>
          <div v-else class="no-data">{{ t('noData') }}</div>
        </div>
      </div>
    </div>
    <div class="code-bg" @click="closeDialog" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { arLangCheck } from '@/utils/arLangCheck'
import { countries } from './config/countries.js'
import { isMobile } from '@/utils'

const { t } = useI18n()
const $emit = defineEmits(['update:modelValue', 'done'])
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const isArLang = arLangCheck()

const keywords = ref('')

const countriesData = computed(() => {
	const data = countries.filter(item => {
		const key = keywords.value.toLowerCase()
		const name = item.name.toLowerCase()
		const dialCode = String(item.dialCode)
		if (isNaN(key)) {
			return name.indexOf(key) > -1
		} else {
			return dialCode === key
		}
	})
	return keywords.value ? data : countries
})

const closeDialog = () => {
	$emit('update:modelValue', false)
}

const choiceHandle = (data) => {
	$emit('done', data)
	closeDialog()
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
				width: 100%;
				height: 80vh;
				bottom: 0;
				background-color: #fff;
				border-top-left-radius: 16px;
				border-top-right-radius: 16px;
				z-index: 999999;
				animation-duration: .75s;
				&.pc {
					width: 600px;
					left: 50%;
					bottom: 10vh;
					border-radius: 16px;
					margin-left: -300px;
				}
				> .title {
					width: 100%;
					height: 60px;
					text-align: center;
					line-height: 60px;
          color: #000;
          font-size: 18px;
				}
				> .search-content {
					padding: 0 15px;
					margin-bottom: 15px;
					> .content {
						height: 44px;
						border-radius: 44px;
						background-color: #f8f8f8;
						display: flex;
						align-items: center;
						padding: 0 20px;
            color: #000;
            font-size: 14px;
						> input {
							flex: 1;
              color: #000;
              width: 100%;
              border: none;
              background-color: transparent;
						}
					}
				}
				> .scroll-content {
					height: calc(80vh - 119px);
          overflow-y: scroll;
					.countries-content {
						&.is-ar {
							> .item > .name {
								padding-left: 10px;
								padding-right: 0;
							}
						}
						> .item {
							width: 100%;
							display: flex;
							align-items: center;
							padding: 8px 15px;
							> .name {
								flex: 1;
								padding-right: 10px;
								font-size: 14px;
                color: #666;
							}
							> .code {
								font-size: 16px;
								color: #000;
							}
						}
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
	.no-data {
		width: 100%;
		height: 200px;
		color: #333;
		display: flex;
		align-items: center;
		justify-content: center;
	}
</style>
