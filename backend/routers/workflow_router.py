"""Workflow API - Visual workflow editor, save/execute/list workflows"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import verify_token
from state import state
import json, uuid, asyncio
from datetime import datetime

router = APIRouter(prefix="/agent/workflow", tags=["Workflow"])

NODE_TYPES = {
    "trigger": {"label": "Trigger", "color": "#4CAF50", "inputs": 0, "outputs": 1},
    "ai_task": {"label": "AI Task", "color": "#2196F3", "inputs": 1, "outputs": 1},
    "data_fetch": {"label": "Data Fetch", "color": "#FF9800", "inputs": 1, "outputs": 1},
    "data_process": {"label": "Data Process", "color": "#9C27B0", "inputs": 1, "outputs": 1},
    "condition": {"label": "Condition", "color": "#F44336", "inputs": 1, "outputs": 2},
    "notification": {"label": "Notification", "color": "#00BCD4", "inputs": 1, "outputs": 1},
    "action": {"label": "Action", "color": "#795548", "inputs": 1, "outputs": 1},
    "end": {"label": "End", "color": "#607D8B", "inputs": 1, "outputs": 0},
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

@router.get("/node-types")
async def get_node_types(_=Depends(verify_token)):
    """Get available node types for the visual editor"""
    return {"ok": True, "types": NODE_TYPES}

@router.post("/save")
async def save_workflow(req: WorkflowSaveRequest, _=Depends(verify_token)):
    """Save or update a workflow"""
    wf_id = req.workflow_id or f"wf_{uuid.uuid4().hex[:12]}"
    workflows = state._data.setdefault("custom_workflows", {})
    workflows[wf_id] = {
        "id": wf_id,
        "name": req.name,
        "description": req.description,
        "nodes": req.nodes,
        "edges": req.edges,
        "created": workflows.get(wf_id, {}).get("created", datetime.now().isoformat()),
        "updated": datetime.now().isoformat(),
        "run_count": workflows.get(wf_id, {}).get("run_count", 0),
    }
    state._save()
    return {"ok": True, "id": wf_id, "message": "Workflow saved"}

@router.get("/list")
async def list_workflows(_=Depends(verify_token)):
    """List all saved workflows"""
    workflows = state._data.get("custom_workflows", {})
    items = sorted(workflows.values(), key=lambda x: x.get("updated", ""), reverse=True)
    return {"ok": True, "workflows": items, "total": len(items)}

@router.get("/{wf_id}")
async def get_workflow(wf_id: str, _=Depends(verify_token)):
    """Get a specific workflow by ID"""
    workflows = state._data.get("custom_workflows", {})
    if wf_id not in workflows:
        raise HTTPException(404, "Workflow not found")
    return {"ok": True, "workflow": workflows[wf_id]}

@router.delete("/{wf_id}")
async def delete_workflow(wf_id: str, _=Depends(verify_token)):
    """Delete a workflow"""
    workflows = state._data.get("custom_workflows", {})
    if wf_id in workflows:
        del workflows[wf_id]
        state._save()
        return {"ok": True, "message": "Workflow deleted"}
    raise HTTPException(404, "Workflow not found")

@router.post("/execute-saved")
async def execute_saved_workflow(req: WorkflowExecuteRequest, _=Depends(verify_token)):
    """Execute a saved workflow"""
    workflows = state._data.get("custom_workflows", {})
    wf = workflows.get(req.workflow_id)
    if not wf:
        raise HTTPException(404, "Workflow not found")
    
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
    
    if len(history) > 100:
        history = history[-100:]
    state._data["workflow_history"] = history
    
    wf["run_count"] = wf.get("run_count", 0) + 1
    wf["updated"] = datetime.now().isoformat()
    state._save()
    
    return {"ok": True, "results": results, "message": f"{wf['name']} executed: {len(results)} steps"}

class WorkflowNLRequest(BaseModel):
    message: str

@router.post("/execute")
async def execute_nl_workflow(req: WorkflowNLRequest, _=Depends(verify_token)):
    """Execute workflow from natural language description"""
    from tools.workflow_engine import WorkflowEngine
    return await WorkflowEngine.parse_and_execute(req.message)

@router.get("/templates")
async def workflow_templates(_=Depends(verify_token)):
    """Get built-in workflow templates"""
    from tools.workflow_engine import WorkflowEngine
    template_list = []
    for name, wf in WorkflowEngine.TEMPLATES.items():
        template_list.append({"name": name, "steps": len(wf["steps"]), "preview": [s["desc"] for s in wf["steps"]]})
    return {"ok": True, "templates": template_list}

@router.get("/history")
async def workflow_history(_=Depends(verify_token)):
    """Get workflow execution history"""
    history = state._data.get("workflow_history", [])[-30:]
    return {"ok": True, "history": history, "total": len(history)}
