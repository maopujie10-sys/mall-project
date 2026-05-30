"""AI内容工厂 — 营销文案/社媒帖子/商品描述/多语言"""
from typing import Dict, List
from tools.logger import get_logger

logger = get_logger("content")

class ContentFactory:
    """AI内容生成工厂"""

    @classmethod
    async def generate_product_desc(cls, product: dict, style: str = "professional", lang: str = "zh") -> str:
        """生成商品描述"""
        try:
            from agents.multi_model import ModelRouter
            prompt = f"""为以下商品生成{style}风格的{'中文' if lang=='zh' else 'English'}描述(150-300字):
商品名: {product.get('name','')}
价格: {product.get('price','')}
品类: {product.get('category','')}
特点: {product.get('features','')}
要求: 突出卖点,含SEO关键词,{'-' if lang!='zh' else ''}"""
            resp = await ModelRouter.smart_chat_async(messages=[{"role":"user","content":prompt}], mode="creative")
            return resp.get("content","") if isinstance(resp,dict) else str(resp)
        except:
            return f"{'【热卖推荐】' if lang=='zh' else '[Hot Sale] '}{product.get('name','')} - {'品质保证，限时优惠！' if lang=='zh' else 'Premium quality, limited offer!'}"

    @classmethod
    async def generate_campaign(cls, campaign: dict) -> str:
        """生成营销活动文案"""
        try:
            from agents.multi_model import ModelRouter
            name = campaign.get("name","")
            discount = campaign.get("discount","")
            prompt = f"为营销活动写一条吸引人的宣传文案(100-200字): 活动:{name}, 优惠:{discount}, 目标:提高转化率"
            resp = await ModelRouter.smart_chat_async(messages=[{"role":"user","content":prompt}], mode="creative")
            return resp.get("content","") if isinstance(resp,dict) else str(resp)
        except:
            return f"🎉 {campaign.get('name','')}来啦!{campaign.get('discount','')},限时优惠!"

    @classmethod
    async def generate_social_post(cls, topic: dict) -> str:
        """生成社交媒体帖子"""
        try:
            from agents.multi_model import ModelRouter
            prompt = f"写一条社交媒体帖子(100-200字),带3-5个相关hashtag:\n主题:{topic.get('theme','')}\n风格:{topic.get('style','轻松活泼')}\n包含: {topic.get('include','')}"
            resp = await ModelRouter.smart_chat_async(messages=[{"role":"user","content":prompt}], mode="creative")
            return resp.get("content","") if isinstance(resp,dict) else str(resp)
        except:
            return f"🔥 {topic.get('theme','')} \n#热门 #推荐"

    @classmethod
    async def generate_email(cls, data: dict) -> str:
        """生成营销邮件"""
        try:
            from agents.multi_model import ModelRouter
            prompt = f"写一封营销邮件: 主题:{data.get('subject','')}, 受众:{data.get('audience','')}, 行动号召:{data.get('cta','')}"
            resp = await ModelRouter.smart_chat_async(messages=[{"role":"user","content":prompt}], mode="creative")
            return resp.get("content","") if isinstance(resp,dict) else str(resp)
        except:
            return f"Subject: {data.get('subject','')}\n\nCheck out our latest offer!"

    @classmethod
    async def batch_generate(cls, products: List[dict], style: str = "professional") -> List[Dict]:
        """批量生成"""
        results = []
        for p in products[:20]:
            desc = await cls.generate_product_desc(p, style)
            results.append({"name": p.get("name",""), "description": desc})
        return results

content_factory = ContentFactory()