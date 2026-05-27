<template>
  <el-dialog
    class="es-dialog"
    :visible.sync="dialogVisible"
    :center="true"
    :append-to-body="true"
    width="600px"
  >
    <div slot="title" class="dialog-title">
      <span>{{ $t('message.home.selectDeliveryAddress') }}</span>
    </div>
    <div class="address-modal-content dialog-content">
      <div
          :class="{
          'address-active': paySelectAddress.id === item.id,
          item: true,
        }"
          v-for="item in addressList"
          :key="item.id"
          @click="selectAddress(item)"
      >
        <div class="info">
          <span class="name">{{ item.contacts }}</span>
          <span class="mobile">&nbsp;&nbsp;+{{ item.phone }}</span>
        </div>
        <div class="address">
          {{ item.country }} {{ item.province }} {{ item.city }}
          {{ item.address }}
        </div>
      </div>
      <div
          class="item"
          @click="changeAddressView"
      >
        {{$t('message.home.addNewAddress')}}
      </div>
    </div>
    <span slot="footer"></span>
  </el-dialog>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex'
export default {
  name: 'EsPayAddress',
  props: {
    show: {
      type: Boolean,
      default: false,
    },
  },
  model: {
    prop: 'show',
    event: 'update',
  },
  data() {
    return {
      dialogVisible: false,
    }
  },
  computed: {
    ...mapGetters({
      addressList: 'user/addressList',
      // defaultAddress: 'user/defaultAddress',
      paySelectAddress: 'user/paySelectAddress',
    }),
  },
  watch: {
    dialogVisible(newValue, oldValue) {
      if (newValue !== oldValue) {
        this.$emit('update', newValue)
        if (newValue) {
          this.requestAddressList()
        }
      }
    },
    show(newValue, oldValue) {
      if (newValue !== oldValue) this.dialogVisible = newValue
    },
  },
  mounted() {
    this.dialogVisible = this.show
  },
  methods: {
    ...mapMutations({
      updatePaySelectAddress: 'user/updatePaySelectAddress',
    }),
    ...mapActions({
      requestAddressList: 'user/requestAddressList',
      requestAddressAdd: 'user/requestAddressAdd',
    }),
    changeAddressView(){
      this.$emit('showAddAddressView')
    },
    selectAddress(item) {
      console.log('选择地址', item)
      this.updatePaySelectAddress(item)
      this.dialogVisible = false
    },
  },
}
</script>

<style lang="scss" scoped>
.item {
  width: 100%;
  border: 1px solid var(--color-border);
  padding: 12px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 20px;
  &:hover {
    border-color: var(--color-main);
  }
  .info {
    margin-bottom: 8px;
  }
}

.address-active {
  border-color: var(--color-main);
}
</style>
