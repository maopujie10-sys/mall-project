"""Prompt模板库 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from tools.logger import get_logger
from auth import verify_token

router = APIRouter(prefix="/agent/prompts", tags=["Prompts"])
logger = get_logger("prompts")

TEMPLATES = [
    {"id":"seo-desc","name":"SEO商品描述","category":"电商","prompt":"为商品「{name}」写SEO优化的描述，含5个关键词，200-300字。","icon":"🛍️"},
    {"id":"social-post","name":"社媒推广帖","category":"营销","prompt":"为「{name}」写TikTok推广文案，带3个热门hashtag，轻松活泼风格。","icon":"📱"},
    {"id":"customer-reply","name":"客服回复模板","category":"客服","prompt":"以专业友好的语气回复客户：「{question}」，针对产品「{name}」。","icon":"💬"},
    {"id":"code-review","name":"代码审查","category":"开发","prompt":"审查以下代码，指出问题和改进建议：\n{code}","icon":"💻"},
    {"id":"data-analysis","name":"数据分析报告","category":"分析","prompt":"分析以下数据并生成报告：\n{data}","icon":"📊"},
    {"id":"email-marketing","name":"营销邮件","category":"营销","prompt":"写一封营销邮件，主题「{subject}」，目标受众「{audience}」。","icon":"📧"},
    {"id":"bug-fix","name":"Bug修复","category":"开发","prompt":"以下代码有bug：「{code}」，错误信息：「{error}」，请修复。","icon":"🐛"},
    {"id":"competitor-analysis","name":"竞品分析","category":"分析","prompt":"分析竞品「{competitor}」的优劣势，与我们的产品「{our_product}」对比。","icon":"🔍"},
    {"id":"translate-product","name":"商品多语言翻译","category":"电商","prompt":"将商品信息翻译成{language}：\n{product_info}","icon":"🌍"},
    {"id":"ad-copy","name":"广告文案","category":"营销","prompt":"为「{name}」写Google/Facebook广告文案，含行动号召，150字内。","icon":"📢"},
    {"id":"summarize","name":"文档总结","category":"通用","prompt":"总结以下内容，提取关键要点：\n{content}","icon":"📝"},
    {"id":"brainstorm","name":"头脑风暴","category":"通用","prompt":"针对「{topic}」进行头脑风暴，生成10个创意想法。","icon":"💡"},
]

@router.get("/templates")
async def list_templates(category: str = "", _=Depends(verify_token)):
    tmpls = TEMPLATES
    if category: tmpls = [t for t in tmpls if t["category"] == category]
    return {"ok":True,"templates":tmpls,"categories":list(set(t["category"] for t in TEMPLATES))}

@router.post("/apply")
async def apply_template(template_id: str = "", params: dict = {}, _=Depends(verify_token)):
    tmpl = next((t for t in TEMPLATES if t["id"] == template_id), None)
    if not tmpl: return {"ok":False,"error":"模板不存在"}
    prompt = tmpl["prompt"]
    for k,v in params.items(): prompt = prompt.replace("{"+k+"}", str(v))
    try:
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="smart")
        return {"ok":True,"result":resp.get("content","") if isinstance(resp,dict) else str(resp),"template":tmpl["name"]}
    except Exception as e:
        return {"ok":False,"error":str(e),"prompt":prompt}