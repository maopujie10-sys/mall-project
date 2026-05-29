"""Vision Agent — 图片识别/视频分析/OCR/UI分析
完全使用 AI 模型（DeepSeek/302AI）替代第三方 API（OCR.space/Imagga）
无需额外注册，用你已有的 API Key 即可"""
import base64
import os
import json
import asyncio
import subprocess
import tempfile
import shutil
from datetime import datetime

_vision_semaphore = asyncio.Semaphore(3)
_VISION_CLIENT = None

def _get_client():
    global _VISION_CLIENT
    if _VISION_CLIENT is None:
        import httpx
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        _VISION_CLIENT = httpx.AsyncClient(timeout=60, limits=limits)
    return _VISION_CLIENT


async def _load_image(image_url_or_path: str) -> str:
    """加载图片并返回 base64 编码"""
    import httpx
    c = _get_client()
    if image_url_or_path.startswith("http"):
        r = await c.get(image_url_or_path)
        return base64.b64encode(r.content).decode()
    else:
        with open(image_url_or_path, "rb") as f:
            return base64.b64encode(f.read()).decode()


async def _call_vision_ai(prompt: str, img_b64: str) -> str:
    """用 AI 模型分析图片 — 优先 302AI，降级 DeepSeek"""
    from config import OPENAI_API_KEY, OPENAI_BASE_URL, DEEPSEEK_API_KEY

    api_key = OPENAI_API_KEY or DEEPSEEK_API_KEY
    if not api_key:
        return "未配置 AI API Key（请在 .env 设置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY）"

    base_url = OPENAI_BASE_URL if OPENAI_API_KEY else "https://api.deepseek.com/v1"
    model = "gpt-4o-mini" if OPENAI_API_KEY else "deepseek-chat"

    try:
        import httpx
        c = _get_client()
        payload = {
            "model": model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            }],
            "max_tokens": 800
        }
        resp = await c.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            # 如果不支持图片，降级为纯文本分析（仅 DeepSeek 兼容模式）
            text_payload = {
                "model": model,
                "messages": [{"role": "user", "content": f"{prompt}\n[图片 base64 已提供但模型不支持图片分析]"}],
                "max_tokens": 500
            }
            resp2 = await c.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=text_payload,
                timeout=30
            )
            if resp2.status_code == 200:
                return resp2.json()["choices"][0]["message"]["content"]
            return f"AI 分析失败: {resp.status_code}"
    except Exception as e:
        return f"AI 调用异常: {str(e)[:100]}"


