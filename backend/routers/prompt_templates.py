''"Prompt API''"
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from tools.logger import get_logger
from auth import verify_token

router = APIRouter(prefix="/agent/prompts", tags=["Prompts"])
logger = get_logger("prompts")

TEMPLATES = [
    {"id":"seo-desc","name":"SEO","category":'',"prompt":"{name}SEO5200-300","icon":""},
    {"id":"social-post","name":'',"category":'',"prompt":"{name}TikTok3hashtag","icon":""},
    {"id":"customer-reply","name":'',"category":'',"prompt":"{question}{name}","icon":""},
    {"id":"code-review","name":'',"category":'',"prompt":"\n{code}","icon":""},
    {"id":"data-analysis","name":'',"category":'',"prompt":"\n{data}","icon":""},
    {"id":"email-marketing","name":'',"category":'',"prompt":"{subject}{audience}","icon":""},
    {"id":"bug-fix","name":"Bug","category":'',"prompt":"bug{code}{error}","icon":""},
    {"id":"competitor-analysis","name":'',"category":'',"prompt":"{competitor}{our_product}","icon":""},
    {"id":"translate-product","name":'',"category":'',"prompt":"{language}\n{product_info}","icon":""},
    {"id":"ad-copy","name":'',"category":'',"prompt":"{name}Google/Facebook150","icon":""},
    {"id":"summarize","name":'',"category":'',"prompt":"\n{content}","icon":""},
    {"id":"brainstorm","name":'',"category":'',"prompt":"{topic}10","icon":""},
]

@router.get("/templates")
async def list_templates(category: str = '', _=Depends(verify_token)):
    tmpls = TEMPLATES
    if category: tmpls = [t for t in tmpls if t["category"] == category]
    return {"ok":True,"templates":tmpls,"categories":list(set(t["category"] for t in TEMPLATES))}

@router.post("/apply")
async def apply_template(template_id: str = '', params: dict = {}, _=Depends(verify_token)):
    tmpl = next((t for t in TEMPLATES if t["id"] == template_id), None)
    if not tmpl: return {"ok":False,"error":''}
    prompt = tmpl["prompt"]
    for k,v in params.items(): prompt = prompt.replace("{"+k+"}", str(v))
    try:
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="smart")
        return {"ok":True,"result":resp.get("content",'') if isinstance(resp,dict) else str(resp),"template":tmpl["name"]}
    except Exception as e:
        return {"ok":False,"error":str(e),"prompt":prompt}