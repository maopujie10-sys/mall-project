锘?""宸ヤ綔娴佸紩鎿?API"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import verify_token
from state import state

router = APIRouter(prefix="/agent/workflow", tags=["Workflow"])

class WorkflowRequest(BaseModel):
    message: str

@router.post("/execute")
async def execute_workflow(req: WorkflowRequest, _=Depends(verify_token)):
    """鎵ц鑷劧璇█宸ヤ綔娴?""
    from tools.workflow_engine import WorkflowEngine
    return await WorkflowEngine.parse_and_execute(req.message)

@router.get("/history")
async def workflow_history(_=Depends(verify_token)):
    """宸ヤ綔娴佸巻鍙?""
    return {"ok": True, "history": state._data.get("workflow_history", [])[-20:]}

@router.get("/templates")
async def workflow_templates(_=Depends(verify_token)):
    """鍙敤宸ヤ綔娴佹ā鏉?""
    from tools.workflow_engine import WorkflowEngine
    return {"ok": True, "templates": ["涓嬫灦浣庡簱瀛樺晢鍝?, "澶囦唤鏁版嵁搴?, "閮ㄧ讲鏈嶅姟", "鍏ㄧ珯宸℃", "SSL璇佷功绠＄悊"]}
