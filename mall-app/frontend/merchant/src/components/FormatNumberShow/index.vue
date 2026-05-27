<template>
  <div style="display: inline-block">
    {{ showNumber }}
  </div>
</template>

<script>
export default {
  name: "FormatNumberShow",
  props: {
    data: {
      type: [Number, String],
      default: 0
    },
    currency: {
      type: Boolean,
      default: false
    },
    decimalPlaces: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      showNumber: 0,
      interval: null
    }
  },
  watch: {
    data() {
      this.showNumberFunc()
    }
  },
  mounted() {
    this.showNumberFunc()
  },
  methods: {
    showNumberFunc() {
      clearInterval(this.interval)
      let index = 0
      const origin = parseFloat(this.data) || 0
      const decLength = origin.toString().indexOf(".") > -1 ? origin.toString().split(".")[1].length : 0
      this.interval = setInterval(() => {
        index++
        let number = origin * (index / 100)
        if (decLength === 0) {
          number = parseInt(number)
        }
        this.showNumber = this.currency ? this.formatMoney(number) : this.formatNumber(number, decLength)
        if (index > 100) {
          clearInterval(this.interval)
          this.showNumber = this.currency ? this.formatMoney(origin) : this.formatNumber(origin, decLength)
        }
      }, 5)
    },
    formatNumber(value = 0, decLength = 0) {
      if (value) {
        //如果存在小数点，小数点的位数大于2且小于this.decimalPlaces，则保留小数点的位数
        let str = ""
        if (value.toString().indexOf(".") > -1) {
          //小数点的位数
          if (decLength <= 2) {
            str = value.toFloor(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",")
          } else {
            let unDecLength = (value * 1).toString().split(".")[1].length
            if (unDecLength < this.decimalPlaces) {
              str = value.toFloor(decLength).replace(/\B(?=(\d{3})+(?!\d))/g, ",")
            } else {
              value = value.toFloor(this.decimalPlaces) * 1
              let unDecLength = (value * 1).toString().split(".")[1].length
              str = (value.toFloor(unDecLength) + "").replace(/\B(?=(\d{3})+(?!\d))/g, ",")
            }
          }
        } else {
          if (this.decimalPlaces > 0) {
            str = value.toFloor(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",")
          } else {
            str = ('' + value).replace(/\B(?=(\d{3})+(?!\d))/g, ",")
          }
        }
        return str
      } else {
        return value
      }
    },
    formatMoney(price) {
      const options = {
        style: "currency",
        currency: "USD",
      }
      const number = ((price * 1).toFloor(2) * 1).toLocaleString("en", options)
      return number
    }
  }
}
</script>

<style scoped></style>
