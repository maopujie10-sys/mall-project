锘?""AI鍟嗗搧鎻忚堪API 鈥?鐢熸垚+澶氳瑷€+鏍囬浼樺寲+鍗栫偣鎻愬彇"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from tools.description_generator import desc_gen

router = APIRouter(prefix="/agent/description", tags=["Description"])


class DescRequest(BaseModel):
    product_name: str
    category: str = ""
    features: list = []
    specs: dict = {}
    target_lang: str = "zh"
    style: str = "standard"
    keywords: list = []
    brand: str = ""
    max_length: int = 300


class MultiLangRequest(BaseModel):
    product_name: str
    category: str = ""
    features: list = []
    specs: dict = {}
    languages: list = ["zh", "en", "es"]
    style: str = "standard"
    keywords: list = []


class BatchDescRequest(BaseModel):
    products: list
    languages: list = ["zh", "en"]
    style: str = "standard"


class TitleRequest(BaseModel):
    title: str
    keywords: list = []
    target_lang: str = "zh"


@router.post("/generate")
async def generate_description(req: DescRequest, _=Depends(verify_token)):
    """鐢熸垚鍟嗗搧鎻忚堪"""
    if not req.product_name.strip():
        raise HTTPException(400, "鍟嗗搧鍚嶇О涓嶈兘涓虹┖")
    result = await desc_gen.generate(
        product_name=req.product_name.strip(),
        category=req.category,
        features=req.features,
        specs=req.specs,
        target_lang=req.target_lang,
        style=req.style,
        keywords=req.keywords,
        brand=req.brand,
        max_length=req.max_length,
    )
    return {"ok": True, "data": result}


@router.post("/multilang")
async def multilang_description(req: MultiLangRequest, _=Depends(verify_token)):
    """鐢熸垚澶氳瑷€鎻忚堪"""
    if not req.product_name.strip():
        raise HTTPException(400, "鍟嗗搧鍚嶇О涓嶈兘涓虹┖")
    if len(req.languages) > 8:
        raise HTTPException(400, "鏈€澶?绉嶈瑷€")
    result = await desc_gen.generate_multilang(
        product_name=req.product_name,
        category=req.category,
        features=req.features,
        specs=req.specs,
        languages=req.languages,
        style=req.style,
        keywords=req.keywords,
    )
    return {"ok": True, "data": result}


@router.post("/batch")
async def batch_generate(req: BatchDescRequest, _=Depends(verify_token)):
    """鎵归噺鐢熸垚鎻忚堪"""
    if not req.products:
        raise HTTPException(400, "浜у搧鍒楄〃涓嶈兘涓虹┖")
    if len(req.products) > 20:
        raise HTTPException(400, "鍗曟鏈€澶?0涓骇鍝?)
    results = await desc_gen.batch_generate(req.products, req.languages, req.style)
    return {"ok": True, "total": len(results), "results": results}


@router.post("/extract-features")
async def extract_features(product_name: str = Query(...), raw_description: str = Query(""), _=Depends(verify_token)):
    """AI鎻愬彇鍟嗗搧鍗栫偣"""
    result = await desc_gen.extract_features(product_name, raw_description)
    return {"ok": True, "data": result}


@router.post("/optimize-title")
async def optimize_title(req: TitleRequest, _=Depends(verify_token)):
    """AI浼樺寲鍟嗗搧鏍囬"""
    result = await desc_gen.optimize_title(req.title, req.keywords, req.target_lang)
    return {"ok": True, "original": req.title, "optimized": result}


@router.get("/languages")
async def supported_languages(_=Depends(verify_token)):
    """鏀寔鐨勮瑷€鍒楄〃"""
    return {"ok": True, "languages": desc_gen.get_languages()}


@router.get("/styles")
async def description_styles(_=Depends(verify_token)):
    """鏀寔鐨勬弿杩伴鏍?""
    return {"ok": True, "styles": desc_gen.get_styles()}
