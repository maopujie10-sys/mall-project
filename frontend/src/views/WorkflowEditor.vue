<template>
  <div class="workflow-editor">
    <div class="wf-header">
      <h2>可视化工作流编辑器</h2>
      <div class="wf-actions">
        <input v-model="workflowName" placeholder="工作流名称" class="wf-name-input" />
        <button @click="saveWorkflow" class="btn btn-primary">保存</button>
        <button @click="executeWorkflow" class="btn btn-success">执行</button>
        <button @click="loadWorkflows" class="btn btn-outline">加载</button>
      </div>
    </div>
    <div class="wf-body">
      <div class="wf-sidebar">
        <h4>节点类型</h4>
        <div v-for="(info, type) in nodeTypes" :key="type" class="wf-node-item" :style="{ borderLeftColor: info.color }" draggable="true" @dragstart="onDragStart($event, type)">
          <span class="node-dot" :style="{ background: info.color }"></span>{{ info.label }}
        </div>
      </div>
      <div class="wf-canvas" ref="canvasRef" @drop="onDrop" @dragover.prevent @mousedown="onCanvasMouseDown" @mousemove="onCanvasMouseMove" @mouseup="onCanvasMouseUp">
        <svg class="wf-edges" v-if="edges.length">
          <line v-for="(edge, i) in edges" :key="i" :x1="getNodeCenter(edge.from).x" :y1="getNodeCenter(edge.from).y" :x2="getNodeCenter(edge.to).x" :y2="getNodeCenter(edge.to).y" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
          <defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#666"/></marker></defs>
        </svg>
        <div v-for="node in nodes" :key="node.id" class="wf-node" :style="{ left: node.x + 'px', top: node.y + 'px', borderColor: getNodeColor(node.type) }" @mousedown.stop="onNodeMouseDown($event, node.id)" @dblclick="startConnection(node.id)">
          <div class="wf-node-header" :style="{ background: getNodeColor(node.type) }">{{ node.label || node.type }}</div>
          <div class="wf-node-body">
            <div class="wf-node-ports">
              <div class="port port-input" v-if="getNodeInfo(node.type).inputs > 0" title="输入"></div>
              <div class="port port-output" v-if="getNodeInfo(node.type).outputs > 0" title="输出" @click.stop="startConnection(node.id)"></div>
            </div>
          </div>
        </div>
        <div v-if="!nodes.length" class="wf-placeholder">从左侧拖拽节点到画布开始编排工作流</div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { agentApi } from '@/api/index'

const workflowName = ref(''); const canvasRef = ref(null); const nodes = ref([]); const edges = ref([])
const nodeTypes = {
  trigger: { label: '触发器', color: '#4CAF50', inputs: 0, outputs: 1 },
  ai_task: { label: 'AI任务', color: '#2196F3', inputs: 1, outputs: 1 },
  data_fetch: { label: '数据获取', color: '#FF9800', inputs: 1, outputs: 1 },
  data_process: { label: '数据处理', color: '#9C27B0', inputs: 1, outputs: 1 },
  condition: { label: '条件判断', color: '#F44336', inputs: 1, outputs: 2 },
  notification: { label: '发送通知', color: '#00BCD4', inputs: 1, outputs: 1 },
  action: { label: '执行动作', color: '#795548', inputs: 1, outputs: 1 },
  end: { label: '结束', color: '#607D8B', inputs: 1, outputs: 0 },
}
let connectingFrom = null

