"""AI商品描述生成器 — 多语言SEO描述+卖点提取+批量生成"""
import os, httpx, json
from datetime import datetime
from typing import Optional
from tools.logger import get_logger

logger = get_logger("desc_gen")

DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
AI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")

# 支持的语言
LANGUAGES = {
    "zh": "中文", "en": "English", "es": "Español", "fr": "Français",
    "de": "Deutsch", "ja": "日本語", "ko": "한국어", "pt": "Português",
    "ar": "العربية", "ru": "Русский", "th": "ไทย", "vi": "Tiếng Việt",
    "id": "Bahasa Indonesia", "ms": "Bahasa Melayu",
}

# 描述模板
DESC_TEMPLATES = {
    "standard": "标准电商描述（标题+卖点+规格+使用场景）",
    "seo": "SEO优化描述（关键词丰富+结构化+适合搜索引擎）",
    "social": "社交媒体风格（活泼+emoji+hashtag）",
    "minimalist": "极简风格（一句话卖点+关键参数）",
}


class DescriptionGenerator:
    """AI多语言商品描述生成器"""

    @classmethod
    async def generate(cls, product_name: str, category: str = "",
                        features: list = None, specs: dict = None,
                        target_lang: str = "zh", style: str = "standard",
                        keywords: list = None, brand: str = "",
                        max_length: int = 300) -> dict:
        """生成单个商品描述"""
        features = features or []
        specs = specs or {}
        keywords = keywords or []

        # 构建prompt
        style_desc = DESC_TEMPLATES.get(style, DESC_TEMPLATES["standard"])
        lang_name = LANGUAGES.get(target_lang, target_lang)

        prompt = f"""为以下商品生成{lang_name}的电商描述({style_desc}):

商品名称: {product_name}
类目: {category}
品牌: {brand or "无"}
核心卖点: {", ".join(features) if features else "请根据商品名称推断"}
规格参数: {json.dumps(specs, ensure_ascii=False) if specs else "无"}
SEO关键词: {", ".join(keywords) if keywords else "自动生成"}
要求: 不超过{max_length}字, 包含标题+卖点+规格+使用场景, 要有吸引力

请按以下JSON格式输出:
{{"title": "商品标题(含关键词)", "subtitle": "副标题", "bullets": ["卖点1","卖点2","卖点3"], "description": "完整描述", "tags": ["标签1","标签2"], "seo_keywords": "SEO关键词串"}}"""

        ai_result = await cls._call_ai(prompt)
        if ai_result:
            return {**ai_result, "lang": target_lang, "style": style, "generated": True}

        # AI不可用时降级
        return cls._fallback_generate(product_name, category, features, target_lang, style)

    @classmethod
    async def generate_multilang(cls, product_name: str, category: str = "",
                                  features: list = None, specs: dict = None,
                                  languages: list = None, style: str = "standard",
                                  keywords: list = None) -> dict:
        """生成多语言商品描述"""
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
        """批量生成（最多20个）"""
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
        """AI提取商品卖点"""
        prompt = f"""分析商品"{product_name}",提取核心卖点和关键词。
{"参考描述: "+raw_description[:500] if raw_description else ""}

输出JSON: {{"features":["卖点1","卖点2",...], "keywords":["关键词1",...], "target_audience":"目标人群", "price_range":"建议价位"}}"""

        result = await cls._call_ai(prompt)
        return result or cls._fallback_features(product_name)

    @classmethod
    async def optimize_title(cls, title: str, keywords: list = None,
                               target_lang: str = "zh") -> str:
        """AI优化商品标题（SEO友好）"""
        kw = ", ".join(keywords or [])
        prompt = f"""优化以下商品标题为SEO友好版本(语言:{LANGUAGES.get(target_lang,target_lang)}):
原标题: {title}
关键词: {kw or "自动提取"}
要求: 50字以内, 包含核心关键词, 有吸引力, 不说"批发""厂家直销"

只返回优化后的标题,不返回其他内容。"""

        result = await cls._call_ai(prompt, max_tokens=80)
        if result and isinstance(result, str):
            return result.strip().strip('"').strip("'")
        return title

    @classmethod
    async def _call_ai(cls, prompt: str, max_tokens: int = 500) -> Optional[dict]:
        """调用AI模型"""
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
                            {"role": "system", "content": "你是电商文案专家。只返回要求的JSON格式，不返回多余内容。"},
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
                        # 返回纯文本
                        return {"title": content[:100], "description": content}
        except Exception as e:
            logger.info(f"AI调用失败: {e}")
        return None

    @classmethod
    def _fallback_generate(cls, name: str, category: str, features: list,
                            lang: str, style: str) -> dict:
        """AI不可用时的模板降级"""
        feat_text = "、".join(features) if features else "高品质、热销爆款"
        return {
            "title": f"【热卖】{name} {category}",
            "subtitle": f"精选{category}，品质保证",
            "bullets": [f"✓ {f}" for f in (features or ["品质保证", "快速发货", "售后无忧"])][:5],
            "description": f"{name} — {feat_text}。适用于日常使用，性价比超高。",
            "tags": [category, "热卖", "品质"],
            "seo_keywords": f"{name},{category},热卖,品质",
            "lang": lang,
            "style": style,
            "generated": True,
            "ai_fallback": True,
        }

    @classmethod
    def _fallback_features(cls, name: str) -> dict:
        return {
            "features": ["品质保证", "快速发货", "售后无忧"],
            "keywords": [name, "热卖"],
            "target_audience": "大众消费者",
            "price_range": "中等价位",
        }

    @classmethod
    def get_languages(cls) -> dict:
        return LANGUAGES

    @classmethod
    def get_styles(cls) -> dict:
        return DESC_TEMPLATES


desc_gen = DescriptionGenerator()
