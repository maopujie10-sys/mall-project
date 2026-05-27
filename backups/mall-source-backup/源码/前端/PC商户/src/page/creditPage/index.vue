<template>
  <div>
    <EsHeaderView />
    <router-view />
    <EsFooterView />
  </div>
</template>

<script>
  import { mapGetters } from "vuex";
  export default {
    computed: {
      ...mapGetters(["isLogin"]),
    },
    created() {
      // if (!this.isLogin) {
      //   this.$message({
      //     message: this.$t("message.home.notLogin"),
      //     type: "warning",
      //   });
      //   this.$router.push("/login");
      // }
    },
  };
</script>

<style lang="scss" scoped></style>
