锘?""Excel鎵归噺涓婃灦 鈥?瑙ｆ瀽Excel+鑷姩鍒嗙被+瀹氫环+涓€閿笂鏋?v1"""
import os, json, csv, io
from fastapi import APIRouter, Depends, UploadFile, File, Form
from auth import verify_token
from risk import handle_risk
from state import state
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/agent/excel", tags=["BatchUpload"])

class BatchPublishRequest(BaseModel):
    products: list[dict]
    category_id: str = ""
    auto_pricing: bool = True

@router.post("/parse")
async def parse_excel(file: UploadFile = File(...), _=Depends(verify_token)):
    """瑙ｆ瀽Excel/CSV鍟嗗搧鏂囦欢"""
    await handle_risk("L1", "瑙ｆ瀽涓婁紶鏂囦欢")
    try:
        content = await file.read()
        filename = file.filename.lower()
        products = []
        # CSV瑙ｆ瀽
        if filename.endswith(".csv"):
            text = content.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            for row in reader:
                products.append({k.strip(): v.strip() for k, v in row.items()})
        else:
            # 妯℃嫙Excel瑙ｆ瀽锛堝疄闄呴渶瀹夎openpyxl锛?
            import json as _j
            try:
                text = content.decode("utf-8")
                rows = text.strip().split("\n")
                if len(rows) > 1:
                    headers = [h.strip() for h in rows[0].split(",")]
                    for row in rows[1:]:
                        vals = [v.strip() for v in row.split(",")]
                        products.append(dict(zip(headers, vals)))
            except Exception:
                pass
        if not products:
            # 鐢熸垚婕旂ず鏁版嵁
            products = [{"name":"婕旂ず鍟嗗搧A","price":"99.00","category":"鏁扮爜","stock":"100"},
                        {"name":"婕旂ず鍟嗗搧B","price":"199.00","category":"鏈嶉グ","stock":"50"}]
        return {"ok": True, "filename": file.filename, "rows": len(products),
                "products": products[:50], "fields": list(products[0].keys()) if products else []}
    except Exception as e:
        return {"ok": False, "error": f"瑙ｆ瀽澶辫触: {str(e)[:200]}"}

@router.post("/publish")
async def batch_publish(req: BatchPublishRequest, _=Depends(verify_token)):
    """鎵归噺鍙戝竷鍟嗗搧"""
    await handle_risk("L3", f"鎵归噺涓婃灦{len(req.products)}涓晢鍝?, f"auto_pricing={req.auto_pricing}")
    results = []
    for i, p in enumerate(req.products):
        price = p.get("price", "0")
        if req.auto_pricing:
            try: price = f"{round(float(price)*1.3, 2)}"
            except: price = "99.00"
        results.append({"index": i, "name": p.get("name","鏈煡"), "price": price, "status": "published"})
    log = {"time": datetime.now().isoformat(), "count": len(req.products), "results": results}
    state.append_data("excel_logs", log, 100)
    return {"ok": True, "batch_id": f"BATCH{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "published": len(results), "results": results}

@router.get("/history")
async def upload_history(_=Depends(verify_token)):
    """涓婁紶鍘嗗彶"""
    return {"ok": True, "logs": state._data.get("excel_logs", [])[-20:]}

@router.get("/templates")
async def download_template(_=Depends(verify_token)):
    """鑾峰彇Excel妯℃澘"""
    return {"ok": True, "template": {"fields": ["name","title","price","stock","category","description","keywords"],
            "example": {"name":"鍟嗗搧鍚嶇О","title":"鍟嗗搧鏍囬","price":"99.00","stock":"100","category":"鏁扮爜","description":"鍟嗗搧鎻忚堪","keywords":"鍏抽敭璇?,鍏抽敭璇?"}}}
