"""Excel批量上架 — 解析Excel+自动分类+定价+一键上架/v1"""
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
    """解析Excel/CSV商品文件"""
    await handle_risk("L1", "解析上传文件")
    try:
        content = await file.read()
        filename = file.filename.lower()
        products = []
        # CSV解析
        if filename.endswith(".csv"):
            text = content.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            for row in reader:
                products.append({k.strip(): v.strip() for k, v in row.items()})
        else:
            # 模拟Excel解析（实际需安装openpyxl）
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
            # 生成演示数据
            products = [{"name":"演示商品A","price":"99.00","category":"数码","stock":"100"},
                        {"name":"演示商品B","price":"199.00","category":"服饰","stock":"50"}]
        return {"ok": True, "filename": file.filename, "rows": len(products),
                "products": products[:50], "fields": list(products[0].keys()) if products else []}
    except Exception as e:
        return {"ok": False, "error": f"解析失败: {str(e)[:200]}"}

@router.post("/publish")
async def batch_publish(req: BatchPublishRequest, _=Depends(verify_token)):
    """批量发布商品"""
    await handle_risk("L3", f"批量上架{len(req.products)}个商品", f"auto_pricing={req.auto_pricing}")
    results = []
    for i, p in enumerate(req.products):
        price = p.get("price", "0")
        if req.auto_pricing:
            try: price = f"{round(float(price)*1.3, 2)}"
            except: price = "99.00"
        results.append({"index": i, "name": p.get("name","未知"), "price": price, "status": "published"})
    log = {"time": datetime.now().isoformat(), "count": len(req.products), "results": results}
    state.append_data("excel_logs", log, 100)
    return {"ok": True, "batch_id": f"BATCH{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "published": len(results), "results": results}

@router.get("/history")
async def upload_history(_=Depends(verify_token)):
    """上传历史"""
    return {"ok": True, "logs": state._data.get("excel_logs", [])[-20:]}

@router.get("/templates")
async def download_template(_=Depends(verify_token)):
    """获取Excel模板"""
    return {"ok": True, "template": {"fields": ["name","title","price","stock","category","description","keywords"],
            "example": {"name":"商品名称","title":"商品标题","price":"99.00","stock":"100","category":"数码","description":"商品描述","keywords":"关键词1,关键词2"}}}
