锘?""AI鍟嗗搧鏂囨鐢熸垚 鈥?澶氳瑷€鏍囬/鎻忚堪/SEO/v2 鏀寔鍏ㄧ悆璇█"""
from fastapi import APIRouter, Depends, Query
from auth import verify_token
from risk import handle_risk
from datetime import datetime

router = APIRouter(prefix="/agent/copy", tags=["AICopy"])

LANGUAGES = {
    "zh": "涓枃", "en": "English", "ja": "鏃ユ湰瑾?, "ko": "頃滉淡鞏?,
    "th": "喙勦笚喔?, "vi": "Ti岷縩g Vi峄噒", "ms": "Bahasa Melayu",
    "id": "Bahasa Indonesia", "es": "Espa帽ol", "fr": "Fran莽ais",
    "de": "Deutsch", "pt": "Portugu锚s", "ar": "丕賱毓乇亘賷丞", "ru": "袪褍褋褋泻懈泄"
}

@router.post("/generate")
async def generate_copy(product_name: str = Query(...), category: str = "", features: str = "",
                         language: str = "en", tone: str = "professional", _=Depends(verify_token)):
    """AI鐢熸垚澶氳瑷€鍟嗗搧鏂囨"""
    await handle_risk("L1", f"鐢熸垚{language}鏂囨: {product_name}")
    lang_name = LANGUAGES.get(language, "English")
    
    # 灏濊瘯鐢ˋI妯″瀷鐢熸垚
    try:
        from config import OPENAI_API_KEY, OPENAI_BASE_URL
        if OPENAI_API_KEY:
            import httpx
            async with httpx.AsyncClient(timeout=20) as c:
                prompt = f"""You are a professional e-commerce copywriter. Generate product copy in {lang_name} ({language}).

Product: {product_name}
Category: {category or 'General'}
Features: {features or 'Standard'}
Tone: {tone}

Return JSON only:
{{"title": "product title in {lang_name}",
  "description": "2-3 sentence product description in {lang_name}",
  "seo_keywords": "comma-separated SEO keywords in {lang_name}",
  "bullet_points": ["point1 in {lang_name}", "point2 in {lang_name}", "point3 in {lang_name}"]}}"""
                resp = await c.post(f"{OPENAI_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    json={"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}], "max_tokens": 500},
                    timeout=30)
                data = resp.json()
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                import json
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    result = json.loads(text[start:end])
                    return {"ok": True, "product": product_name, "language": language,
                            "lang_name": lang_name, "generated_by": "ai", **result}
    except: pass

    # 鍐呯疆妯℃澘锛堝璇█锛?    tones = {"professional": {"zh":"涓撲笟","en":"Professional","ja":"銉椼儹銉曘偋銉冦偡銉с儕銉?,"ko":"頂勲韼橃厰雱?},
             "friendly": {"zh":"浜插垏","en":"Friendly","ja":"銉曘儸銉炽儔銉兗","ko":"旃滉芳頃?},
             "luxury": {"zh":"楂樼","en":"Luxury","ja":"銉┿偘銈搞儱銈儶銉?,"ko":"霟厰毽?},
             "youth": {"zh":"骞磋交","en":"Youth","ja":"銉ゃ兂銈?,"ko":"觳厔"}}
    tone_label = tones.get(tone, {}).get(language, tone)
    features_list = [f.strip() for f in features.split(",") if f.strip()]

    # 璇█鐗瑰畾妯℃澘
    templates = {
        "zh": {"title": f"{category} | {product_name}" if category else product_name,
               "desc": f"銆恵tone_label}鍝佽川銆憑product_name}\n鏍稿績鐗圭偣: {'銆?.join(features_list[:5])}\n鍝佽川淇濊瘉锛屽€煎緱淇¤禆銆?,
               "lang": "涓枃"},
        "en": {"title": f"{category} | {product_name}" if category else product_name,
               "desc": f"[{tone_label} Quality] {product_name}\nKey Features: {', '.join(features_list[:5])}\nPremium quality, trusted worldwide.",
               "lang": "English"},
        "ja": {"title": f"{product_name} | {category}" if category else product_name,
               "desc": f"銆恵tone_label}鍝佽唱銆憑product_name}\n涓汇仾鐗瑰敬: {'銆?.join(features_list[:5])}\n楂樺搧璩仹淇￠牸銇с亶銈嬭＝鍝併仹銇欍€?,
               "lang": "鏃ユ湰瑾?},
        "ko": {"title": f"{product_name} | {category}" if category else product_name,
               "desc": f"銆恵tone_label} 頀堨銆憑product_name}\n欤检殧 韸轨: {', '.join(features_list[:5])}\n瓿犿拡歆? 鞁犽頃?靾?鞛堧姅 鞝滍拡.",
               "lang": "頃滉淡鞏?},
    }
    tpl = templates.get(language, templates["en"])
    seo = [product_name, category] if category else [product_name]
    seo += features_list[:3]

    return {"ok": True, "product": product_name, "language": language,
            "lang_name": tpl["lang"], "generated_by": "template",
            "title": tpl["title"], "description": tpl["desc"],
            "seo_keywords": ", ".join(seo),
            "bullet_points": features_list[:5] or [f"{product_name} - {tone_label} Quality"]}

@router.get("/languages")
async def list_languages(_=Depends(verify_token)):
    """鏀寔鐨勮瑷€鍒楄〃"""
    return {"ok": True, "languages": [{"code": k, "name": v} for k, v in LANGUAGES.items()]}
