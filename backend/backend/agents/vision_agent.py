''"Vision Agent -- //OCR/UI
 AI (DeepSeek/302AI) API(OCR.space/Imagga)
, API Key ''"
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
    ''" base64 ''"
    import httpx
    c = _get_client()
    if image_url_or_path.startswith("http"):
        r = await c.get(image_url_or_path)
        return base64.b64encode(r.content).decode()
    else:
        with open(image_url_or_path, "rb") as f:
            return base64.b64encode(f.read()).decode()


async def _call_vision_ai(prompt: str, img_b64: str) -> str:
    ''" AI  --  302AI, DeepSeek''"
    from config import OPENAI_API_KEY, OPENAI_BASE_URL, DEEPSEEK_API_KEY

    api_key = OPENAI_API_KEY or DEEPSEEK_API_KEY
    if not api_key:
        return " AI API Key( .env  OPENAI_API_KEY  DEEPSEEK_API_KEY)"

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
            # ,( DeepSeek )
            text_payload = {
                "model": model,
                "messages": [{"role": "user", "content": f"{prompt}\n[ base64 ]"}],
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
            return f"AI : {resp.status_code}"
    except Exception as e:
        return f"AI : {str(e)[:100]}"


class VisionAgent:
    ''"Agent --  AI ''"

    @staticmethod
    async def ocr_recognize(image_url: str) -> dict:
        ''"OCR  --  AI ''"
        try:
            img_b64 = await _load_image(image_url)
            prompt = ''" OCR ..
:
1. ,
2. 
3. ,''
4. ,''
5. ''"
            text = await _call_vision_ai(prompt, img_b64)
            return {"ok": True, "text": text.strip(), "source": image_url, "engine": "ai_vision"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def analyze_video(video_url: str) -> dict:
        ''" -- /''"
        try:
            tmpdir = tempfile.mkdtemp()
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", video_url],
                capture_output=True, text=True, timeout=30)
            info = json.loads(result.stdout) if result.stdout else {}
            duration = float(info.get("format", {}).get("duration", 0))
            return {"ok": True, "duration_sec": duration, "format": info.get("format", {}).get("format_name", ''), "streams": len(info.get("streams", []))}
        except FileNotFoundError:
            return {"ok": True, "note": "ffprobe,", "url": video_url}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            try: shutil.rmtree(tmpdir, ignore_errors=True)
            except: pass

    @staticmethod
    async def detect_objects(image_url: str) -> dict:
        ''" --  AI ''"
        try:
            img_b64 = await _load_image(image_url)
            prompt = ''".
 JSON , name() confidence(0-100).
,10.
:[{"name": '', "confidence": 95}, {"name": '', "confidence": 80}]
 JSON,.''"
            raw = await _call_vision_ai(prompt, img_b64)
            #  JSON
            try:
                #  JSON
                import re
                m = _re.search(r'\[.*?\]', raw, _re.DOTALL)
                if m:
                    objects = json.loads(m.group())
                    return {"ok": True, "objects": objects[:10]}
            except Exception:
                pass
            return {"ok": True, "objects": [{"name": "AI", "confidence": 50, "raw": raw[:200]}], "engine": "ai_vision"}
        except Exception as e:
            return {"ok": False, "objects": [], "error": str(e)}

    @staticmethod
    async def analyze_video_frames(video_url, frame_interval=5):
        ''" --  AI ''"
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
                        prompt = f"{i * frame_interval},(JSON)"
                        raw = await _call_vision_ai(prompt, img_b64)
                        frames_result.append({"time_sec": i * frame_interval, "analysis": raw[:300]})
                    except Exception:
                        frames_result.append({"time_sec": i * frame_interval, "objects": []})
            return {"ok": True, "duration_sec": duration, "frames": frame_count,
                    "frame_analysis": frames_result,
                    "summary": f"{int(duration)}, {frame_count}"}
        except FileNotFoundError:
            return {"ok": False, "error": "ffmpeg not installed"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    @staticmethod
    async def detect_faces(image_url: str) -> dict:
        ''" --  AI ''"
        try:
            img_b64 = await _load_image(image_url)
            prompt = ''":
1. ?
2. (////)
3. (//)

 JSON :{"face_count": N, "details": ''}
 JSON,.''"
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
        ''" --  AI ''"
        try:
            url = image_url or image_path
            img_b64 = await _load_image(url)
            prompt = ''",:
1):
2):
3):
4):
5):
6):
7):

,.''"
            analysis = await _call_vision_ai(prompt, img_b64)
            return {"ok": True, "analysis": analysis, "analyzed_at": datetime.now().isoformat(), "source": url}
        except Exception as e:
            return {"ok": False, "analysis": f": {str(e)[:200]}", "source": image_url or image_path}