<template>
  <div class="workflow-editor">
    <div class="wf-header">
      <h2>?????????</h2>
      <div class="wf-actions">
        <input v-model="workflowName" placeholder="?????" class="wf-name-input" />
        <button @click="saveWorkflow" class="btn btn-primary">??</button>
        <button @click="executeWorkflow" class="btn btn-success">??</button>
        <button @click="loadWorkflows" class="btn btn-outline">??</button>
      </div>
    </div>

    <div class="wf-body">
      <!-- ?????? -->
      <div class="wf-sidebar">
        <h4>????</h4>
        <div
          v-for="(info, type) in nodeTypes"
          :key="type"
          class="wf-node-item"
          :style="{ borderLeftColor: info.color }"
          draggable="true"
          @dragstart="onDragStart($event, type)"
        >
          <span class="node-dot" :style="{ background: info.color }"></span>
          {{ info.label }}
        </div>
      </div>

      <!-- ???? -->
      <div
        class="wf-canvas"
        ref="canvasRef"
        @drop="onDrop"
        @dragover.prevent
        @mousedown="onCanvasMouseDown"
        @mousemove="onCanvasMouseMove"
        @mouseup="onCanvasMouseUp"
      >
        <svg class="wf-edges" v-if="edges.length">
          <line
            v-for="(edge, i) in edges"
            :key="i"
            :x1="getNodeCenter(edge.from).x"
            :y1="getNodeCenter(edge.from).y"
            :x2="getNodeCenter(edge.to).x"
            :y2="getNodeCenter(edge.to).y"
            stroke="#666"
            stroke-width="2"
            marker-end="url(#arrowhead)"
          />
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
            </marker>
          </defs>
        </svg>

        <div
          v-for="node in nodes"
          :key="node.id"
          class="wf-node"
          :style="{ left: node.x + 'px', top: node.y + 'px', borderColor: getNodeColor(node.type) }"
          @mousedown.stop="onNodeMouseDown($event, node.id)"
          @dblclick="startConnection(node.id)"
        >
          <div class="wf-node-header" :style="{ background: getNodeColor(node.type) }">
            {{ node.label || node.type }}
          </div>
          <div class="wf-node-body">
            <div class="wf-node-ports">
              <div class="port port-input" v-if="getNodeInfo(node.type).inputs > 0" title="??"></div>
              <div class="port port-output" v-if="getNodeInfo(node.type).outputs > 0" title="??" @click.stop="startConnection(node.id)"></div>
            </div>
          </div>
        </div>

        <div v-if="!nodes.length" class="wf-placeholder">
          ????????????????
        </div>
      </div>

      <!-- ?????? -->
      <div class="wf-props" v-if="selectedNode">
        <h4>????</h4>
        <div class="prop-group">
          <label>??</label>
          <input v-model="selectedNode.label" @input="updateNode" class="prop-input" />
        </div>
        <div class="prop-group">
          <label>??</label>
          <select v-model="selectedNode.type" @change="updateNode" class="prop-input">
            <option v-for="(info, type) in nodeTypes" :key="type" :value="type">{{ info.label }}</option>
          </select>
        </div>
        <div class="prop-group">
          <label>??</label>
          <textarea v-model="selectedNode.description" @input="updateNode" class="prop-input" rows="3"></textarea>
        </div>
        <button @click="deleteSelectedNode" class="btn btn-danger btn-sm">????</button>
        <button @click="selectedNode = null" class="btn btn-outline btn-sm" style="margin-left:8px">????</button>
      </div>
    </div>

    <!-- ??????? -->
    <div class="modal" v-if="showLoadModal" @click.self="showLoadModal = false">
      <div class="modal-content">
        <h4>?????????</h4>
        <div v-if="savedWorkflows.length" class="wf-list">
          <div
            v-for="wf in savedWorkflows"
            :key="wf.id"
            class="wf-list-item"
            @click="loadWorkflow(wf)"
          >
            <strong>{{ wf.name }}</strong>
            <span class="text-muted">{{ wf.description }}</span>
            <span class="text-muted">{{ wf.updated?.slice(0,10) }}</span>
            <button @click.stop="deleteWorkflow(wf.id)" class="btn btn-danger btn-xs">??</button>
          </div>
        </div>
        <div v-else class="text-muted">????????</div>
        <button @click="showLoadModal = false" class="btn btn-outline" style="margin-top:12px">??</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { agentApi } from "@/api/index";

