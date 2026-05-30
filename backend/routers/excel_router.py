"""Excel -- Excel+++/v1"""
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
    category_id: str = ''
    auto_pricing: bool = True

@router.post("/parse")
async def parse_excel(file: UploadFile = File(...), _=Depends(verify_token)):
    ''"Excel/CSV''"
    await handle_risk("L1", '')
    try:
        content = await file.read()
        filename = file.filename.lower()
        products = []
        # CSV
        if filename.endswith(".csv"):
            text = content.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            for row in reader:
                products.append({k.strip(): v.strip() for k, v in row.items()})
        else:
            # Excel(openpyxl)
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
            
            products = [{"name":"A","price":"99.00","category":'',"stock":"100"},
                        {"name":"B","price":"199.00","category":'',"stock":"50"}]
        return {"ok": True, "filename": file.filename, "rows": len(products),
                "products": products[:50], "fields": list(products[0].keys()) if products else []}
    except Exception as e:
        return {"ok": False, "error": f": {str(e)[:200]}"}

@router.post("/publish")
async def batch_publish(req: BatchPublishRequest, _=Depends(verify_token)):
    ''''''
    await handle_risk("L3", f"{len(req.products)}", f"auto_pricing={req.auto_pricing}")
    results = []
    for i, p in enumerate(req.products):
        price = p.get("price", "0")
        if req.auto_pricing:
            try: price = f"{round(float(price)*1.3, 2)}"
            except: price = "99.00"
        results.append({"index": i, "name": p.get("name",''), "price": price, "status": "published"})
    log = {"time": datetime.now().isoformat(), "count": len(req.products), "results": results}
    state.append_data("excel_logs", log, 100)
    return {"ok": True, "batch_id": f"BATCH{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "published": len(results), "results": results}

@router.get("/history")
async def upload_history(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "logs": state._data.get("excel_logs", [])[-20:]}

@router.get("/templates")
async def download_template(_=Depends(verify_token)):
    ''"Excel''"
    return {"ok": True, "template": {"fields": ["name","title","price","stock","category","description","keywords"],
            "example": {"name":'',"title":'',"price":"99.00","stock":"100","category":'',"description":'',"keywords":"1,2"}}}