class VisionAgent:
    """视觉Agent — 全部使用 AI 模型分析"""

    @staticmethod
    async def ocr_recognize(image_url: str) -> dict:
        """OCR 文字识别 — 用 AI 提取图片中的全部文字"""
        try:
            img_b64 = await _load_image(image_url)
            prompt = """你是专业 OCR 引擎。请严格识别这张图片中的所有文字内容。
规则：
1. 只输出识别到的文字，不要添加分析或评论
2. 保持原文排版和换行
3. 如果图片清晰但无文字，输出"图片中没有可识别的文字"
4. 如果图片模糊无法识别，输出"图片质量不足以识别文字"
5. 用中文输出识别结果"""
            text = await _call_vision_ai(prompt, img_b64)
            return {"ok": True, "text": text.strip(), "source": image_url, "engine": "ai_vision"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def analyze_video(video_url: str) -> dict:
        """视频分析 — 提取元信息/截图关键帧"""
        try:
            tmpdir = tempfile.mkdtemp()
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", video_url],
                capture_output=True, text=True, timeout=30)
            info = json.loads(result.stdout) if result.stdout else {}
            duration = float(info.get("format", {}).get("duration", 0))
            return {"ok": True, "duration_sec": duration, "format": info.get("format", {}).get("format_name", ""), "streams": len(info.get("streams", []))}
        except FileNotFoundError:
            return {"ok": True, "note": "ffprobe未安装，仅返回基本信息", "url": video_url}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            try: shutil.rmtree(tmpdir, ignore_errors=True)
            except: pass

    @staticmethod
    async def detect_objects(image_url: str) -> dict:
        """物体检测 — 用 AI 识别图片中的主要物体"""
        try:
            img_b64 = await _load_image(image_url)
            prompt = """请识别这张图片中的所有主要物体和场景元素。
请以 JSON 数组格式输出，每个物体包含 name（中文名）和 confidence（0-100的置信度）。
按显著性排序，最多返回10个。
示例：[{"name": "手机", "confidence": 95}, {"name": "桌子", "confidence": 80}]
只输出 JSON，不要其他文字。"""
            raw = await _call_vision_ai(prompt, img_b64)
            # 尝试解析 JSON
            try:
                # 从回复中提取 JSON
                import re
                m = _re.search(r'\[.*?\]', raw, _re.DOTALL)
                if m:
                    objects = json.loads(m.group())
                    return {"ok": True, "objects": objects[:10]}
            except Exception:
                pass
            return {"ok": True, "objects": [{"name": "AI分析结果", "confidence": 50, "raw": raw[:200]}], "engine": "ai_vision"}
        except Exception as e:
            return {"ok": False, "objects": [], "error": str(e)}

    @staticmethod
    async def analyze_video_frames(video_url, frame_interval=5):
        """视频帧分析 — 提取关键帧并用 AI 分析"""
        tmpdir = tempfile.mkdtemp()
        frames_dir = os.path.join(tmpdir, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        try:
            probe = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_url],
                                   capture_output=True, text=True, timeout=30)
            info = json.loads(probe.stdout) if probe.stdout else {}
            duration = float(info.get("format", {}).get("duration", 0))
            frame_count = max(1, int(duration / frame_interval))
            for i in range(frame_count):
                t = i * frame_interval
                out = os.path.join(frames_dir, "frame_%03d.jpg" % i)
                subprocess.run(["ffmpeg", "-ss", str(t), "-i", video_url, "-vframes", "1", "-q:v", "2", out, "-y"],
                               capture_output=True, timeout=30)
            frames_result = []
            for i in range(frame_count):
                fp = os.path.join(frames_dir, "frame_%03d.jpg" % i)
                if os.path.exists(fp):
                    with open(fp, "rb") as f:
                        img_b64 = base64.b64encode(f.read()).decode()
                    try:
                        prompt = f"这是视频第{i * frame_interval}秒的关键帧，请列出画面中的主要物体（JSON数组格式）"
                        raw = await _call_vision_ai(prompt, img_b64)
                        frames_result.append({"time_sec": i * frame_interval, "analysis": raw[:300]})
                    except Exception:
                        frames_result.append({"time_sec": i * frame_interval, "objects": []})
            return {"ok": True, "duration_sec": duration, "frames": frame_count,
                    "frame_analysis": frames_result,
                    "summary": f"{int(duration)}秒视频, {frame_count}帧分析完成"}
        except FileNotFoundError:
            return {"ok": False, "error": "ffmpeg not installed"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    @staticmethod
    async def detect_faces(image_url: str) -> dict:
        """人脸检测 — 用 AI 检测图片中的人脸数量"""
        try:
            img_b64 = await _load_image(image_url)
            prompt = """请分析这张图片：
1. 图片中有几张人脸？
2. 每张人脸的大致位置（左/中/右、上/中/下）
3. 每个人的大致表情（微笑/严肃/其他）

以 JSON 格式输出：{"face_count": N, "details": "具体描述"}
只输出 JSON，不要其他文字。"""
            raw = await _call_vision_ai(prompt, img_b64)
            import re
            m = _re.search(r'\{.*\}', raw, _re.DOTALL)
            if m:
                try:
                    data = json.loads(m.group())
                    return {"ok": True, "face_count": data.get("face_count", 0), "details": data.get("details", raw[:200])}
                except Exception:
                    pass
            return {"ok": True, "face_count": 0, "details": raw[:200], "engine": "ai_vision"}
        except Exception as e:
            return {"ok": True, "face_count": 0, "error": str(e)}

    @staticmethod
    async def analyze_image(image_path: str = None, image_url: str = None) -> dict:
        """分析图片内容 — 用 AI 模型综合分析"""
        try:
            url = image_url or image_path
            img_b64 = await _load_image(url)
            prompt = """详细分析这张图片，按以下格式输出：
1）图片主体：描述核心内容
2）主要物体：列出可见物体
3）识别到的文字：提取所有可见文字
4）颜色色调：主色调和配色
5）图片质量：清晰度、构图评价
6）适合分类：适合在哪个商品类目下售卖
7）优化建议：如何改进这张图片

用中文回答，简洁专业。"""
            analysis = await _call_vision_ai(prompt, img_b64)
            return {"ok": True, "analysis": analysis, "analyzed_at": datetime.now().isoformat(), "source": url}
        except Exception as e:
            return {"ok": False, "analysis": f"分析失败: {str(e)[:200]}", "source": image_url or image_path}