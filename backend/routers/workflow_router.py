"""工作流引擎 API"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import verify_token
from state import state

router = APIRouter(prefix="/agent/workflow", tags=["Workflow"])

class WorkflowRequest(BaseModel):
    message: str

@router.post("/execute")
async def execute_workflow(req: WorkflowRequest, _=Depends(verify_token)):
    """执行自然语言工作流"""
    from tools.workflow_engine import WorkflowEngine
    return await WorkflowEngine.parse_and_execute(req.message)

@router.get("/history")
async def workflow_history(_=Depends(verify_token)):
    """工作流历史"""
    return {"ok": True, "history": state._data.get("workflow_history", [])[-20:]}

@router.get("/templates")
async def workflow_templates(_=Depends(verify_token)):
    """可用工作流模板"""
    from tools.workflow_engine import WorkflowEngine
    return {"ok": True, "templates": ["下架低库存商品", "备份数据库", "部署服务", "全站巡检", "SSL证书管理"]}
