"""Brain Event Router - bidirectional 3D brain <-> Agent <-> Mall"""
from fastapi import APIRouter, Depends
from auth import verify_token
from digital_lifeform import DigitalLifeform
from agents.master_agent import MasterAgent

router = APIRouter(prefix="/agent/brain", tags=["Brain"])

@router.get("/status")
async def brain_status(_=Depends(verify_token)):
    return {
        "ok": True,
        "lifeform": DigitalLifeform.get_lifeform_status(),
        "agents": MasterAgent.get_status(),
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }

@router.post("/event")
async def brain_event(data: dict, _=Depends(verify_token)):
    event_type = data.get("type", "ping")
    DigitalLifeform.record_interaction("brain_event", data)
    if event_type == "query_mall":
        result = await MasterAgent.execute("mall", data.get("query", ""))
        return {"ok": True, "result": result}
    elif event_type == "query_server":
        result = await MasterAgent.execute("server", data.get("query", ""))
        return {"ok": True, "result": result}
    return {"ok": True, "message": f"Brain event {event_type} received"}