"""AI 内容工厂 -- 作图/视频/文案生成工具封装"""
import httpx
import json
from datetime import datetime
from typing import Optional
from state import state

# ===== 配置(从config导入)=====
from config import (
    CLAUDE_API_KEY,
    CLAUDE_MODEL,
    IMAGE_API_KEY,
    IMAGE_API_URL,
    VIDEO_API_KEY,
    VIDEO_API_URL,
)


# ===== 文案生成 =====
COPYWRITER_PROMPTS = {
    "title": "你是一个电商文案专家.请为以下商品生成一个吸引人的中文标题(20字以内),突出卖点:\n{product_info}",
    "description": "你是一个电商文案专家.请为以下商品生成一段详细的中文商品描述(200-300字),包含卖点、规格、适用场景:\n{product_info}",
    "seo": "你是一个SEO专家.请为以下商品生成SEO关键词和描述(100字以内):\n{product_info}",
    "ad": "你是一个营销文案专家.请为以下商品生成一条朋友圈/社交媒体推广文案(80字以内):\n{product_info}",
}

async def generate_copy(product_info: str, style: str = "title") -> dict:
    """调用 Claude 生成文案"""
    prompt = COPYWRITER_PROMPTS.get(style, COPYWRITER_PROMPTS["title"])
    prompt = prompt.replace("{product_info}", product_info)

    if not CLAUDE_API_KEY:
        return {"ok": False, "error": "CLAUDE_API_KEY 未配置,请在 .env 中设置", "style": style}

    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": CLAUDE_MODEL or "claude-3-5-sonnet-latest",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            if r.status_code == 200:
                content = r.json()["content"][0]["text"]
                return {"ok": True, "style": style, "content": content.strip()}
            return {"ok": False, "error": f"API返回 {r.status_code}: {r.text[:200]}", "style": style}
    except Exception as e:
        return {"ok": False, "error": str(e), "style": style}


# ===== 图片生成 =====
async def generate_image(prompt: str, size: str = "1024x1024", style: str = " realistic") -> dict:
    """调用作图 API 生成商品图"""
    if not IMAGE_API_KEY:
        return {"ok": False, "error": "IMAGE_API_KEY 未配置,请在 .env 中设置"}

    try:
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(
                IMAGE_API_URL or "https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {IMAGE_API_KEY}"},
                json={
                    "model": "dall-e-3",
                    "prompt": f"{prompt}, {style}, e-commerce product photo, white background, high quality",
                    "n": 1,
                    "size": size,
                },
            )
            if r.status_code == 200:
                data = r.json()
                url = data["data"][0]["url"]
                return {"ok": True, "url": url, "prompt": prompt, "size": size}
            return {"ok": False, "error": f"API返回 {r.status_code}", "prompt": prompt}
    except Exception as e:
        return {"ok": False, "error": str(e), "prompt": prompt}


# ===== 视频生成 =====
async def generate_video(product_name: str, script: str = "", duration: int = 15) -> dict:
    """调用视频 API 生成商品展示视频"""
    if not VIDEO_API_KEY:
        return {"ok": False, "error": "VIDEO_API_KEY 未配置,请在 .env 中设置"}

    try:
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(
                VIDEO_API_URL or "https://api.runwayml.com/v1/generations",
                headers={"Authorization": f"Bearer {VIDEO_API_KEY}"},
                json={
                    "prompt": f"Product showcase: {product_name}. {script}",
                    "duration": duration,
                },
            )
            if r.status_code == 200:
                data = r.json()
                return {"ok": True, "video_url": data.get("url", ""), "product": product_name}
            return {"ok": False, "error": f"API返回 {r.status_code}: {r.text[:200]}", "product": product_name}
    except Exception as e:
        return {"ok": False, "error": str(e), "product": product_name}


# ===== 历史记录 =====
def get_history(category: str = "all") -> list:
    """获取 AI 内容生成历史"""
    key = f"ai_factory_{category}"
    return state._data.get(key, [])

def save_record(category: str, record: dict):
    """保存生成记录"""
    key = f"ai_factory_{category}"
    records = state._data.setdefault(key, [])
    records.insert(0, record)
    if len(records) > 100:
        records[:] = records[:100]
    state._save()
