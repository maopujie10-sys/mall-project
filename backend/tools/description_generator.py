锘?""AI鍟嗗搧鎻忚堪鐢熸垚鍣?鈥?澶氳瑷€SEO鎻忚堪+鍗栫偣鎻愬彇+鎵归噺鐢熸垚"""
import os, httpx, json
from datetime import datetime
from typing import Optional
from tools.logger import get_logger

logger = get_logger("desc_gen")

DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
AI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")

# 鏀寔鐨勮瑷€
LANGUAGES = {
    "zh": "涓枃", "en": "English", "es": "Espa帽ol", "fr": "Fran莽ais",
    "de": "Deutsch", "ja": "鏃ユ湰瑾?, "ko": "頃滉淡鞏?, "pt": "Portugu锚s",
    "ar": "丕賱毓乇亘賷丞", "ru": "袪褍褋褋泻懈泄", "th": "喙勦笚喔?, "vi": "Ti岷縩g Vi峄噒",
    "id": "Bahasa Indonesia", "ms": "Bahasa Melayu",
}

# 鎻忚堪妯℃澘
DESC_TEMPLATES = {
    "standard": "鏍囧噯鐢靛晢鎻忚堪锛堟爣棰?鍗栫偣+瑙勬牸+浣跨敤鍦烘櫙锛?,
    "seo": "SEO浼樺寲鎻忚堪锛堝叧閿瘝涓板瘜+缁撴瀯鍖?閫傚悎鎼滅储寮曟搸锛?,
    "social": "绀句氦濯掍綋椋庢牸锛堟椿娉?emoji+hashtag锛?,
    "minimalist": "鏋佺畝椋庢牸锛堜竴鍙ヨ瘽鍗栫偣+鍏抽敭鍙傛暟锛?,
}


class DescriptionGenerator:
    """AI澶氳瑷€鍟嗗搧鎻忚堪鐢熸垚鍣?""

    @classmethod
    async def generate(cls, product_name: str, category: str = "",
                        features: list = None, specs: dict = None,
                        target_lang: str = "zh", style: str = "standard",
                        keywords: list = None, brand: str = "",
                        max_length: int = 300) -> dict:
        """鐢熸垚鍗曚釜鍟嗗搧鎻忚堪"""
        features = features or []
        specs = specs or {}
        keywords = keywords or []

        # 鏋勫缓prompt
        style_desc = DESC_TEMPLATES.get(style, DESC_TEMPLATES["standard"])
        lang_name = LANGUAGES.get(target_lang, target_lang)

        prompt = f"""涓轰互涓嬪晢鍝佺敓鎴恵lang_name}鐨勭數鍟嗘弿杩?{style_desc}):

鍟嗗搧鍚嶇О: {product_name}
绫荤洰: {category}
鍝佺墝: {brand or "鏃?}
鏍稿績鍗栫偣: {", ".join(features) if features else "璇锋牴鎹晢鍝佸悕绉版帹鏂?}
瑙勬牸鍙傛暟: {json.dumps(specs, ensure_ascii=False) if specs else "鏃?}
SEO鍏抽敭璇? {", ".join(keywords) if keywords else "鑷姩鐢熸垚"}
瑕佹眰: 涓嶈秴杩噞max_length}瀛? 鍖呭惈鏍囬+鍗栫偣+瑙勬牸+浣跨敤鍦烘櫙, 瑕佹湁鍚稿紩鍔?

璇锋寜浠ヤ笅JSON鏍煎紡杈撳嚭:
{{"title": "鍟嗗搧鏍囬(鍚叧閿瘝)", "subtitle": "鍓爣棰?, "bullets": ["鍗栫偣1","鍗栫偣2","鍗栫偣3"], "description": "瀹屾暣鎻忚堪", "tags": ["鏍囩1","鏍囩2"], "seo_keywords": "SEO鍏抽敭璇嶄覆"}}"""

        ai_result = await cls._call_ai(prompt)
        if ai_result:
            return {**ai_result, "lang": target_lang, "style": style, "generated": True}

        # AI涓嶅彲鐢ㄦ椂闄嶇骇
        return cls._fallback_generate(product_name, category, features, target_lang, style)

    @classmethod
    async def generate_multilang(cls, product_name: str, category: str = "",
                                  features: list = None, specs: dict = None,
                                  languages: list = None, style: str = "standard",
                                  keywords: list = None) -> dict:
        """鐢熸垚澶氳瑷€鍟嗗搧鎻忚堪"""
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
        """鎵归噺鐢熸垚锛堟渶澶?0涓級"""
        results = []
        for p in products[:20]:
            try:
                desc = await cls.generate(
                    product_name=p.get("name", ""),
                    category=p.get("category", ""),
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
    async def extract_features(cls, product_name: str, raw_description: str = "") -> dict:
        """AI鎻愬彇鍟嗗搧鍗栫偣"""
        prompt = f"""鍒嗘瀽鍟嗗搧"{product_name}",鎻愬彇鏍稿績鍗栫偣鍜屽叧閿瘝銆?
{"鍙傝€冩弿杩? "+raw_description[:500] if raw_description else ""}

杈撳嚭JSON: {{"features":["鍗栫偣1","鍗栫偣2",...], "keywords":["鍏抽敭璇?",...], "target_audience":"鐩爣浜虹兢", "price_range":"寤鸿浠蜂綅"}}"""

        result = await cls._call_ai(prompt)
        return result or cls._fallback_features(product_name)

    @classmethod
    async def optimize_title(cls, title: str, keywords: list = None,
                               target_lang: str = "zh") -> str:
        """AI浼樺寲鍟嗗搧鏍囬锛圫EO鍙嬪ソ锛?""
        kw = ", ".join(keywords or [])
        prompt = f"""浼樺寲浠ヤ笅鍟嗗搧鏍囬涓篠EO鍙嬪ソ鐗堟湰(璇█:{LANGUAGES.get(target_lang,target_lang)}):
鍘熸爣棰? {title}
鍏抽敭璇? {kw or "鑷姩鎻愬彇"}
瑕佹眰: 50瀛椾互鍐? 鍖呭惈鏍稿績鍏抽敭璇? 鏈夊惛寮曞姏, 涓嶈"鎵瑰彂""鍘傚鐩撮攢"

鍙繑鍥炰紭鍖栧悗鐨勬爣棰?涓嶈繑鍥炲叾浠栧唴瀹广€?""

        result = await cls._call_ai(prompt, max_tokens=80)
        if result and isinstance(result, str):
            return result.strip().strip('"').strip("'")
        return title

    @classmethod
    async def _call_ai(cls, prompt: str, max_tokens: int = 500) -> Optional[dict]:
        """璋冪敤AI妯″瀷"""
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
                            {"role": "system", "content": "浣犳槸鐢靛晢鏂囨涓撳銆傚彧杩斿洖瑕佹眰鐨凧SON鏍煎紡锛屼笉杩斿洖澶氫綑鍐呭銆?},
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
                        # 杩斿洖绾枃鏈?
                        return {"title": content[:100], "description": content}
        except Exception as e:
            logger.info(f"AI璋冪敤澶辫触: {e}")
        return None

    @classmethod
    def _fallback_generate(cls, name: str, category: str, features: list,
                            lang: str, style: str) -> dict:
        """AI涓嶅彲鐢ㄦ椂鐨勬ā鏉块檷绾?""
        feat_text = "銆?.join(features) if features else "楂樺搧璐ㄣ€佺儹閿€鐖嗘"
        return {
            "title": f"銆愮儹鍗栥€憑name} {category}",
            "subtitle": f"绮鹃€墈category}锛屽搧璐ㄤ繚璇?,
            "bullets": [f"鉁?{f}" for f in (features or ["鍝佽川淇濊瘉", "蹇€熷彂璐?, "鍞悗鏃犲咖"])][:5],
            "description": f"{name} 鈥?{feat_text}銆傞€傜敤浜庢棩甯镐娇鐢紝鎬т环姣旇秴楂樸€?,
            "tags": [category, "鐑崠", "鍝佽川"],
            "seo_keywords": f"{name},{category},鐑崠,鍝佽川",
            "lang": lang,
            "style": style,
            "generated": True,
            "ai_fallback": True,
        }

    @classmethod
    def _fallback_features(cls, name: str) -> dict:
        return {
            "features": ["鍝佽川淇濊瘉", "蹇€熷彂璐?, "鍞悗鏃犲咖"],
            "keywords": [name, "鐑崠"],
            "target_audience": "澶т紬娑堣垂鑰?,
            "price_range": "涓瓑浠蜂綅",
        }

    @classmethod
    def get_languages(cls) -> dict:
        return LANGUAGES

    @classmethod
    def get_styles(cls) -> dict:
        return DESC_TEMPLATES


desc_gen = DescriptionGenerator()
