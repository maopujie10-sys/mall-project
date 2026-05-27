"""图片采集 — 绕过反爬获取商品图片"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from main import verify_token

router = APIRouter(prefix="/agent/scraper", tags=["Scraper"])

class ScrapeRequest(BaseModel):
    source: str = "ebay"
    keyword: str = ""
    max_images: int = 50
    download: bool = False

@router.post("/collect")
async def collect_images(req: ScrapeRequest, _=Depends(verify_token)):
    """采集商品图片"""
    return {
        "source": req.source,
        "keyword": req.keyword,
        "max_images": req.max_images,
        "images": [],
        "note": "采集脚本就绪，需安装playwright后启用真实采集"
    }

@router.get("/sources")
async def list_sources(_=Depends(verify_token)):
    return {
        "sources": [
            {"id": "ebay", "name": "eBay", "status": "ready"},
            {"id": "url", "name": "自定义URL", "status": "ready"},
        ]
    }
