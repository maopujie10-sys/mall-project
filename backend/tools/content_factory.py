"""AI内容工厂 — 商品描述+营销文案+社媒帖子+翻译"""
import json, re
from tools.logger import get_logger

logger = get_logger("content_factory")

class ContentFactory:
    """AI内容生成工厂"""

    @classmethod
    async def generate_product_desc(cls, product_info: dict) -> str:
        """生成商品描述"""
        try:
            from agents.multi_model import ModelRouter
            resp = await ModelRouter.smart_chat(messages=[{"role":"user","content":f"为以下商品写一段有吸引力的描述(100-200字),突出卖点:\n名称:{product_info.get('name','')}\n品类:{product_info.get('category','')}\n价格:{product_info.get('price','')}\n特点:{product_info.get('features','')}"}], mode="fast")
            return resp.get("content", "")
        except Exception as e:
            logger.error(f"生成商品描述失败: {e}")
            return f"【{product_info.get('name','')}】高品质{product_info.get('category','')}，价格{product_info.get('price','')}，{product_info.get('features','')}"

    @classmethod
    async def generate_marketing_copy(cls, campaign: dict) -> str:
        """生成营销文案"""
        try:
            from agents.multi_model import ModelRouter
            resp = await ModelRouter.smart_chat(messages=[{"role":"user","content":f"为以下营销活动写一条吸引人的推广文案(50-100字),带emoji:\n活动:{campaign.get('name','')}\n优惠:{campaign.get('discount','')}\n目标人群:{campaign.get('audience','')}\n平台:{campaign.get('platform','全平台')}"}], mode="fast")
            return resp.get("content", "")
        except:
            return f"🎉 {campaign.get(\"name\",\"\")}来啦！{campaign.get(\"discount\",\"\")}，限时优惠！"

    @classmethod
    async def generate_social_post(cls, topic: dict) -> str:
        """生成社媒帖子"""
        try:
            from agents.multi_model import ModelRouter
            resp = await ModelRouter.smart_chat(messages=[{"role":"user","content":f"写一条社交媒体帖子(100-200字),带3-5个相关hashtag:\n主题:{topic.get('theme','')}\n风格:{topic.get('style','轻松活泼')}\n包含: {topic.get('include','')}"}], mode="fast")
            return resp.get("content", "")
        except:
            return f"📢 {topic.get('theme','')}\n{topic.get('include','')}\n#好物 #推荐 #跨境电商 #TikTokShop"

    @classmethod
    async def translate_content(cls, text: str, target_lang: str = "en") -> str:
        """翻译内容"""
        lang_names = {"en":"英语","ja":"日语","ko":"韩语","fr":"法语","de":"德语","es":"西班牙语","ar":"阿拉伯语"}
        try:
            from agents.multi_model import ModelRouter
            resp = await ModelRouter.smart_chat(messages=[{"role":"user","content":f"将以下内容翻译成{lang_names.get(target_lang,target_lang)},保持格式:\n{text}"}], mode="fast")
            return resp.get("content", "")
        except:
            return f"[翻译失败] {text}"

    @classmethod
    async def batch_generate(cls, products: list, task_type: str = "description") -> list:
        """批量生成"""
        results = []
        for p in products:
            if task_type == "description":
                text = await cls.generate_product_desc(p)
            elif task_type == "marketing":
                text = await cls.generate_marketing_copy(p)
            elif task_type == "social":
                text = await cls.generate_social_post(p)
            else:
                text = ""
            results.append({"input": p, "output": text})
        return results

content_factory = ContentFactory()
