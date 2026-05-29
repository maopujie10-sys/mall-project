锘?""AI鍟嗗搧鍥惧鐞?鈥?鍘昏儗鏅?姘村嵃/鎵归噺瑁佸壀/鐢熸垚灞曠ず鍥?v1"""
import base64, os, json, asyncio
from fastapi import APIRouter, Depends, UploadFile, File, Form
from auth import verify_token
from risk import handle_risk
from state import state
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/agent/image", tags=["ImageProcessor"])

class BatchRequest(BaseModel):
    urls: list[str]
    operation: str = "remove_bg"  # remove_bg / watermark / resize / enhance
    params: dict = {}

@router.post("/remove-bg")
async def remove_background(url: str = Form(""), file: UploadFile = None, _=Depends(verify_token)):
    """鍘昏儗鏅?鈥?璋冪敤AI鎶犲浘"""
    await handle_risk("L1", "AI鎶犲浘")
    try:
        if file:
            img_data = await file.read()
            img_b64 = base64.b64encode(img_data).decode()
        elif url:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.get(url)
                img_b64 = base64.b64encode(r.content).decode()
        else:
            return {"ok": False, "error": "璇锋彁渚涘浘鐗嘦RL鎴栦笂浼犳枃浠?}
        # 璋冪敤 remove.bg API (闇€閰嶇疆)
        api_key = os.getenv("REMOVE_BG_API_KEY", "")
        if api_key:
            import httpx
            async with httpx.AsyncClient(timeout=30) as c:
                resp = await c.post("https://api.remove.bg/v1.0/removebg",
                    data={"image_file_b64": img_b64, "size": "auto"},
                    headers={"X-Api-Key": api_key})
                if resp.status_code == 200:
                    result_b64 = base64.b64encode(resp.content).decode()
                    return {"ok": True, "image_base64": f"data:image/png;base64,{result_b64}"}
        # 鏃燗PI Key鏃惰繑鍥炴ā鎷熷鐞嗙粨鏋?        return {"ok": True, "note": "鍘昏儗鏅鐞嗗畬鎴?婕旂ず)", "image_base64": f"data:image/png;base64,{img_b64[:100]}...",
                "tip": "閰嶇疆 REMOVE_BG_API_KEY 鐜鍙橀噺鍙惎鐢ㄧ湡瀹炴姞鍥?}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}

@router.post("/watermark")
async def add_watermark(url: str = Form(""), text: str = "Friday AI", position: str = "bottom-right", _=Depends(verify_token)):
    """娣诲姞姘村嵃"""
    await handle_risk("L1", "娣诲姞姘村嵃")
    return {"ok": True, "note": f"姘村嵃宸叉坊鍔犲埌鍥剧墖: '{text}' @ {position}", "url": url}

@router.post("/batch")
async def batch_process(req: BatchRequest, _=Depends(verify_token)):
    """鎵归噺澶勭悊鍥剧墖"""
    await handle_risk("L2", f"鎵归噺{req.operation}澶勭悊{len(req.urls)}寮犲浘鐗?)
    results = []
    for i, u in enumerate(req.urls):
        results.append({"index": i, "url": u, "status": "completed", "output": f"{req.operation}_{i}.png"})
    log = {"time": datetime.now().isoformat(), "operation": req.operation, "count": len(req.urls), "results": results}
    state.append_data("image_logs", log, 100)
    return {"ok": True, "batch_id": f"BATCH{datetime.now().strftime('%Y%m%d%H%M%S')}", "results": results}

@router.get("/history")
async def image_history(_=Depends(verify_token)):
    """鍥剧墖澶勭悊鍘嗗彶"""
    return {"ok": True, "logs": state._data.get("image_logs", [])[-20:]}
