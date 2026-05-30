"""AI -- //SEO/v2 """
from fastapi import APIRouter, Depends, Query
from auth import verify_token
from risk import handle_risk
from datetime import datetime

router = APIRouter(prefix="/agent/copy", tags=["AICopy"])

LANGUAGES = {
    "zh": '', "en": "English", "ja": '', "ko": "",
    "th": "", "vi": "Ting Vit", "ms": "Bahasa Melayu",
    "id": "Bahasa Indonesia", "es": "Espaol", "fr": "Franais",
    "de": "Deutsch", "pt": "Portugus", "ar": "", "ru": ""
}

@router.post("/generate")
async def generate_copy(product_name: str = Query(...), category: str = '', features: str = '',
                         language: str = "en", tone: str = "professional", _=Depends(verify_token)):
    ''"AI''"
    await handle_risk("L1", f"{language}: {product_name}")
    lang_name = LANGUAGES.get(language, "English")
    
    # AI
    try:
        from config import OPENAI_API_KEY, OPENAI_BASE_URL
        if OPENAI_API_KEY:
            import httpx
            async with httpx.AsyncClient(timeout=20) as c:
                prompt = f''"You are a professional e-commerce copywriter. Generate product copy in {lang_name} ({language}).

Product: {product_name}
Category: {category or 'General'}
Features: {features or 'Standard'}
Tone: {tone}

Return JSON only:
{{"title": "product title in {lang_name}",
  "description": "2-3 sentence product description in {lang_name}",
  "seo_keywords": "comma-separated SEO keywords in {lang_name}",
  "bullet_points": ["point1 in {lang_name}", "point2 in {lang_name}", "point3 in {lang_name}"]}}''"
                resp = await c.post(f"{OPENAI_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    json={"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}], "max_tokens": 500},
                    timeout=30)
                data = resp.json()
                text = data.get("choices", [{}])[0].get("message", {}).get("content", '')
                import json
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    result = json.loads(text[start:end])
                    return {"ok": True, "product": product_name, "language": language,
                            "lang_name": lang_name, "generated_by": "ai", **result}
    except: pass

    # ()
    tones = {"professional": {"zh":'',"en":"Professional","ja":"","ko":""},
             "friendly": {"zh":'',"en":"Friendly","ja":"","ko":""},
             "luxury": {"zh":'',"en":"Luxury","ja":"","ko":""},
             "youth": {"zh":'',"en":"Youth","ja":"","ko":""}}
    tone_label = tones.get(tone, {}).get(language, tone)
    features_list = [f.strip() for f in features.split(",") if f.strip()]

    
    templates = {
        "zh": {"title": f"{category} | {product_name}" if category else product_name,
               "desc": f"{tone_label}{product_name}\n: {''.join(features_list[:5])}\n,.",
               "lang": ''},
        "en": {"title": f"{category} | {product_name}" if category else product_name,
               "desc": f"[{tone_label} Quality] {product_name}\nKey Features: {', '.join(features_list[:5])}\nPremium quality, trusted worldwide.",
               "lang": "English"},
        "ja": {"title": f"{product_name} | {category}" if category else product_name,
               "desc": f"{tone_label}{product_name}\n: {''.join(features_list[:5])}\n.",
               "lang": ''},
        "ko": {"title": f"{product_name} | {category}" if category else product_name,
               "desc": f"{tone_label} {product_name}\n : {', '.join(features_list[:5])}\n,    .",
               "lang": ""},
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
    ''''''
    return {"ok": True, "languages": [{"code": k, "name": v} for k, v in LANGUAGES.items()]}