function getNodeInfo(type) { return nodeTypes[type] || { inputs: 1, outputs: 1 } }
function getNodeColor(type) { return (nodeTypes[type] || {}).color || '#666' }
function getNodeCenter(id) { const n = nodes.value.find(x => x.id === id); return n ? { x: n.x + 80, y: n.y + 25 } : { x: 0, y: 0 } }
function onDragStart(e, type) { e.dataTransfer.setData('nodeType', type) }
function onDrop(e) { const type = e.dataTransfer.getData('nodeType'); if (type) { const rect = canvasRef.value.getBoundingClientRect(); nodes.value.push({ id: 'n' + Date.now(), type, label: nodeTypes[type]?.label || type, x: e.clientX - rect.left - 40, y: e.clientY - rect.top - 15 }) } }
function onCanvasMouseDown() {}
function onCanvasMouseMove() {}
function onCanvasMouseUp() {}
function onNodeMouseDown(e, id) { e.stopPropagation() }
function startConnection(id) { connectingFrom = id }
async function saveWorkflow() { if (!workflowName.value) return; try { await agentApi.post('/agent/workflow/save', { name: workflowName.value, nodes: nodes.value, edges: edges.value }); alert('已保存') } catch (e) { alert('保存失败') } }
async function executeWorkflow() { try { const r = await agentApi.post('/agent/workflow/execute', { message: workflowName.value || '执行工作流' }); alert('执行完成: ' + JSON.stringify(r?.data)) } catch (e) { alert('执行失败') } }
async function loadWorkflows() { try { const r = await agentApi.get('/agent/workflow/list'); if (r?.data?.ok && r.data.workflows?.length) { const wf = r.data.workflows[0]; workflowName.value = wf.name; nodes.value = wf.nodes || []; edges.value = wf.edges || [] } } catch (e) {} }
onMounted(async () => { try { const r = await agentApi.get('/agent/workflow/node-types'); if (r?.data?.ok) Object.assign(nodeTypes, r.data.types) } catch (e) {} })
</script>
<style scoped>
.workflow-editor { display: flex; flex-direction: column; height: calc(100vh - 80px); padding: 16px; }
.wf-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.wf-header h2 { font-size: 18px; margin: 0; color: #e0e0ff; }
.wf-actions { display: flex; gap: 8px; }
.wf-name-input { padding: 6px 10px; background: rgba(0,0,0,0.3); border: 1px solid rgba(102,126,234,0.3); border-radius: 6px; color: #e0e0e0; font-size: 13px; width: 150px; }
.btn { padding: 6px 14px; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; }
.btn-primary { background: #667eea; color: #fff; }
.btn-success { background: #52c41a; color: #fff; }
.btn-outline { background: transparent; border: 1px solid rgba(102,126,234,0.3); color: #a0b4ff; }
.wf-body { display: flex; flex: 1; gap: 12px; }
.wf-sidebar { width: 140px; background: rgba(0,0,0,0.25); border-radius: 8px; padding: 12px; }
.wf-sidebar h4 { font-size: 12px; color: rgba(255,255,255,0.5); margin: 0 0 10px; }
.wf-node-item { display: flex; align-items: center; gap: 6px; padding: 8px; margin-bottom: 6px; background: rgba(0,0,0,0.2); border-radius: 6px; border-left: 3px solid; cursor: grab; font-size: 11px; color: #ccc; }
.node-dot { width: 8px; height: 8px; border-radius: 50%; }
.wf-canvas { flex: 1; background: rgba(0,0,0,0.15); border-radius: 8px; position: relative; overflow: hidden; min-height: 400px; }
.wf-edges { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.wf-node { position: absolute; width: 160px; background: rgba(13,16,37,0.9); border: 2px solid; border-radius: 8px; cursor: move; }
.wf-node-header { padding: 6px 10px; font-size: 11px; color: #fff; border-radius: 6px 6px 0 0; }
.wf-node-body { padding: 4px 8px; }
.wf-node-ports { display: flex; justify-content: space-between; }
.port { width: 10px; height: 10px; border-radius: 50%; background: #667eea; cursor: crosshair; }
.wf-placeholder { display: flex; align-items: center; justify-content: center; height: 100%; color: rgba(255,255,255,0.3); font-size: 14px; }
@media (max-width: 768px) { .workflow-editor { padding: 8px; } .wf-body { flex-direction: column; } .wf-sidebar { width: 100%; display: flex; flex-wrap: wrap; gap: 6px; } .wf-node-item { margin-bottom: 0; } }
</style>