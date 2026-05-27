<template>
  <div class="CommonProblem">
    <van-nav-bar
        fixed
        :title="$t('语言设置')"
        left-arrow
        @click-left="onClickLeft"
    />
    <div style="width: 100%;height: 46px;"></div>
    <div class="language-content">
      <div v-for="(item, index) in lang" :key="index" class="item" @click="handleSetLang(item.key)">
        <div class="content">
          <img :src="item.icon" alt="" class="nation">
          <div class="title">{{item.title}}</div>
        </div>
        <img v-if="item.key==$i18n.locale" :src="checkIcon" alt="" class="check">
      </div>
    </div>
  </div>
</template>
<script>
import {mapGetters, mapMutations} from "vuex";

export default {
  data() {
    return {
      lang: [
        {
          title:'简体中文',
          key: 'zh-CN',
          icon: require('@/assets/image/language/cn.png')
        },
        {
          title: 'English',
          key: 'en-US',
          icon: require('@/assets/image/language/usa.png')
        },
        {
          title:'繁体中文',
          key: 'CN',
          icon: require('@/assets/image/language/tw.png')
        }
      ],
      checkIcon: require('@/assets/image/language/check.png')
    }
  },
  computed: {
    ...mapGetters({
      activeLang: 'language'
    })
  },
  methods:{
    ...mapMutations(['setLanguage']),
    handleSetLang(lang) {
      // 设置i18n.locale 组件库会按照上面的配置使用对应的文案文件
      this.$i18n.locale = lang
      // 提交mutations
      this.setLanguage(lang)
      history.go(-1)
    },
    onClickLeft() {
      // console.log(this.$i18n.locale)
      history.go(-1)
    },
  }
}
</script>
<style lang="scss" scoped>
.language-content {
  > .item {
    box-sizing: border-box;
    width: 100%;
    height: 50px;
    padding: 0 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #fff;
    border-bottom: 1px solid #eee;
    &:last-child {
      border-bottom: none;
    }
    > .content {
      display: flex;
      > .nation {
        width: 18px;
        height: 18px;
      }
      > .title {
        font-size: 14px;
        color: #333;
        margin-left: 11px;
      }
    }
    > .check {
      width: 7.74px;
      height: 8.4px;
    }
  }
}
</style>