const canvasRef = ref(null);
const workflowName = ref("?????");
const nodes = ref([]);
const edges = ref([]);
const selectedNode = ref(null);
const showLoadModal = ref(false);
const savedWorkflows = ref([]);
const connectingFrom = ref(null);
const draggingNode = ref(null);
const dragOffset = ref({ x: 0, y: 0 });

const nodeTypes = {
  trigger: { label: "???", color: "#4CAF50", inputs: 0, outputs: 1 },
  ai_task: { label: "AI??", color: "#2196F3", inputs: 1, outputs: 1 },
  data_fetch: { label: "????", color: "#FF9800", inputs: 1, outputs: 1 },
  data_process: { label: "????", color: "#9C27B0", inputs: 1, outputs: 1 },
  condition: { label: "????", color: "#F44336", inputs: 1, outputs: 2 },
  notification: { label: "????", color: "#00BCD4", inputs: 1, outputs: 1 },
  action: { label: "????", color: "#795548", inputs: 1, outputs: 1 },
  end: { label: "??", color: "#607D8B", inputs: 1, outputs: 0 },
};

let nodeIdCounter = 1;

function getNodeColor(type) {
  return nodeTypes[type]?.color || "#999";
}

function getNodeInfo(type) {
  return nodeTypes[type] || { inputs: 1, outputs: 1 };
}

function getNodeCenter(nodeId) {
  const node = nodes.value.find((n) => n.id === nodeId);
  return node ? { x: node.x + 80, y: node.y + 30 } : { x: 0, y: 0 };
}

function onDragStart(e, type) {
  e.dataTransfer.setData("nodeType", type);
}

function onDrop(e) {
  const type = e.dataTransfer.getData("nodeType");
  if (!type) return;
  const rect = canvasRef.value.getBoundingClientRect();
  const x = e.clientX - rect.left - 70;
  const y = e.clientY - rect.top - 25;
  nodes.value.push({
    id: "n" + nodeIdCounter++,
    type,
    label: nodeTypes[type]?.label || type,
    description: "",
    x: Math.max(0, x),
    y: Math.max(0, y),
  });
}

function onNodeMouseDown(e, nodeId) {
  if (connectingFrom.value) {
    edges.value.push({ from: connectingFrom.value, to: nodeId });
    connectingFrom.value = null;
    return;
  }
  const node = nodes.value.find((n) => n.id === nodeId);
  selectedNode.value = node;
  draggingNode.value = nodeId;
  dragOffset.value = {
    x: e.clientX - node.x,
    y: e.clientY - node.y,
  };
}

function onCanvasMouseDown(e) {
  if (e.target === canvasRef.value || e.target.classList.contains("wf-placeholder")) {
    selectedNode.value = null;
    connectingFrom.value = null;
  }
}

function onCanvasMouseMove(e) {
  if (draggingNode.value) {
    const node = nodes.value.find((n) => n.id === draggingNode.value);
    if (node) {
      node.x = e.clientX - dragOffset.value.x;
      node.y = e.clientY - dragOffset.value.y;
    }
  }
}

function onCanvasMouseUp() {
  draggingNode.value = null;
}

function startConnection(nodeId) {
  if (connectingFrom.value === nodeId) {
    connectingFrom.value = null;
  } else {
    connectingFrom.value = nodeId;
  }
}

function updateNode() {
  // reactivity handles this
}

function deleteSelectedNode() {
  if (selectedNode.value) {
    const id = selectedNode.value.id;
    nodes.value = nodes.value.filter((n) => n.id !== id);
    edges.value = edges.value.filter((e) => e.from !== id && e.to !== id);
    selectedNode.value = null;
  }
}

async function saveWorkflow() {
  try {
    const res = await agentApi.post("/agent/workflow/save", {
      name: workflowName.value || "??????",
      description: "",
      nodes: nodes.value.map((n) => ({
        id: n.id,
        type: n.type,
        label: n.label,
        description: n.description,
        x: n.x,
        y: n.y,
      })),
      edges: edges.value,
    });
    if (res.data?.ok) {
      alert("??????: " + res.data.id);
    }
  } catch (e) {
    alert("????: " + (e.response?.data?.detail || e.message));
  }
}

async function executeWorkflow() {
  if (!nodes.value.length) return alert("??????");
  try {
    const res = await agentApi.post("/agent/workflow/execute-saved", {
      workflow_id: "",
      message: workflowName.value,
    });
    if (res.data?.ok) {
      alert("????! ?" + res.data.results?.length + "?");
    }
  } catch (e) {
    alert("????: " + (e.response?.data?.detail || e.message));
  }
}

async function loadWorkflows() {
  try {
    const res = await agentApi.get("/agent/workflow/list");
    if (res.data?.ok) {
      savedWorkflows.value = res.data.workflows || [];
      showLoadModal.value = true;
    }
  } catch (e) {
    alert("????");
  }
}

