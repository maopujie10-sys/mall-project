''" API -- ///COS/''"
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from risk import handle_risk
from tools.cache import cached
from tools.scraper_engine import ScraperEngine

router = APIRouter(prefix="/agent/scraper", tags=["Scraper"])


class StartJobRequest(BaseModel):
    platform: str = "ebay"
    keyword: str
    max_items: int = 20
    download_images: bool = True

class ImportRequest(BaseModel):
    product_ids: list[str]


#  API

@router.post("/jobs")
async def start_job(req: StartJobRequest, _=Depends(verify_token)):
    ''" --  +  + COS''"
    await handle_risk("L1", '', f"{req.platform}:{req.keyword}")
    if req.max_items > 100:
        raise HTTPException(400, "100")
    job = await ScraperEngine.start_job(
        platform=req.platform,
        keyword=req.keyword,
        max_items=req.max_items,
        download_images=req.download_images,
    )
    return {"ok": True, "job": job}

@router.get("/jobs")
async def list_jobs(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    return {"jobs": ScraperEngine.get_jobs()}

@router.get("/jobs/{job_id}")
async def get_job(job_id: str, _=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    job = ScraperEngine.get_job(job_id)
    if not job:
        raise HTTPException(404, '')
    return {"job": job}

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str, _=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '', job_id)
    from tools.scraper_engine import _get_jobs
    jobs = _get_jobs()
    if job_id not in jobs:
        raise HTTPException(404, '')
    del jobs[job_id]
    from state import state
    state._save()
    return {"ok": True, "deleted": job_id}

@router.get("/products")
async def list_products(
    _=Depends(verify_token),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
):
    ''''''
    await handle_risk("L1", '')
    return ScraperEngine.get_products(page=page, size=size, status=status)

@router.post("/products/import")
async def import_products(req: ImportRequest, _=Depends(verify_token)):
    ''''''
    await handle_risk("L3", '', f"{len(req.product_ids)} ")
    result = ScraperEngine.import_to_mall(req.product_ids)
    return {"ok": True, **result}

@router.post("/products/{product_id}/upload")
async def upload_product_images(product_id: str, _=Depends(verify_token)):
    ''''''
    await handle_risk("L2", '', product_id)
    return {"product_id": product_id, "status": "queued"}


@router.get("/cos-status")
async def cos_status(_=Depends(verify_token)):
    ''" COS ''"
    await handle_risk("L1", "COS")
    from tools.cloud_storage import get_cos_status as _cos
    try:
        status = await _cos() if callable(_cos) else {"status": '', "bucket": "N/A", "region": "N/A", "uploaded": 0, "usage": "0 MB"}
        return {"ok": True, "status": status}
    except Exception:
        return {"ok": True, "status": {"status": '', "bucket": "N/A", "region": "N/A", "uploaded": 0, "usage": "0 MB"}}

@router.get("/sources")
@cached('scraper_sources', ttl=300)
async def list_sources(_=Depends(verify_token)):
    ''''''
    await handle_risk("L1", '')
    return {
        "sources": [
            {"id": "ebay",     "name": "eBay ",       "type": "api",   "status": "ready"},
            {"id": "amazon",   "name": "Amazon ",     "type": "scrape","status": "ready"},
            {"id": "aliexpress","name": "AliExpress ", "type": "scrape","status": "ready"},
            {"id": "shopee",   "name": "Shopee ",       "type": "hybrid","status": "ready"},
            {"id": "lazada",   "name": "Lazada ",     "type": "scrape","status": "ready"},
            {"id": "wish",     "name": "Wish ",       "type": "scrape","status": "ready"},
            {"id": "tiktok",   "name": "TikTok Shop",       "type": "scrape","status": "ready"},
            {"id": "taobao",  "name": "/",          "type": "scrape","status": "ready"},
            {"id": "alibaba1688","name": "1688",     "type": "scrape","status": "ready"},
        ]
    }