"""AI -- SEO++"""
import os, httpx, json
from datetime import datetime
from typing import Optional
from tools.logger import get_logger

logger = get_logger("desc_gen")

DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", '')
OPENAI_KEY = os.getenv("OPENAI_API_KEY", '')
AI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")


LANGUAGES = {
    "zh": '', "en": "English", "es": "Espaol", "fr": "Franais",
    "de": "Deutsch", "ja": '', "ko": "", "pt": "Portugus",
    "ar": "", "ru": "", "th": "", "vi": "Ting Vit",
    "id": "Bahasa Indonesia", "ms": "Bahasa Melayu",
}


DESC_TEMPLATES = {
    "standard": "(+++)",
    "seo": "SEO(++)",
    "social": "(+emoji+hashtag)",
    "minimalist": "(+)",
}


class DescriptionGenerator:
    ''"AI''"

    @classmethod
    async def generate(cls, product_name: str, category: str = '',
                        features: list = None, specs: dict = None,
                        target_lang: str = "zh", style: str = "standard",
                        keywords: list = None, brand: str = '',
                        max_length: int = 300) -> dict:
        ''''''
        features = features or []
        specs = specs or {}
        keywords = keywords or []

        # prompt
        style_desc = DESC_TEMPLATES.get(style, DESC_TEMPLATES["standard"])
        lang_name = LANGUAGES.get(target_lang, target_lang)

        prompt = f''"{lang_name}({style_desc}):

: {product_name}
: {category}
: {brand or ''}
: {", ".join(features) if features else ''}
: {json.dumps(specs, ensure_ascii=False) if specs else ''}
SEO: {", ".join(keywords) if keywords else ''}
: {max_length}, +++, 

JSON:
{{"title": "()", "subtitle": '', "bullets": ["1","2","3"], "description": '', "tags": ["1","2"], "seo_keywords": "SEO"}}''"

        ai_result = await cls._call_ai(prompt)
        if ai_result:
            return {**ai_result, "lang": target_lang, "style": style, "generated": True}

        # AI
        return cls._fallback_generate(product_name, category, features, target_lang, style)

    @classmethod
    async def generate_multilang(cls, product_name: str, category: str = '',
                                  features: list = None, specs: dict = None,
                                  languages: list = None, style: str = "standard",
                                  keywords: list = None) -> dict:
        ''''''
        languages = languages or ["zh", "en", "es"]
        results = {}
        for lang in languages:
            try:
                result = await cls.generate(
                    product_name, category, features, specs, lang, style, keywords
                )
                results[lang] = result
            except Exception as e:
                results[lang] = {"error": str(e)[:100], "lang": lang}
        return {
            "product": product_name,
            "languages": results,
            "total": len(results),
            "success": sum(1 for r in results.values() if r.get("generated")),
        }

    @classmethod
    async def batch_generate(cls, products: list, languages: list = None,
                              style: str = "standard") -> list:
        ''"(20)''"
        results = []
        for p in products[:20]:
            try:
                desc = await cls.generate(
                    product_name=p.get("name", ''),
                    category=p.get("category", ''),
                    features=p.get("features", []),
                    specs=p.get("specs", {}),
                    target_lang=p.get("lang", "zh"),
                    style=style,
                    keywords=p.get("keywords", []),
                )
                results.append({"product": p.get("name"), "result": desc})
            except Exception as e:
                results.append({"product": p.get("name"), "error": str(e)[:100]})
        return results

    @classmethod
    async def extract_features(cls, product_name: str, raw_description: str = '') -> dict:
        ''"AI''"
        prompt = f''''{product_name}",.
{": "+raw_description[:500] if raw_description else ''}

JSON: {{"features":["1","2",...], "keywords":["1",...], "target_audience":'', "price_range":''}}''"

        result = await cls._call_ai(prompt)
        return result or cls._fallback_features(product_name)

    @classmethod
    async def optimize_title(cls, title: str, keywords: list = None,
                               target_lang: str = "zh") -> str:
        ''"AI(SEO)''"
        kw = ", ".join(keywords or [])
        prompt = f''"SEO(:{LANGUAGES.get(target_lang,target_lang)}):
: {title}
: {kw or ''}
: 50, , ''''

,.''"

        result = await cls._call_ai(prompt, max_tokens=80)
        if result and isinstance(result, str):
            return result.strip().strip(''').strip(''")
        return title

    @classmethod
    async def _call_ai(cls, prompt: str, max_tokens: int = 500) -> Optional[dict]:
        ''"AI''"
        if not (DEEPSEEK_KEY or OPENAI_KEY):
            return None
        try:
            key = DEEPSEEK_KEY or OPENAI_KEY
            api_url = "https://api.deepseek.com/v1/chat/completions" if DEEPSEEK_KEY else f"{AI_BASE_URL}/chat/completions"
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post(api_url,
                    headers={"Authorization": f"Bearer {key}"},
                    json={
                        "model": AI_MODEL,
                        "messages": [
                            {"role": "system", "content": ".JSON,."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": max_tokens,
                        "response_format": {"type": "json_object"} if "json" in prompt.lower() else None,
                    })
                if r.status_code == 200:
                    content = r.json()["choices"][0]["message"]["content"].strip()
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        
                        return {"title": content[:100], "description": content}
        except Exception as e:
            logger.info(f"AI: {e}")
        return None

    @classmethod
    def _fallback_generate(cls, name: str, category: str, features: list,
                            lang: str, style: str) -> dict:
        ''"AI''"
        feat_text = "".join(features) if features else ""
        return {
            "title": f"{name} {category}",
            "subtitle": f"{category},",
            "bullets": [f" {f}" for f in (features or ['', '', ''])][:5],
            "description": f"{name} -- {feat_text}.,.",
            "tags": [category, '', ''],
            "seo_keywords": f"{name},{category},",
            "lang": lang,
            "style": style,
            "generated": True,
            "ai_fallback": True,
        }

    @classmethod
    def _fallback_features(cls, name: str) -> dict:
        return {
            "features": ['', '', ''],
            "keywords": [name, ''],
            "target_audience": '',
            "price_range": '',
        }

    @classmethod
    def get_languages(cls) -> dict:
        return LANGUAGES

    @classmethod
    def get_styles(cls) -> dict:
        return DESC_TEMPLATES


desc_gen = DescriptionGenerator()
