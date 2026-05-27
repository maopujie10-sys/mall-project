<template>
  <div>
    <div v-if="loading" class="container spinning-dots-scaled"></div>
    <slot v-else></slot>
  </div>
</template>
<script>
export default {
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
  },
  name: 'EsLoading',
}
</script>
<style lang="scss">
.loading {
  width: 100%;
  height: 100%;
}
.container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 175px;
  overflow: hidden;
  width: 100%;
  position: relative;
}
@-webkit-keyframes spin {
  to {
    -webkit-transform: rotate(360deg);
    transform: rotate(360deg);
  }
}

@keyframes spin {
  to {
    -webkit-transform: rotate(360deg);
    transform: rotate(360deg);
  }
}

.spinning-dots-scaled {
  &::before {
    display: block;
    animation: spin 1.5s infinite linear;
    border-radius: 8px;
    box-shadow: 20px 0px 0 -4px var(--color-main),
      12.4698px 15.63663px 0 -4px var(--color-main),
      -4.45042px 19.49856px 0 -3px var(--color-main),
      -18.01938px 8.67767px 0 -2px var(--color-main),
      -18.01938px -8.67767px 0 -1px var(--color-main),
      -4.45042px -19.49856px 0 1px var(--color-main),
      12.4698px -15.63663px 0 2px var(--color-main);
    content: '';
    height: 8px;
    width: 8px;
  }
}
</style>
