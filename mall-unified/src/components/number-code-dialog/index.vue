<template>
  <div :class="{'active': modelValue}" class="number-code-dialog">
    <div class="code-content">
      <div class="title">{{ t('entryVerifyCode') }}</div>
      <div class="input-content">
        <div class="input">
          <input type="text" v-model="verCode" :placeholder="t('verificationCode')">
        </div>
        <div @click="makCode">
          <canvas id="s-canvas" :width="contentWidth" :height="contentHeight"></canvas>
        </div>
      </div>
      <van-button type="custom" block @click="submitHandle">{{ t('确定') }}</van-button>
    </div>
    <div class="code-bg" @click="closeDialog" />
  </div>
</template>

<script setup name="NumberCodeDialog">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Toast } from 'vant'

const { t } = useI18n()
const $emit = defineEmits(['update:modelValue', 'done'])
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const verCode = ref('')
const identifyCode = ref('')
const backgroundColorMin = ref(180)
const backgroundColorMax = ref(240)
const contentWidth = ref(100)
const contentHeight = ref(35)
const colorMin = ref(50)
const colorMax = ref(160)
const fontSizeMin = ref(32)
const fontSizeMax = ref(40)
const lineColorMin = ref(40)
const lineColorMax = ref(100)

// 生成一个随机数
const randomNum = (min, max) => {
  return Math.floor(Math.random() * (max - min) + min)
}

// 生成一个随机的颜色
const randomColor = (min, max) => {
  let r = randomNum(min, max);
  let g = randomNum(min, max);
  let b = randomNum(min, max);
  return "rgb(" + r + "," + g + "," + b + ")";
}

const drawPic = () => {
  let canvas = document.getElementById("s-canvas");
  let ctx = canvas.getContext("2d");
  ctx.textBaseline = "bottom";
  // 绘制背景
  ctx.fillStyle = randomColor(backgroundColorMin.value, backgroundColorMax.value);
  ctx.fillRect(0, 0, contentWidth.value, contentHeight.value);
  // 绘制文字
  for (let i = 0; i < identifyCode.value.length; i++) {
    drawText(ctx, identifyCode.value[i], i);
  }
  drawLine(ctx);
  drawDot(ctx);
}

const drawText = (ctx, txt, i) => {
  ctx.fillStyle = randomColor(colorMin.value, colorMax.value);
  ctx.font = randomNum(fontSizeMin.value, fontSizeMax.value) + "px SimHei";
  let x = (i + 1) * (contentWidth.value / (identifyCode.value.length + 1));
  let y = randomNum(fontSizeMax.value, contentHeight.value - 5);
  var deg = randomNum(-15, 15);
  // 修改坐标原点和旋转角度
  ctx.translate(x, y);
  ctx.rotate((deg * Math.PI) / 180);
  ctx.fillText(txt, 0, 0);
  // 恢复坐标原点和旋转角度
  ctx.rotate((-deg * Math.PI) / 180);
  ctx.translate(-x, -y);
}

const drawLine = (ctx) => {
  // 绘制干扰线
  for (let i = 0; i < 4; i++) {
    ctx.strokeStyle = randomColor(
      lineColorMin.value,
      lineColorMax.value
    );
    ctx.beginPath();
    ctx.moveTo(
      randomNum(0, contentWidth.value),
      randomNum(0, contentHeight.value)
    );
    ctx.lineTo(
      randomNum(0, contentWidth.value),
      randomNum(0, contentHeight.value)
    );
    ctx.stroke();
  }
}

const drawDot = (ctx) => {
  // 绘制干扰点
  for (let i = 0; i < 10; i++) {
    ctx.fillStyle = randomColor(0, 100);
    ctx.beginPath();
    ctx.arc(
      randomNum(0, contentWidth.value),
      randomNum(0, contentHeight.value),
      1,
      0,
      2 * Math.PI
    );
    ctx.fill();
  }
}

const refreshCode = () => {
  identifyCode.value = ''
  makCode()
}

const makCode = () => {
  const numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
  let rTxt = ''
  for (let i = 0; i < 4; i++) {
    const index = Math.floor(Math.random() * numbers.length)
    rTxt += numbers[index]
  }
  identifyCode.value = rTxt
  drawPic()
}

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      refreshCode()
    } else {
      verCode.value = ''
    }
  }
)

const closeDialog = () => {
	$emit('update:modelValue', false)
}

const submitHandle = () => {
  if (!verCode.value) {
    Toast(t('验证码不能为空'))
    return
  }
  if (verCode.value === identifyCode.value) {
    $emit('done')
    closeDialog()
  } else {
    Toast(t('验证码不正确'))
  }
}
</script>

<style lang="scss" scoped>
.number-code-dialog {
		width: 100%;
		height: 100vh;
		pointer-events: none;
		position: fixed;
		top: 0;
		left: 0;
		z-index: 98;
		opacity: 0;
		> div {
			position: fixed;
			left: 0;
			&.code-content {
				width: 90vw;
				height: 200px;
				left: 5vw;
        top: 50%;
        margin-top: -100px;
				background-color: #fff;
				border-radius: 8px;
				z-index: 9;
				animation-duration: .75s;
        padding: 0 20px;
				> .title {
					width: 100%;
					height: 60px;
					text-align: center;
					line-height: 60px;
          color: #000;
          font-size: 16px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
				}
        > .input-content {
          width: 100%;
          display: flex;
          align-items: center;
          border: 1px solid #ddd;
          border-radius: 4px;
          padding: 5px 15px;
          color: #000;
          > .input {
            flex: 1;
            height: 100%;
            padding-right: 15px;
            background-color: #fff;
            > input {
              background-color: #fff;
              width: 100%;
            }
          }
        }
			}
			&.code-bg {
				top: 0;
				width: 100%;
				height: 100vh;
				background-color: rgba(0, 0, 0, .4);
				z-index: 8;
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

  .van-button--custom {
    color: #fff;
    background: var(--site-main-color) !important;
    margin-top: 20px;
  }
</style>
