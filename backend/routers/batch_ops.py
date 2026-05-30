""" -- // + L3 + """
import httpx
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from risk import handle_risk
from state import state
from config import MALL_BASE_URL

router = APIRouter(prefix="/batch", tags=["Batch"])

MAX_BATCH = 100

class BatchAction(BaseModel):
    action: str          # online / offline / update_title / update_price / update_stock / replace_image
    ids: list[int]       # ID
    value: Optional[str] = None
    field: Optional[str] = None

def _get_jobs():
    return state._data.setdefault("batch_jobs", [])

async def _proxy_batch(action: str, ids: list, value: str = None, field: str = None) -> list:
    ''''''
    results = []
    action_map = {
        "online": {"path": "/api/product/batch-online", "method": "POST"},
        "offline": {"path": "/api/product/batch-offline", "method": "POST"},
        "update_title": {"path": "/api/product/batch-update", "method": "PUT"},
        "update_price": {"path": "/api/product/batch-update", "method": "PUT"},
        "update_stock": {"path": "/api/product/batch-update", "method": "PUT"},
        "replace_image": {"path": "/api/product/batch-replace-image", "method": "PUT"},
    }
    cfg = action_map.get(action)
    if not cfg:
        return [{"id": pid, "ok": False, "error": f": {action}"} for pid in ids]

    async with httpx.AsyncClient(timeout=30) as c:
        for pid in ids:
            try:
                payload = {"id": pid}
                if value is not None:
                    payload["value"] = value
                if field is not None:
                    payload["field"] = field

                method = cfg["method"]
                url = f"{MALL_BASE_URL}{cfg['path']}"
                if method == "GET":
                    r = await c.get(url, params=payload)
                elif method == "POST":
                    r = await c.post(url, json=payload)
                else:
                    r = await c.put(url, json=payload)

                results.append({
                    "id": pid,
                    "ok": r.status_code < 500,
                    "status": r.status_code,
                    "response": r.text[:200] if r.status_code >= 400 else "ok",
                })
            except Exception as e:
                results.append({"id": pid, "ok": False, "error": str(e)})
    return results

@router.post("/submit")
async def submit_batch(req: BatchAction, _=Depends(verify_token)):
    ''"()''"
    if len(req.ids) > MAX_BATCH:
        raise HTTPException(400, f" {MAX_BATCH} ")
    if len(req.ids) == 0:
        raise HTTPException(400, '')

    action_names = {
        "online": '', "offline": '',
        "update_title": '', "update_price": '',
        "update_stock": '', "replace_image": '',
    }
    action_name = action_names.get(req.action, req.action)

    risk = await handle_risk("L3", f"{action_name} ({len(req.ids)})",
        f": {req.field or '-'} | : {str(req.value)[:50] or '-'}")
    if not risk["allowed"]:
        return risk

    jobs = _get_jobs()
    job = {
        "id": risk["approval_id"],
        "action": req.action,
        "action_name": action_name,
        "ids": req.ids,
        "value": req.value,
        "field": req.field,
        "status": "pending_approval",
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "progress": 0,
        "results": [],
    }
    jobs.insert(0, job)
    if len(jobs) > 50: jobs[:] = jobs[:50]
    state._save()

    return {"job_id": job["id"], "status": "pending_approval", "total": len(req.ids), "message": ","}

@router.get("/jobs")
async def list_jobs(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    return {"jobs": _get_jobs()}

@router.get("/jobs/{job_id}")
async def get_job(job_id: str, _=Depends(verify_token)):
    for j in _get_jobs():
        if j["id"] == job_id:
            return j
    return {"error": ''}

@router.post("/execute/{job_id}")
async def execute_job(job_id: str, _=Depends(verify_token)):
    ''''''
    jobs = _get_jobs()
    for j in jobs:
        if j["id"] == job_id:
            if j["status"] != "pending_approval":
                return {"error": f": {j['status']}"}
            j["status"] = "running"
            j["progress"] = 0
            state._save()

            results = await _proxy_batch(j["action"], j["ids"], j.get("value"), j.get("field"))
            ok_count = sum(1 for r in results if r["ok"])
            j["results"] = results
            j["status"] = "completed"
            j["progress"] = 100
            j["completed_at"] = datetime.now().isoformat()
            j["ok_count"] = ok_count
            j["fail_count"] = len(results) - ok_count
            state._save()

            return {
                "job_id": job_id,
                "status": "completed",
                "total": len(results),
                "ok": ok_count,
                "failed": len(results) - ok_count,
                "results": results[:10],
            }
    raise HTTPException(404, '')

@router.post("/preview")
async def preview_batch(req: BatchAction, _=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '', f"{req.action} {len(req.ids)}")
    return {
        "action": req.action,
        "affected_count": len(req.ids),
        "sample_ids": req.ids[:5],
        "estimated_impact": f" {len(req.ids)} ",
        "note": " /batch/submit ",
    }
