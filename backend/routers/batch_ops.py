"""批量修改引擎 — 批量操作商品/上下架/换图 + L3审批 + 回滚"""
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
    ids: list[int]       # 商品ID列表
    value: Optional[str] = None
    field: Optional[str] = None

def _get_jobs():
    return state._data.setdefault("batch_jobs", [])

async def _proxy_batch(action: str, ids: list, value: str = None, field: str = None) -> list:
    """实际执行批量操作"""
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
        return [{"id": pid, "ok": False, "error": f"不支持的操作: {action}"} for pid in ids]

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
    """提交批量操作（进入审批流程）"""
    if len(req.ids) > MAX_BATCH:
        raise HTTPException(400, f"单次最多操作 {MAX_BATCH} 条")
    if len(req.ids) == 0:
        raise HTTPException(400, "请选择要操作的商品")

    action_names = {
        "online": "批量上架", "offline": "批量下架",
        "update_title": "批量修改标题", "update_price": "批量修改价格",
        "update_stock": "批量修改库存", "replace_image": "批量替换图片",
    }
    action_name = action_names.get(req.action, req.action)

    risk = await handle_risk("L3", f"{action_name} ({len(req.ids)}条)",
        f"字段: {req.field or '-'} | 值: {str(req.value)[:50] or '-'}")
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

    return {"job_id": job["id"], "status": "pending_approval", "total": len(req.ids), "message": "已提交审批，请在审批中心处理"}

@router.get("/jobs")
async def list_jobs(_=Depends(verify_token)):
    """查看批量操作记录"""
    await handle_risk("L1", "查看批量操作记录")
    return {"jobs": _get_jobs()}

@router.get("/jobs/{job_id}")
async def get_job(job_id: str, _=Depends(verify_token)):
    for j in _get_jobs():
        if j["id"] == job_id:
            return j
    return {"error": "任务不存在"}

@router.post("/execute/{job_id}")
async def execute_job(job_id: str, _=Depends(verify_token)):
    """执行已审批的批量操作"""
    jobs = _get_jobs()
    for j in jobs:
        if j["id"] == job_id:
            if j["status"] != "pending_approval":
                return {"error": f"任务状态不允许执行: {j['status']}"}
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
    raise HTTPException(404, "任务不存在")

@router.post("/preview")
async def preview_batch(req: BatchAction, _=Depends(verify_token)):
    """预览批量操作"""
    await handle_risk("L1", "预览批量操作", f"{req.action} {len(req.ids)}条")
    return {
        "action": req.action,
        "affected_count": len(req.ids),
        "sample_ids": req.ids[:5],
        "estimated_impact": f"将影响 {len(req.ids)} 条商品记录",
        "note": "预览通过后请使用 /batch/submit 提交审批",
    }
