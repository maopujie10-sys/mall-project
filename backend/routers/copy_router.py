"""AI商品文案生成 — 标题/描述/SEO/多语言"""
from fastapi import APIRouter, Depends, Query
from auth import verify_token
from risk import handle_risk

router = APIRouter(prefix="/agent/copy", tags=["AICopy"])

@router.post("/generate")
async def generate_copy(product_name: str = Query(...), category: str = "", features: str = "",
                         language: str = "zh", tone: str = "professional", _=Depends(verify_token)):
    """AI生成商品文案"""
    await handle_risk("L1", f"生成文案: {product_name}")
    # 使用内置模板生成（不依赖API Key）
    tones = {"professional": "专业", "friendly": "亲切", "luxury": "高端", "youth": "年轻"}
    tone_label = tones.get(tone, "专业")
    features_list = [f.strip() for f in features.split(",") if f.strip()]
    # 标题
    title = f"{product_name}"
    if category: title = f"{category} | {product_name}"
    # 描述
    desc_parts = [f"【{tone_label}品质】{product_name}"]
    if features_list: desc_parts.append(f"核心特点: {'、'.join(features_list[:5])}")
    desc_parts.append("品质保证，值得信赖。")
    # SEO关键词
    seo_keywords = [product_name, category] if category else [product_name]
    seo_keywords += features_list[:3]
    return {"ok": True, "product": product_name,
            "title": title, "description": "\n".join(desc_parts),
            "seo_keywords": ", ".join(seo_keywords),
            "language": language, "tone": tone}
