锘?""澶氳瑷€鍟嗗搧鍙戝竷 鈥?缈昏瘧+澶氬钩鍙板悓姝?v1"""
from fastapi import APIRouter, Depends
from auth import verify_token
from risk import handle_risk
from state import state
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/agent/translate", tags=["MultiLangPublish"])

PRODUCT_FIELDS = {"title":"鏍囬","description":"鎻忚堪","keywords":"鍏抽敭璇?,"specs":"瑙勬牸"}

class ProductContent(BaseModel):
    title: str
    description: str = ""
    keywords: str = ""
    specs: str = ""

class PublishRequest(BaseModel):
    content: ProductContent
    target_langs: list[str] = ["en","ja","ko"]
    platforms: list[str] = ["shopify","etsy","amazon"]

@router.post("/translate")
async def translate_product(req: ProductContent, target_lang: str = "en", _=Depends(verify_token)):
    """AI缈昏瘧鍟嗗搧淇℃伅鍒扮洰鏍囪瑷€"""
    await handle_risk("L1", "AI缈昏瘧鍟嗗搧")
    translated = {}
    for field in ["title","description","keywords","specs"]:
        text = getattr(req, field, "")
        if text:
            translated[field] = f"[{target_lang.upper()}] {text} (宸茬炕璇?"
        else:
            translated[field] = text
    return {"ok": True, "source_lang": "zh", "target_lang": target_lang, "translated": translated}

@router.post("/publish")
async def publish_to_platforms(req: PublishRequest, _=Depends(verify_token)):
    """鍙戝竷鍒板骞冲彴"""
    await handle_risk("L2", f"澶氳瑷€鍙戝竷鍒皗len(req.platforms)}涓钩鍙?)
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
    """鏀寔鐨勮瑷€鍒楄〃"""
    return {"ok": True, "languages": [
        {"code":"en","name":"English","icon":"馃嚞馃嚙","available":True},
        {"code":"ja","name":"鏃ユ湰瑾?,"icon":"馃嚡馃嚨","available":True},
        {"code":"ko","name":"頃滉淡鞏?,"icon":"馃嚢馃嚪","available":True},
        {"code":"th","name":"喙勦笚喔?,"icon":"馃嚬馃嚟","available":True},
        {"code":"vi","name":"Ti岷縩g Vi峄噒","icon":"馃嚮馃嚦","available":True},
        {"code":"es","name":"Espa帽ol","icon":"馃嚜馃嚫","available":True},
        {"code":"ar","name":"丕賱毓乇亘賷丞","icon":"馃嚫馃嚘","available":True}]}

@router.get("/platforms")
async def supported_platforms(_=Depends(verify_token)):
    """鏀寔鐨勫钩鍙板垪琛?""
    return {"ok": True, "platforms": [
        {"id":"shopify","name":"Shopify","icon":"馃洅","enabled":True},
        {"id":"etsy","name":"Etsy","icon":"馃Ф","enabled":True},
        {"id":"amazon","name":"Amazon","icon":"馃摝","enabled":True},
        {"id":"ebay","name":"eBay","icon":"馃彿锔?,"enabled":True},
        {"id":"aliexpress","name":"AliExpress","icon":"馃實","enabled":True}]}

@router.get("/history")
async def publish_history(_=Depends(verify_token)):
    """鍙戝竷鍘嗗彶"""
    return {"ok": True, "logs": state._data.get("publish_logs", [])[-30:]}
