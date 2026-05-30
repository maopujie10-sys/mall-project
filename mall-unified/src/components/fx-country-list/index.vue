<template>
  <div class="intl-tel-input allow-dropdown w-full mt-1.5" @click="hideSubMenu = !hideSubMenu">
    <div class="flag-container w-full">
      <div class="selected-flag" style="width: 100%" :title="currentData.name + ': +' + currentData.dialCode"
      >
        <div :class="'iti-flag ' + currentData.code"></div>
        <div class="flex items-center h-full ml-10 text-base" style="color: #1F2025">{{ currentCountry }}</div>
      </div>
      <ul class="country-list" v-show="!hideSubMenu">
        <li v-for="item in frontCountriesArray" :key="item.id"
            :class="'country ' + (item.code == currentCode ? 'highlight' : '')"
            @click.stop="handleClick(item)">
          <div class="flag-box">
            <div :class="'iti-flag ' + item.code"></div>
          </div>
          <span class="country-name">{{ item.name }}</span>
          <span class="dial-code">+{{ item.dialCode }}</span>
        </li>
        <!--                <li class="divider"></li>-->
        <li class="van-hairline--bottom" v-for="item in countriesArray" :key="item.id"
            :class="'country ' + (item.code == currentCode ? 'highlight' : '')"
            @click.stop="handleClick(item)">
          <div class="flag-box">
            <div :class="'iti-flag ' + item.code"></div>
          </div>
          <span class="country-name">{{ item.name }}</span>
          <span class="dial-code">+{{ item.dialCode }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>


<script>
import countries from './countryList'

export default {
  props: {
    toFront: {
      type: Array,
      default: () => {
        return []
      }
    },
    countryCode: {
      type: String,
      default: Object.keys(countries)[0],
      validator(code) {
        var clearCode = String(code).toLowerCase()
        return !!countries[clearCode]
      }
    }
  },

  data() {
    console.log()
    return {
      currentCode: this.countryCode,
      hideSubMenu: true,
    }
  },

  computed: {
    currentData() {
      return countries[this.currentCode]
    },
    frontCountriesArray() {
      const toFrontCodes = {}
      this.toFront.forEach((code) => {
        const stringCode = String(code)
        const needObj = countries[stringCode]

        if (needObj) {
          toFrontCodes[stringCode] = needObj
        }
      })
      return toFrontCodes
    },
    countriesArray() {
      const countryCopie = {...countries}
      this.toFront.forEach((code) => {
        delete countryCopie[code]
      })
      return countryCopie
    },
    currentCountry() {
      return countries[this.currentCode].name.split(' (')[0]
    }
  },

  watch: {
    countryCode(newCode) {
      this.setCountry(countries[newCode])
    },
  },

  methods: {
    setCountry(item) {
      this.currentCode = item.code
      this.toFront.push(String(item.code))
      this.$emit('excountry', item)
    },
    handleClick(item) {
      console.log(item.name)
      this.currentCode = item.code;
      this.hideSubMenu = true;
      console.log(this.hideSubMenu)
      this.setCountry(item);
    },
  },

  mounted() {
    this.$emit('excountry', countries[this.countryCode])
  }
}
</script>


<style lang="scss" scoped>
@import "intl.css";

.intl-tel-input {
  height: 40px;
  color: #666;
  font-size: 14px;

  .country-list {
    width: 335px;
    height: 400px;
    margin-top: 12px;
  }
}

.item-list {

}
</style>
  