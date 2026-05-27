<template>
  <section class="app-main">
    <transition mode="out-in" name="fade-transform">
      <keep-alive :include="cachedViews" v-if="keepAlive">
        <router-view :key="key" v-loading="loading" class="app-main-content"/>
      </keep-alive>
      <router-view v-else :key="key" v-loading="loading" class="app-main-content"/>
    </transition>
  </section>
</template>

<script>
export default {
  name: "AppMain",
  computed: {
    cachedViews() {
      return this.$store.state.tagsView.cachedViews;
    },
    key() {
      return this.$route.path;
    },
    loading() {
      return this.$store.getters.loading;
    },
  },
  data() {
    return {
      keepAlive: true,
    };
  },
  watch: {
    "$route"(to, from) {
      if (to.meta.keepAlive) {
        this.keepAlive = true;
      } else {
        this.keepAlive = false;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.app-main {
  /* 50= navbar  50  */
  min-height: calc(100vh - 94px);
  width: 100%;
  position: relative;
  overflow: auto;
  background-color: #f0f2f5;

  .app-main-content {
    min-height: calc(100vh - 94px);
  }
}

.fixed-header + .app-main {
  padding-top: 50px;
}

.hasTagsView {
  .app-main {
    /* 60 = navbar = 60  */
    //min-height: calc(100vh - 60px);
    //height: calc(100vh - 70px);
    //overflow: auto;
    background-color: #f0f2f5;
  }

  .fixed-header + .app-main {
    padding-top: 94px;
  }
}
</style>

<style lang="scss">
// fix css style bug in open el-dialog
.el-popup-parent--hidden {
  .fixed-header {
    padding-right: 15px;
  }
}

</style>
