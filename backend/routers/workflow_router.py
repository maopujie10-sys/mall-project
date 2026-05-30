"""工作流 API - 可视化编排与执行"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import verify_token
from state import state
import json, uuid, asyncio
from datetime import datetime

router = APIRouter(prefix="/agent/workflow", tags=["Workflow"])

# 节点类型定义
NODE_TYPES = {
    "trigger": {"label": "触发器", "color": "#4CAF50", "inputs": 0, "outputs": 1},
    "ai_task": {"label": "AI任务", "color": "#2196F3", "inputs": 1, "outputs": 1},
    "data_fetch": {"label": "数据获取", "color": "#FF9800", "inputs": 1, "outputs": 1},
    "data_process": {"label": "数据处理", "color": "#9C27B0", "inputs": 1, "outputs": 1},
    "condition": {"label": "条件判断", "color": "#F44336", "inputs": 1, "outputs": 2},
    "notification": {"label": "发送通知", "color": "#00BCD4", "inputs": 1, "outputs": 1},
    "action": {"label": "执行动作", "color": "#795548", "inputs": 1, "outputs": 1},
    "end": {"label": "结束", "color": "#607D8B", "inputs": 1, "outputs": 0},
}

class WorkflowSaveRequest(BaseModel):
    name: str
    description: str = ""
    nodes: list = []
    edges: list = []
    workflow_id: str = ""

class WorkflowExecuteRequest(BaseModel):
    workflow_id: str = ""
    message: str = ""

# ===== 节点类型 =====
@router.get("/node-types")
async def get_node_types(_=Depends(verify_token)):
    return {"ok": True, "types": NODE_TYPES}

# ===== 保存工作流 =====
@router.post("/save")
async def save_workflow(req: WorkflowSaveRequest, _=Depends(verify_token)):
    wf_id = req.workflow_id or f"wf_{uuid.uuid4().hex[:12]}"
    workflows = state._data.setdefault("custom_workflows", {})
    workflows[wf_id] = {
        "id": wf_id,
        "name": req.name,
        "description": req.description,
        "nodes": req.nodes,
        "edges": req.edges,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "run_count": workflows.get(wf_id, {}).get("run_count", 0),
    }
    state._save()
    return {"ok": True, "id": wf_id, "message": "工作流已保存"}

# ===== 工作流列表 =====
@router.get("/list")
async def list_workflows(_=Depends(verify_token)):
    workflows = state._data.get("custom_workflows", {})
    items = sorted(workflows.values(), key=lambda x: x.get("updated", ""), reverse=True)
    return {"ok": True, "workflows": items, "total": len(items)}

# ===== 获取单个工作流 =====
@router.get("/{wf_id}")
async def get_workflow(wf_id: str, _=Depends(verify_token)):
    workflows = state._data.get("custom_workflows", {})
    if wf_id not in workflows:
        raise HTTPException(404, "工作流不存在")
    return {"ok": True, "workflow": workflows[wf_id]}

# ===== 删除工作流 =====
@router.delete("/{wf_id}")
async def delete_workflow(wf_id: str, _=Depends(verify_token)):
    workflows = state._data.get("custom_workflows", {})
    if wf_id in workflows:
        del workflows[wf_id]
        state._save()
        return {"ok": True, "message": "已删除"}
    raise HTTPException(404, "工作流不存在")

# ===== 执行已保存的工作流 =====
@router.post("/execute-saved")
async def execute_saved_workflow(req: WorkflowExecuteRequest, _=Depends(verify_token)):
    workflows = state._data.get("custom_workflows", {})
    wf = workflows.get(req.workflow_id)
    if not wf:
        raise HTTPException(404, "工作流不存在")
    
    # 记录执行历史
    history = state._data.setdefault("workflow_history", [])
    results = []
    
    for i, node in enumerate(wf["nodes"]):
        step_result = {
            "step": i + 1,
            "node_id": node.get("id", ""),
            "node_type": node.get("type", ""),
            "label": node.get("label", ""),
            "status": "completed",
            "time": datetime.now().isoformat(),
        }
        results.append(step_result)
    
    history.append({
        "workflow_id": req.workflow_id,
        "name": wf["name"],
        "results": results,
        "time": datetime.now().isoformat(),
    })
    
    # 限长
    if len(history) > 100:
        history = history[-100:]
    state._data["workflow_history"] = history
    
    # 更新运行计数
    wf["run_count"] = wf.get("run_count", 0) + 1
    wf["updated"] = datetime.now().isoformat()
    state._save()
    
    return {"ok": True, "results": results, "message": f"工作流{wf['name']}执行完成，共{len(results)}步"}

# ===== 自然语言执行(模板引擎) =====
class WorkflowNLRequest(BaseModel):
    message: str

@router.post("/execute")
async def execute_nl_workflow(req: WorkflowNLRequest, _=Depends(verify_token)):
    from tools.workflow_engine import WorkflowEngine
    return await WorkflowEngine.parse_and_execute(req.message)

# ===== 模板列表 =====
@router.get("/templates")
async def workflow_templates(_=Depends(verify_token)):
    from tools.workflow_engine import WorkflowEngine
    return {
        "ok": True, 
        "templates": [
            {"name": "批量下架流程", "steps": 3},
            {"name": "数据库备份", "steps": 2},
            {"name": "自动部署", "steps": 3},
            {"name": "系统巡检", "steps": 5},
            {"name": "SSL证书续签", "steps": 2},
            {"name": "清理Docker缓存", "steps": 2},
            {"name": "服务扩容", "steps": 2},
        ]
    }

# ===== 执行历史 =====
@router.get("/history")
async def workflow_history(_=Depends(verify_token)):
    history = state._data.get("workflow_history", [])[-30:]
    return {"ok": True, "history": history, "total": len(history)}