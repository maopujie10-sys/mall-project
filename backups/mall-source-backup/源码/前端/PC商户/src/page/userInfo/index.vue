<template>
  <div class="user-info">
    <EsHeaderView />
    <div class="app-container">
      <navBar />
      <div class="set-container">
        <router-view />
      </div>
    </div>
    <EsFooterView />
  </div>
</template>
<script>
  import navBar from "./navBar.vue";
  export default {
    components: {
      navBar,
    },
  };
</script>
<style lang="scss" scoped>
html[dir="rtl"] {
    :deep(.info_page_container)  {
    margin-left: 0;
    margin-right: 34px;
  }
}
  .user-info {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .header {
    margin-bottom: 0;
  }

  .app-container {
    margin-bottom: 50px;
    display: flex;
    width: 1200px;
    flex: 1;

    .set-container {
      flex: 1;
    }
  }

  /deep/ .info_page_container {
    margin-top: 24px;
    margin-left: 34px;
  }

  /deep/ .page-title {
    font-weight: 700;
    font-size: 24px;
    color: #333;
  }
</style>
