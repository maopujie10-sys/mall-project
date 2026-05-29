锘?""鍏ㄩ噺鍟嗗搧閲囬泦 API 鈥?鎼滅储/鎻愬彇/涓嬭浇/涓婁紶COS/瀵煎叆鍟嗗煄"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from risk import handle_risk
from tools.cache import cached
from tools.scraper_engine import ScraperEngine

router = APIRouter(prefix="/agent/scraper", tags=["Scraper"])

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
#  璇锋眰妯″瀷
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?

class StartJobRequest(BaseModel):
    platform: str = "ebay"
    keyword: str
    max_items: int = 20
    download_images: bool = True

class ImportRequest(BaseModel):
    product_ids: list[str]

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
#  API
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?

@router.post("/jobs")
async def start_job(req: StartJobRequest, _=Depends(verify_token)):
    """鍚姩閲囬泦浠诲姟 鈥?鍏抽敭璇嶆悳绱?+ 璇︽儏椤垫彁鍙?+ 鍥剧墖涓婁紶COS"""
    await handle_risk("L1", "鍚姩閲囬泦浠诲姟", f"{req.platform}:{req.keyword}")
    if req.max_items > 100:
        raise HTTPException(400, "鍗曟鏈€澶氶噰闆?00涓晢鍝?)
    job = await ScraperEngine.start_job(
        platform=req.platform,
        keyword=req.keyword,
        max_items=req.max_items,
        download_images=req.download_images,
    )
    return {"ok": True, "job": job}

@router.get("/jobs")
async def list_jobs(_=Depends(verify_token)):
    """鏌ョ湅鎵€鏈夐噰闆嗕换鍔?""
    await handle_risk("L1", "鏌ョ湅閲囬泦浠诲姟鍒楄〃")
    return {"jobs": ScraperEngine.get_jobs()}

@router.get("/jobs/{job_id}")
async def get_job(job_id: str, _=Depends(verify_token)):
    """鏌ョ湅閲囬泦浠诲姟杩涘害"""
    await handle_risk("L1", "鏌ョ湅閲囬泦浠诲姟")
    job = ScraperEngine.get_job(job_id)
    if not job:
        raise HTTPException(404, "浠诲姟涓嶅瓨鍦?)
    return {"job": job}

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str, _=Depends(verify_token)):
    """鍒犻櫎閲囬泦浠诲姟"""
    await handle_risk("L1", "鍒犻櫎閲囬泦浠诲姟", job_id)
    from tools.scraper_engine import _get_jobs
    jobs = _get_jobs()
    if job_id not in jobs:
        raise HTTPException(404, "浠诲姟涓嶅瓨鍦?)
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
    """娴忚閲囬泦鍒扮殑鍟嗗搧"""
    await handle_risk("L1", "鏌ョ湅閲囬泦鍟嗗搧")
    return ScraperEngine.get_products(page=page, size=size, status=status)

@router.post("/products/import")
async def import_products(req: ImportRequest, _=Depends(verify_token)):
    """鎵归噺瀵煎叆閲囬泦鍟嗗搧鍒板晢鍩?""
    await handle_risk("L3", "瀵煎叆閲囬泦鍟嗗搧鍒板晢鍩?, f"{len(req.product_ids)} 涓晢鍝?)
    result = ScraperEngine.import_to_mall(req.product_ids)
    return {"ok": True, **result}

@router.post("/products/{product_id}/upload")
async def upload_product_images(product_id: str, _=Depends(verify_token)):
    """鎵嬪姩閲嶆柊涓婁紶鏌愪釜浜у搧鐨勫浘鐗?""
    await handle_risk("L2", "閲嶆柊涓婁紶浜у搧鍥剧墖", product_id)
    return {"product_id": product_id, "status": "queued"}


@router.get("/cos-status")
async def cos_status(_=Depends(verify_token)):
    """鏌ョ湅 COS 涓婁紶鐘舵€?""
    await handle_risk("L1", "鏌ョ湅COS鐘舵€?)
    from tools.cloud_storage import get_cos_status as _cos
    try:
        status = await _cos() if callable(_cos) else {"status": "鏈繛鎺?, "bucket": "N/A", "region": "N/A", "uploaded": 0, "usage": "0 MB"}
        return {"ok": True, "status": status}
    except Exception:
        return {"ok": True, "status": {"status": "鏈繛鎺?, "bucket": "N/A", "region": "N/A", "uploaded": 0, "usage": "0 MB"}}

@router.get("/sources")
@cached('scraper_sources', ttl=300)
async def list_sources(_=Depends(verify_token)):
    """鏌ョ湅鍙敤閲囬泦骞冲彴"""
    await handle_risk("L1", "鏌ョ湅閲囬泦骞冲彴")
    return {
        "sources": [
            {"id": "ebay",     "name": "eBay 鍏ㄧ悆绔?,       "type": "api",   "status": "ready"},
            {"id": "amazon",   "name": "Amazon 鍏ㄧ悆绔?,     "type": "scrape","status": "ready"},
            {"id": "aliexpress","name": "AliExpress 閫熷崠閫?, "type": "scrape","status": "ready"},
            {"id": "shopee",   "name": "Shopee 铏剧毊",       "type": "hybrid","status": "ready"},
            {"id": "lazada",   "name": "Lazada 鏉ヨ禐杈?,     "type": "scrape","status": "ready"},
            {"id": "wish",     "name": "Wish 鍏ㄧ悆绔?,       "type": "scrape","status": "ready"},
            {"id": "tiktok",   "name": "TikTok Shop",       "type": "scrape","status": "ready"},
            {"id": "taobao",  "name": "娣樺疂/澶╃尗",          "type": "scrape","status": "ready"},
            {"id": "alibaba1688","name": "1688闃块噷宸村反",     "type": "scrape","status": "ready"},
        ]
    }