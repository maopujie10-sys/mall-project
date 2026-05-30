""" -- +/v1"""
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from state import state
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/agent/translate", tags=["MultiLangPublish"])

PRODUCT_FIELDS = {"title":'',"description":'',"keywords":'',"specs":''}

class ProductContent(BaseModel):
    title: str
    description: str = ''
    keywords: str = ''
    specs: str = ''

class PublishRequest(BaseModel):
    content: ProductContent
    target_langs: list[str] = ["en","ja","ko"]
    platforms: list[str] = ["shopify","etsy","amazon"]

@router.post("/translate")
async def translate_product(req: ProductContent, target_lang: str = "en", _=Depends(verify_token)):
    ''"AI''"
    await handle_risk("L1", "AI")
    translated = {}
    for field in ["title","description","keywords","specs"]:
        text = getattr(req, field, '')
        if text:
            translated[field] = f"[{target_lang.upper()}] {text} ()"
        else:
            translated[field] = text
    return {"ok": True, "source_lang": "zh", "target_lang": target_lang, "translated": translated}

@router.post("/publish")
async def publish_to_platforms(req: PublishRequest, _=Depends(verify_token)):
    ''''''
    await handle_risk("L2", f"{len(req.platforms)}")
    results = []
    for lang in req.target_langs:
        for platform in req.platforms:
            results.append({"platform": platform, "language": lang, "status": "published",
                            "url": f"https://{platform}.com/item/{datetime.now().strftime('%s')}",
                            "time": datetime.now().isoformat()})
    log = {"time": datetime.now().isoformat(), "content_preview": req.content.title[:50],
           "languages": req.target_langs, "platforms": req.platforms, "results": results}
    state.append_data("publish_logs", log, 200)
    return {"ok": True, "publish_id": f"PUB{datetime.now().strftime('%Y%m%d%H%M%S')}", "results": results}

@router.get("/languages")
async def supported_languages(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "languages": [
        {"code":"en","name":"English","icon":"","available":True},
        {"code":"ja","name":'',"icon":"","available":True},
        {"code":"ko","name":"","icon":"","available":True},
        {"code":"th","name":"","icon":"","available":True},
        {"code":"vi","name":"Ting Vit","icon":"","available":True},
        {"code":"es","name":"Espaol","icon":"","available":True},
        {"code":"ar","name":"","icon":"","available":True}]}

@router.get("/platforms")
async def supported_platforms(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "platforms": [
        {"id":"shopify","name":"Shopify","icon":"","enabled":True},
        {"id":"etsy","name":"Etsy","icon":"","enabled":True},
        {"id":"amazon","name":"Amazon","icon":"","enabled":True},
        {"id":"ebay","name":"eBay","icon":"","enabled":True},
        {"id":"aliexpress","name":"AliExpress","icon":"","enabled":True}]}

@router.get("/history")
async def publish_history(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "logs": state._data.get("publish_logs", [])[-30:]}
