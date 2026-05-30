<template>
  <div ref="chart" class="kg-container"></div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const chart = ref(null)
let instance = null

const props = defineProps({
  data: { type: Object, default: () => ({}) }
})

function buildGraph() {
  if (!chart.value) return
  const nodes = [], links = [], categories = [
    { name: '商品' }, { name: '用户' }, { name: '订单' }, { name: '品类' }
  ]
  const d = props.data
  if (d.products) d.products.forEach((p,i) => nodes.push({id:p.id||`p${i}`,name:p.name,category:0,symbolSize:20+Math.random()*20}))
  if (d.users) d.users.forEach((u,i) => nodes.push({id:u.id||`u${i}`,name:u.name,category:1,symbolSize:15}))
  if (d.orders) d.orders.forEach(o => {links.push({source:o.user_id||'',target:o.goods_id||'',value:o.amount||1})})
  if (d.categories) d.categories.forEach((c,i) => nodes.push({id:`cat${i}`,name:c,category:3,symbolSize:30}))

  const option = {
    tooltip: {}, legend: [{ data: categories.map(c => c.name) }],
    series: [{
      type: 'graph', layout: 'force', roam: true, draggable: true,
      categories, data: nodes, links,
      force: { repulsion: 300, edgeLength: [80,200] },
      lineStyle: { color: '#667eea', curveness: 0.2, opacity: 0.4 },
      label: { show: true, fontSize: 11, color: '#ccc' },
      itemStyle: { borderColor: '#fff', borderWidth: 1 }
    }]
  }
  instance = echarts.init(chart.value)
  instance.setOption(option)
}

onMounted(() => { buildGraph(); window.addEventListener('resize', () => instance?.resize()) })
onBeforeUnmount(() => { instance?.dispose(); window.removeEventListener('resize', () => instance?.resize()) })
</script>
<style scoped>
.kg-container { width: 100%; height: 500px; background: rgba(10,13,42,0.6); border-radius: 12px; }
</style>