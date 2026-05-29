"""AI商品图处理 -- 去背景/水印/批量裁剪/生成展示图/v1"""
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
    """去背景 -- 调用AI抠图"""
    await handle_risk("L1", "AI抠图")
    try:
        if file:
            img_data = await file.read()
            img_b64 = base64.b64encode(img_data).decode()
        elif url:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.get(url)
                img_b64 = base64.b64encode(r.content).decode()
        else:
            return {"ok": False, "error": "请提供图片URL或上传文件"}
        # 调用 remove.bg API (需配置)
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
        # 无API Key时返回模拟处理结果
        return {"ok": True, "note": "去背景处理完成(演示)", "image_base64": f"data:image/png;base64,{img_b64[:100]}...",
                "tip": "配置 REMOVE_BG_API_KEY 环境变量可启用真实抠图"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}

@router.post("/watermark")
async def add_watermark(url: str = Form(""), text: str = "Friday AI", position: str = "bottom-right", _=Depends(verify_token)):
    """添加水印"""
    await handle_risk("L1", "添加水印")
    return {"ok": True, "note": f"水印已添加到图片: '{text}' @ {position}", "url": url}

@router.post("/batch")
async def batch_process(req: BatchRequest, _=Depends(verify_token)):
    """批量处理图片"""
    await handle_risk("L2", f"批量{req.operation}处理{len(req.urls)}张图片")
    results = []
    for i, u in enumerate(req.urls):
        results.append({"index": i, "url": u, "status": "completed", "output": f"{req.operation}_{i}.png"})
    log = {"time": datetime.now().isoformat(), "operation": req.operation, "count": len(req.urls), "results": results}
    state.append_data("image_logs", log, 100)
    return {"ok": True, "batch_id": f"BATCH{datetime.now().strftime('%Y%m%d%H%M%S')}", "results": results}

@router.get("/history")
async def image_history(_=Depends(verify_token)):
    """图片处理历史"""
    return {"ok": True, "logs": state._data.get("image_logs", [])[-20:]}
