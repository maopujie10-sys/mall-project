''"AI  ///''"
from typing import Dict, List
from tools.logger import get_logger

logger = get_logger("content")

class ContentFactory:
    ''"AI''"

    @classmethod
    async def generate_product_desc(cls, product: dict, style: str = "professional", lang: str = "zh") -> str:
        ''''''
        try:
            from agents.multi_model import ModelRouter
            prompt = f''"{style}{'' if lang=='zh' else 'English'}(150-300):
: {product.get('name','')}
: {product.get('price','')}
: {product.get('category','')}
: {product.get('features','')}
: ,SEO,{'-' if lang!='zh' else ''}''"
            resp = await ModelRouter.smart_chat_async(messages=[{"role":"user","content":prompt}], mode="creative")
            return resp.get("content",'') if isinstance(resp,dict) else str(resp)
        except:
            return f"{'' if lang=='zh' else '[Hot Sale] '}{product.get('name','')} - {'' if lang=='zh' else 'Premium quality, limited offer!'}"

    @classmethod
    async def generate_campaign(cls, campaign: dict) -> str:
        ''''''
        try:
            from agents.multi_model import ModelRouter
            name = campaign.get("name",'')
            discount = campaign.get("discount",'')
            prompt = f"(100-200): :{name}, :{discount}, :"
            resp = await ModelRouter.smart_chat_async(messages=[{"role":"user","content":prompt}], mode="creative")
            return resp.get("content",'') if isinstance(resp,dict) else str(resp)
        except:
            return f" {campaign.get('name','')}!{campaign.get('discount','')},!"

    @classmethod
    async def generate_social_post(cls, topic: dict) -> str:
        ''''''
        try:
            from agents.multi_model import ModelRouter
            prompt = f"(100-200),3-5hashtag:\n:{topic.get('theme','')}\n:{topic.get('style','')}\n: {topic.get('include','')}"
            resp = await ModelRouter.smart_chat_async(messages=[{"role":"user","content":prompt}], mode="creative")
            return resp.get("content",'') if isinstance(resp,dict) else str(resp)
        except:
            return f" {topic.get('theme','')} \n# #"

    @classmethod
    async def generate_email(cls, data: dict) -> str:
        ''''''
        try:
            from agents.multi_model import ModelRouter
            prompt = f": :{data.get('subject','')}, :{data.get('audience','')}, :{data.get('cta','')}"
            resp = await ModelRouter.smart_chat_async(messages=[{"role":"user","content":prompt}], mode="creative")
            return resp.get("content",'') if isinstance(resp,dict) else str(resp)
        except:
            return f"Subject: {data.get('subject','')}\n\nCheck out our latest offer!"

    @classmethod
    async def batch_generate(cls, products: List[dict], style: str = "professional") -> List[Dict]:
        ''''''
        results = []
        for p in products[:20]:
            desc = await cls.generate_product_desc(p, style)
            results.append({"name": p.get("name",''), "description": desc})
        return results

content_factory = ContentFactory()