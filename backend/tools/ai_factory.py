锘?""AI 鍐呭宸ュ巶 鈥?浣滃浘/瑙嗛/鏂囨鐢熸垚宸ュ叿灏佽"""
import httpx
import json
from datetime import datetime
from typing import Optional
from state import state

# ===== 閰嶇疆锛堜粠config瀵煎叆锛?====
from config import (
    CLAUDE_API_KEY,
    CLAUDE_MODEL,
    IMAGE_API_KEY,
    IMAGE_API_URL,
    VIDEO_API_KEY,
    VIDEO_API_URL,
)


# ===== 鏂囨鐢熸垚 =====
COPYWRITER_PROMPTS = {
    "title": "浣犳槸涓€涓數鍟嗘枃妗堜笓瀹躲€傝涓轰互涓嬪晢鍝佺敓鎴愪竴涓惛寮曚汉鐨勪腑鏂囨爣棰橈紙20瀛椾互鍐咃級锛岀獊鍑哄崠鐐癸細\n{product_info}",
    "description": "浣犳槸涓€涓數鍟嗘枃妗堜笓瀹躲€傝涓轰互涓嬪晢鍝佺敓鎴愪竴娈佃缁嗙殑涓枃鍟嗗搧鎻忚堪锛?00-300瀛楋級锛屽寘鍚崠鐐广€佽鏍笺€侀€傜敤鍦烘櫙锛歕n{product_info}",
    "seo": "浣犳槸涓€涓猄EO涓撳銆傝涓轰互涓嬪晢鍝佺敓鎴怱EO鍏抽敭璇嶅拰鎻忚堪锛?00瀛椾互鍐咃級锛歕n{product_info}",
    "ad": "浣犳槸涓€涓惀閿€鏂囨涓撳銆傝涓轰互涓嬪晢鍝佺敓鎴愪竴鏉℃湅鍙嬪湀/绀句氦濯掍綋鎺ㄥ箍鏂囨锛?0瀛椾互鍐咃級锛歕n{product_info}",
}

async def generate_copy(product_info: str, style: str = "title") -> dict:
    """璋冪敤 Claude 鐢熸垚鏂囨"""
    prompt = COPYWRITER_PROMPTS.get(style, COPYWRITER_PROMPTS["title"])
    prompt = prompt.replace("{product_info}", product_info)

    if not CLAUDE_API_KEY:
        return {"ok": False, "error": "CLAUDE_API_KEY 鏈厤缃紝璇峰湪 .env 涓缃?, "style": style}

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
            return {"ok": False, "error": f"API杩斿洖 {r.status_code}: {r.text[:200]}", "style": style}
    except Exception as e:
        return {"ok": False, "error": str(e), "style": style}


# ===== 鍥剧墖鐢熸垚 =====
async def generate_image(prompt: str, size: str = "1024x1024", style: str = " realistic") -> dict:
    """璋冪敤浣滃浘 API 鐢熸垚鍟嗗搧鍥?""
    if not IMAGE_API_KEY:
        return {"ok": False, "error": "IMAGE_API_KEY 鏈厤缃紝璇峰湪 .env 涓缃?}

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
            return {"ok": False, "error": f"API杩斿洖 {r.status_code}", "prompt": prompt}
    except Exception as e:
        return {"ok": False, "error": str(e), "prompt": prompt}


# ===== 瑙嗛鐢熸垚 =====
async def generate_video(product_name: str, script: str = "", duration: int = 15) -> dict:
    """璋冪敤瑙嗛 API 鐢熸垚鍟嗗搧灞曠ず瑙嗛"""
    if not VIDEO_API_KEY:
        return {"ok": False, "error": "VIDEO_API_KEY 鏈厤缃紝璇峰湪 .env 涓缃?}

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
            return {"ok": False, "error": f"API杩斿洖 {r.status_code}: {r.text[:200]}", "product": product_name}
    except Exception as e:
        return {"ok": False, "error": str(e), "product": product_name}


# ===== 鍘嗗彶璁板綍 =====
def get_history(category: str = "all") -> list:
    """鑾峰彇 AI 鍐呭鐢熸垚鍘嗗彶"""
    key = f"ai_factory_{category}"
    return state._data.get(key, [])

def save_record(category: str, record: dict):
    """淇濆瓨鐢熸垚璁板綍"""
    key = f"ai_factory_{category}"
    records = state._data.setdefault(key, [])
    records.insert(0, record)
    if len(records) > 100:
        records[:] = records[:100]
    state._save()
