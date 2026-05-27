<template>
  <div>
    <balance></balance>
    <count></count>
    <visit></visit>
  </div>
</template>

<script>
import balance from "./balance.vue";
import count from "./count.vue";
import visit from "./visit.vue";
export default {
  components: {
    balance,
    count,
    visit,
  },
};
</script>
