''"Agent API''"
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from agents.orchestrator import orchestrator, AgentOrchestrator
from auth import verify_token

router = APIRouter(prefix="/agent/collab", tags=["Collaboration"])

class CollabRequest(BaseModel):
    goal: str

@router.post("/plan")
async def plan_collab(req: CollabRequest, _=Depends(verify_token)):
    ''''''
    task = await orchestrator.plan_task(req.goal)
    return {"ok": True, "task": {"id": task.id, "goal": task.goal, "steps": [{"id": s.id, "role": s.agent_role.value, "action": s.action} for s in task.steps]}}

@router.post("/execute/{task_id}")
async def execute_collab(task_id: str, _=Depends(verify_token)):
    ''''''
    task = await orchestrator.execute_task(task_id)
    return {"ok": task.status == "done", "task": {"id": task.id, "goal": task.goal, "status": task.status, "summary": task.summary}}

@router.post("/run")
async def plan_and_run(req: CollabRequest, _=Depends(verify_token)):
    ''''''
    task = await orchestrator.plan_task(req.goal)
    task = await orchestrator.execute_task(task.id)
    return {"ok": task.status == "done", "task": {"id": task.id, "goal": task.goal, "status": task.status, "summary": task.summary}}

@router.get("/status")
async def collab_status(_=Depends(verify_token)):
    return {"ok": True, **orchestrator.get_status()}
