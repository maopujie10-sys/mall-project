"""AI商品文案生成 — 多语言标题/描述/SEO/v2 支持全球语言"""
from fastapi import APIRouter, Depends, Query
from auth import verify_token
from risk import handle_risk
from datetime import datetime

router = APIRouter(prefix="/agent/copy", tags=["AICopy"])

LANGUAGES = {
    "zh": "中文", "en": "English", "ja": "日本語", "ko": "한국어",
    "th": "ไทย", "vi": "Tiếng Việt", "ms": "Bahasa Melayu",
    "id": "Bahasa Indonesia", "es": "Español", "fr": "Français",
    "de": "Deutsch", "pt": "Português", "ar": "العربية", "ru": "Русский"
}

@router.post("/generate")
async def generate_copy(product_name: str = Query(...), category: str = "", features: str = "",
                         language: str = "en", tone: str = "professional", _=Depends(verify_token)):
    """AI生成多语言商品文案"""
    await handle_risk("L1", f"生成{language}文案: {product_name}")
    lang_name = LANGUAGES.get(language, "English")
    
    # 尝试用AI模型生成
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

    # 内置模板（多语言）
    tones = {"professional": {"zh":"专业","en":"Professional","ja":"プロフェッショナル","ko":"프로페셔널"},
             "friendly": {"zh":"亲切","en":"Friendly","ja":"フレンドリー","ko":"친근한"},
             "luxury": {"zh":"高端","en":"Luxury","ja":"ラグジュアリー","ko":"럭셔리"},
             "youth": {"zh":"年轻","en":"Youth","ja":"ヤング","ko":"청년"}}
    tone_label = tones.get(tone, {}).get(language, tone)
    features_list = [f.strip() for f in features.split(",") if f.strip()]

    # 语言特定模板
    templates = {
        "zh": {"title": f"{category} | {product_name}" if category else product_name,
               "desc": f"【{tone_label}品质】{product_name}\n核心特点: {'、'.join(features_list[:5])}\n品质保证，值得信赖。",
               "lang": "中文"},
        "en": {"title": f"{category} | {product_name}" if category else product_name,
               "desc": f"[{tone_label} Quality] {product_name}\nKey Features: {', '.join(features_list[:5])}\nPremium quality, trusted worldwide.",
               "lang": "English"},
        "ja": {"title": f"{product_name} | {category}" if category else product_name,
               "desc": f"【{tone_label}品質】{product_name}\n主な特徴: {'、'.join(features_list[:5])}\n高品質で信頼できる製品です。",
               "lang": "日本語"},
        "ko": {"title": f"{product_name} | {category}" if category else product_name,
               "desc": f"【{tone_label} 품질】{product_name}\n주요 특징: {', '.join(features_list[:5])}\n고품질, 신뢰할 수 있는 제품.",
               "lang": "한국어"},
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
    """支持的语言列表"""
    return {"ok": True, "languages": [{"code": k, "name": v} for k, v in LANGUAGES.items()]}
