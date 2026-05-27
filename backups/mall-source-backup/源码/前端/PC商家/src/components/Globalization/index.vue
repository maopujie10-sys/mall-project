<template>
  <div class="globalization">
    <el-dropdown :placement="['ar'].includes(currentLanguage)?'bottom-start':'bottom-end'" size="medium" trigger="click"
                 @command="handleClick">
      <div class="flex items-center" style="position: relative;cursor: pointer">
        <div class="ml-14 mr-18 font-14 font-400 lang-img"
        >
          <div style="line-height: 20px;margin-right: 12px">{{ languageName }}</div>
          <img :src="langImg" alt="" class="w-21 h-21 mr-6 lang-icon" style="margin-right: 6px;"/>
        </div>
        <div style="width: 24px;transform: translateX(1px)"><i class="el-icon-caret-bottom"></i></div>
      </div>
      <el-dropdown-menu slot="dropdown" class="project-dropdown">
        <div style="padding: 0 12px;box-sizing: border-box;height: 46px;" v-if="false">
          <el-input v-model="searchLanguage" suffix-icon="el-icon-search" class="icon-search"
                    @input="searchLanguages"></el-input>
        </div>
        <div class="project-dropdown-content">
          <div class="project-dropdown-list">
            <el-dropdown-item v-for="(item, index) in languageList" :key="index + item" :command="item.value"
                              v-if="item.show">
              <div :class="['ar'].includes(currentLanguage)?'so-dropdown-item rtl':'so-dropdown-item'">
                <img :src="icon[item.code]" alt="" class="w-21 h-21 mr-6 lang-icon"
                     style="border: solid 1px #e5e5e5;border-radius: 50%"/>
                <span style="line-height: 22px">{{ item.name }}</span>
              </div>
            </el-dropdown-item>
          </div>
        </div>
      </el-dropdown-menu>
    </el-dropdown>
  </div>
</template>

<script>
import {setStorage} from "@/utils/utis";
import {i18n} from "@/lang";
import {mapGetters, mapMutations} from "vuex";

export default {
  name: "Globalization",
  data() {
    return {
      icon: {
        en: require('@/assets/images/nav/langIcon/en.png'),
        cn: require('@/assets/images/nav/langIcon/cn.png'),
        tw: require('@/assets/images/nav/langIcon/tw.png'),
        de: require('@/assets/images/nav/langIcon/de.png'),
        fr: require('@/assets/images/nav/langIcon/fr.png'),
        ja: require('@/assets/images/nav/langIcon/ja.png'),
        ko: require('@/assets/images/nav/langIcon/ko.png'),
        ms: require('@/assets/images/nav/langIcon/ms.png'),
        th: require('@/assets/images/nav/langIcon/th.png'),
        pt: require('@/assets/images/nav/langIcon/pt.png'),
        es: require('@/assets/images/nav/langIcon/es.png'),
        ru: require('@/assets/images/nav/langIcon/ru.png'),
        el: require('@/assets/images/nav/langIcon/el.png'),
        it: require('@/assets/images/nav/langIcon/it.png'),
        tr: require('@/assets/images/nav/langIcon/tr.png'),
        af: require('@/assets/images/nav/langIcon/af.png'),
        ph: require('@/assets/images/nav/langIcon/ph.png'),
        ar: require('@/assets/images/nav/langIcon/ar.png'),
        vi: require('@/assets/images/nav/langIcon/vi.png'),
        id: require('@/assets/images/nav/langIcon/id.png'),
        hi: require('@/assets/images/nav/langIcon/hi.png'),
      },
      langImg: require('@/assets/images/nav/langIcon/en.png'),
      thisLanguages: [],
      languageName: 'English',
      searchLanguage: '',
      languageList: [],
    }
  },
  computed: {
    ...mapGetters(["currentLanguage", "languages", "lang"]),
  },
  watch: {
    currentLanguage: {
      immediate: true,
      deep: false,
      handler(val) {
        this.changeLang(val)
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      setTimeout(() => {
        this.changeLang(this.currentLanguage)
      }, 300)
    })
    this.thisLanguages = this.languages.filter(item => item.show)
    this.languageList = [...this.thisLanguages]
  },
  methods: {
    ...mapMutations('language', ['setCurrentLanguage']),
    searchLanguages() {
      this.languageList = this.thisLanguages.filter(item => {
        return item.name.indexOf(this.searchLanguage) > -1 || item.value.indexOf(this.searchLanguage) > -1 || item.code.indexOf(this.searchLanguage) > -1
      })
    },
    handleClick(item) {
      setStorage('merchant_pc_lang', item)
      this.$router.go(0)
    },
    changeLang(val) {
      this.setCurrentLanguage(val)
      this.langImg = this.icon[this.lang]
      this.languageName = (this.thisLanguages.find(item => item.value === val) || {name: 'English'}).name
      i18n.locale = this.$store.getters.lang;
    },
  }
}
</script>

<style scoped lang="scss">

.project-dropdown {
  //设置高度才能显示出滚动条 !important
  height: 215px;

  .project-dropdown-content {
    height: 200px;
    overflow-x: hidden;
    overflow-y: auto;

    .project-dropdown-list {
      overflow-y: auto;

      &::-webkit-scrollbar {
        width: 5px;
        height: 5px;
        background-color: #F5F5F5;
      }

      &::-webkit-scrollbar-track {
        //-webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.3);
        border-radius: 10px;
        background-color: #F5F5F5;
      }
    }
  }
}


.project-dropdown-content::-webkit-scrollbar {
  width: 5px;
  height: 5px;
  background-color: #F5F5F5;
}

.project-dropdown-content::-webkit-scrollbar-track {
  //-webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.3);
  border-radius: 10px;
  background-color: #F5F5F5;
}

.lang-img {
  position: absolute;
  display: flex;
  justify-content: flex-end;
  width: 110px;
  right: 0px;
}

.globalization {
  width: 100px;
  display: flex;
  justify-content: flex-end;
  margin-left: 24px;
}

.so-dropdown-item {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  height: 40px;
}
</style>
