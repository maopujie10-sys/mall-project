"""AIAPI -- +++"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from tools.description_generator import desc_gen

router = APIRouter(prefix="/agent/description", tags=["Description"])


class DescRequest(BaseModel):
    product_name: str
    category: str = ''
    features: list = []
    specs: dict = {}
    target_lang: str = "zh"
    style: str = "standard"
    keywords: list = []
    brand: str = ''
    max_length: int = 300


class MultiLangRequest(BaseModel):
    product_name: str
    category: str = ''
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
    ''''''
    if not req.product_name.strip():
        raise HTTPException(400, '')
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
    ''''''
    if not req.product_name.strip():
        raise HTTPException(400, '')
    if len(req.languages) > 8:
        raise HTTPException(400, "8")
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
    ''''''
    if not req.products:
        raise HTTPException(400, '')
    if len(req.products) > 20:
        raise HTTPException(400, "20")
    results = await desc_gen.batch_generate(req.products, req.languages, req.style)
    return {"ok": True, "total": len(results), "results": results}


@router.post("/extract-features")
async def extract_features(product_name: str = Query(...), raw_description: str = Query(''), _=Depends(verify_token)):
    ''"AI''"
    result = await desc_gen.extract_features(product_name, raw_description)
    return {"ok": True, "data": result}


@router.post("/optimize-title")
async def optimize_title(req: TitleRequest, _=Depends(verify_token)):
    ''"AI''"
    result = await desc_gen.optimize_title(req.title, req.keywords, req.target_lang)
    return {"ok": True, "original": req.title, "optimized": result}


@router.get("/languages")
async def supported_languages(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "languages": desc_gen.get_languages()}


@router.get("/styles")
async def description_styles(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "styles": desc_gen.get_styles()}
