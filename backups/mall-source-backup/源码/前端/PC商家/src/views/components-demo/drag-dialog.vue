<template>
  <div class="components-container">
    <el-button type="primary" @click="dialogTableVisible = true">{{ $t('open') }} a Drag{{ $t('Dialog') }}</el-button>
    <el-dialog v-el-drag-dialog :visible.sync="dialogTableVisible" title="Shipping address" @dragDialog="handleDrag">
      <el-select ref="select" v-model="value" :placeholder="$t('请选择')">

        <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value"/>

      </el-select>
      <el-table :data="gridData">
        <el-table-column label="Date" property="date" width="150"/>
        <el-table-column label="Name" property="name" width="200"/>
        <el-table-column label="Address" property="address"/>
      </el-table>
    </el-dialog>
  </div>
</template>

<script>
import elDragDialog from '@/directive/el-drag-dialog' // base on element-ui

export default {
  name: 'DragDialogDemo',
  directives: {elDragDialog},
  data() {
    return {
      dialogTableVisible: false,
      options: [
        {value: this.$t('选项1'), label: this.$t('黄金糕')},
        {value: this.$t('选项2'), label: this.$t('双皮奶')},
        {value: this.$t('选项3'), label: this.$t('蚵仔煎')},
        {value: this.$t('选项4'), label: this.$t('龙须面')}
      ],
      value: '',
      gridData: [{
        date: '2016-05-02',
        name: 'John Smith',
        address: 'No.1518,  Jinshajiang Road, Putuo District'
      }, {
        date: '2016-05-04',
        name: 'John Smith',
        address: 'No.1518,  Jinshajiang Road, Putuo District'
      }, {
        date: '2016-05-01',
        name: 'John Smith',
        address: 'No.1518,  Jinshajiang Road, Putuo District'
      }, {
        date: '2016-05-03',
        name: 'John Smith',
        address: 'No.1518,  Jinshajiang Road, Putuo District'
      }]
    };
  },
  methods: {
    // v-el-drag-dialog onDrag callback function
    handleDrag() {
      this.$refs.select.blur()
    }
  }
}
</script>
