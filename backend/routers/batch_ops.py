"""鎵归噺淇敼寮曟搸 鈥?鎵归噺鎿嶄綔鍟嗗搧/涓婁笅鏋?鎹㈠浘 + L3瀹℃壒 + 鍥炴粴"""
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
    ids: list[int]       # 鍟嗗搧ID鍒楄〃
    value: Optional[str] = None
    field: Optional[str] = None

def _get_jobs():
    return state._data.setdefault("batch_jobs", [])

async def _proxy_batch(action: str, ids: list, value: str = None, field: str = None) -> list:
    """瀹為檯鎵ц鎵归噺鎿嶄綔"""
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
        return [{"id": pid, "ok": False, "error": f"涓嶆敮鎸佺殑鎿嶄綔: {action}"} for pid in ids]

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
    """鎻愪氦鎵归噺鎿嶄綔锛堣繘鍏ュ鎵规祦绋嬶級"""
    if len(req.ids) > MAX_BATCH:
        raise HTTPException(400, f"鍗曟鏈€澶氭搷浣?{MAX_BATCH} 鏉?)
    if len(req.ids) == 0:
        raise HTTPException(400, "璇烽€夋嫨瑕佹搷浣滅殑鍟嗗搧")

    action_names = {
        "online": "鎵归噺涓婃灦", "offline": "鎵归噺涓嬫灦",
        "update_title": "鎵归噺淇敼鏍囬", "update_price": "鎵归噺淇敼浠锋牸",
        "update_stock": "鎵归噺淇敼搴撳瓨", "replace_image": "鎵归噺鏇挎崲鍥剧墖",
    }
    action_name = action_names.get(req.action, req.action)

    risk = await handle_risk("L3", f"{action_name} ({len(req.ids)}鏉?",
        f"瀛楁: {req.field or '-'} | 鍊? {str(req.value)[:50] or '-'}")
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

    return {"job_id": job["id"], "status": "pending_approval", "total": len(req.ids), "message": "宸叉彁浜ゅ鎵癸紝璇峰湪瀹℃壒涓績澶勭悊"}

@router.get("/jobs")
async def list_jobs(_=Depends(verify_token)):
    """鏌ョ湅鎵归噺鎿嶄綔璁板綍"""
    await handle_risk("L1", "鏌ョ湅鎵归噺鎿嶄綔璁板綍")
    return {"jobs": _get_jobs()}

@router.get("/jobs/{job_id}")
async def get_job(job_id: str, _=Depends(verify_token)):
    for j in _get_jobs():
        if j["id"] == job_id:
            return j
    return {"error": "浠诲姟涓嶅瓨鍦?}

@router.post("/execute/{job_id}")
async def execute_job(job_id: str, _=Depends(verify_token)):
    """鎵ц宸插鎵圭殑鎵归噺鎿嶄綔"""
    jobs = _get_jobs()
    for j in jobs:
        if j["id"] == job_id:
            if j["status"] != "pending_approval":
                return {"error": f"浠诲姟鐘舵€佷笉鍏佽鎵ц: {j['status']}"}
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
    raise HTTPException(404, "浠诲姟涓嶅瓨鍦?)

@router.post("/preview")
async def preview_batch(req: BatchAction, _=Depends(verify_token)):
    """棰勮鎵归噺鎿嶄綔"""
    await handle_risk("L1", "棰勮鎵归噺鎿嶄綔", f"{req.action} {len(req.ids)}鏉?)
    return {
        "action": req.action,
        "affected_count": len(req.ids),
        "sample_ids": req.ids[:5],
        "estimated_impact": f"灏嗗奖鍝?{len(req.ids)} 鏉″晢鍝佽褰?,
        "note": "棰勮閫氳繃鍚庤浣跨敤 /batch/submit 鎻愪氦瀹℃壒",
    }
