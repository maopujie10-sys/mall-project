<template>
  <div class="setup">
    <router-view />
  </div>
</template>

<script></script>

<style lang="scss" scoped>
html[dir='rtl']{
  .setup{
    margin-right: 52px;
    margin-left: 0;
  }
}
.setup {
  padding: 32px 0 32px 50px;

  /deep/ .form {
    margin-top: 50px;

    .el-input {
      width: 422px;
    }

    &-item {
      &__label {
        font-size: 14px;
        color: #333;
        font-weight: 500;
      }
    }

    .form-submit-btn {
      width: 100%;
      display: block;
      background-color: var(--color-main);
      color: #fff;
      height: 52px;
      margin-top: 50px;
    }
  }
}
</style>