function loadWorkflow(wf) {
  nodes.value = (wf.nodes || []).map((n) => ({
    ...n,
    x: n.x || 100,
    y: n.y || 100,
  }));
  edges.value = wf.edges || [];
  workflowName.value = wf.name || "";
  nodeIdCounter = Math.max(...nodes.value.map((n) => parseInt(n.id?.slice(1) || "0")), 0) + 1;
  showLoadModal.value = false;
}

async function deleteWorkflow(id) {
  if (!confirm("?????????")) return;
  try {
    await agentApi.delete("/agent/workflow/" + id);
    savedWorkflows.value = savedWorkflows.value.filter((w) => w.id !== id);
  } catch (e) {
    alert("????");
  }
}
</script>

<style scoped>
.workflow-editor {
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  background: rgba(26,26,46,0.85);
  color: #e0e0e0;
}

.wf-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: #16213e;
  border-bottom: 1px solid #0f3460;
}

.wf-header h2 {
  margin: 0;
  font-size: 18px;
  white-space: nowrap;
}

.wf-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex: 1;
}

.wf-name-input {
  padding: 6px 12px;
  border: 1px solid #0f3460;
  border-radius: 6px;
  background: rgba(26,26,46,0.85);
  color: #e0e0e0;
  width: 200px;
}

.wf-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.wf-sidebar {
  width: 180px;
  padding: 12px;
  background: #16213e;
  border-right: 1px solid #0f3460;
  overflow-y: auto;
}

.wf-sidebar h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #aaa;
}

.wf-node-item {
  padding: 10px 12px;
  margin-bottom: 6px;
  background: rgba(26,26,46,0.85);
  border-left: 4px solid;
  border-radius: 4px;
  cursor: grab;
  font-size: 13px;
  transition: all 0.2s;
}

.wf-node-item:hover {
  background: #0f3460;
  transform: translateX(4px);
}

.node-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
}

.wf-canvas {
  flex: 1;
  position: relative;
  overflow: auto;
  background: 
    linear-gradient(90deg, #ffffff08 1px, transparent 1px),
    linear-gradient(#ffffff08 1px, transparent 1px);
  background-size: 20px 20px;
}

.wf-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #666;
  font-size: 18px;
  pointer-events: none;
}

.wf-edges {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.wf-node {
  position: absolute;
  width: 160px;
  background: rgba(26,26,46,0.85);
  border: 2px solid;
  border-radius: 8px;
  cursor: move;
  user-select: none;
  z-index: 10;
  transition: box-shadow 0.2s;
}

.wf-node:hover {
  box-shadow: 0 0 12px rgba(100, 150, 255, 0.3);
}

.wf-node-header {
  padding: 8px 12px;
  border-radius: 6px 6px 0 0;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.wf-node-body {
  padding: 8px;
}

.wf-node-ports {
  display: flex;
  justify-content: space-between;
}

.port {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #555;
  border: 2px solid #888;
  cursor: crosshair;
}

.port:hover {
  background: #4CAF50;
  border-color: #4CAF50;
}

.port-input {
  margin-right: auto;
}

.port-output {
  margin-left: auto;
}

.wf-props {
  width: 240px;
  padding: 16px;
  background: #16213e;
  border-left: 1px solid #0f3460;
  overflow-y: auto;
}

.wf-props h4 {
  margin: 0 0 16px 0;
}

.prop-group {
  margin-bottom: 12px;
}

.prop-group label {
  display: block;
  font-size: 12px;
  color: #aaa;
  margin-bottom: 4px;
}

.prop-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #0f3460;
  border-radius: 4px;
  background: rgba(26,26,46,0.85);
  color: #e0e0e0;
  font-size: 13px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-primary { background: #2196F3; color: #fff; }
.btn-success { background: #4CAF50; color: #fff; }
.btn-danger { background: #F44336; color: #fff; }
.btn-outline { background: transparent; border: 1px solid #555; color: #ccc; }
.btn-sm { padding: 4px 10px; font-size: 12px; }
.btn-xs { padding: 2px 8px; font-size: 11px; }

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  background: rgba(26,26,46,0.85);
  border: 1px solid #0f3460;
  border-radius: 12px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 70vh;
  overflow-y: auto;
}

.wf-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-bottom: 1px solid #0f3460;
  cursor: pointer;
  font-size: 13px;
}

.wf-list-item:hover {
  background: #0f3460;
}

.text-muted {
  color: #888;
  font-size: 12px;
}
</style>
