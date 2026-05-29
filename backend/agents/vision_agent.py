"""Vision Agent 鈥?鍥剧墖璇嗗埆/瑙嗛鍒嗘瀽/OCR/UI鍒嗘瀽
瀹屽叏浣跨敤 AI 妯″瀷锛圖eepSeek/302AI锛夋浛浠ｇ涓夋柟 API锛圤CR.space/Imagga锛?
鏃犻渶棰濆娉ㄥ唽锛岀敤浣犲凡鏈夌殑 API Key 鍗冲彲"""
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
    """鍔犺浇鍥剧墖骞惰繑鍥?base64 缂栫爜"""
    import httpx
    c = _get_client()
    if image_url_or_path.startswith("http"):
        r = await c.get(image_url_or_path)
        return base64.b64encode(r.content).decode()
    else:
        with open(image_url_or_path, "rb") as f:
            return base64.b64encode(f.read()).decode()


async def _call_vision_ai(prompt: str, img_b64: str) -> str:
    """鐢?AI 妯″瀷鍒嗘瀽鍥剧墖 鈥?浼樺厛 302AI锛岄檷绾?DeepSeek"""
    from config import OPENAI_API_KEY, OPENAI_BASE_URL, DEEPSEEK_API_KEY

    api_key = OPENAI_API_KEY or DEEPSEEK_API_KEY
    if not api_key:
        return "鏈厤缃?AI API Key锛堣鍦?.env 璁剧疆 OPENAI_API_KEY 鎴?DEEPSEEK_API_KEY锛?

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
            # 濡傛灉涓嶆敮鎸佸浘鐗囷紝闄嶇骇涓虹函鏂囨湰鍒嗘瀽锛堜粎 DeepSeek 鍏煎妯″紡锛?
            text_payload = {
                "model": model,
                "messages": [{"role": "user", "content": f"{prompt}\n[鍥剧墖 base64 宸叉彁渚涗絾妯″瀷涓嶆敮鎸佸浘鐗囧垎鏋怾"}],
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
            return f"AI 鍒嗘瀽澶辫触: {resp.status_code}"
    except Exception as e:
        return f"AI 璋冪敤寮傚父: {str(e)[:100]}"


class VisionAgent:
    """瑙嗚Agent 鈥?鍏ㄩ儴浣跨敤 AI 妯″瀷鍒嗘瀽"""

    @staticmethod
    async def ocr_recognize(image_url: str) -> dict:
        """OCR 鏂囧瓧璇嗗埆 鈥?鐢?AI 鎻愬彇鍥剧墖涓殑鍏ㄩ儴鏂囧瓧"""
        try:
            img_b64 = await _load_image(image_url)
            prompt = """浣犳槸涓撲笟 OCR 寮曟搸銆傝涓ユ牸璇嗗埆杩欏紶鍥剧墖涓殑鎵€鏈夋枃瀛楀唴瀹广€?
瑙勫垯锛?
1. 鍙緭鍑鸿瘑鍒埌鐨勬枃瀛楋紝涓嶈娣诲姞鍒嗘瀽鎴栬瘎璁?
2. 淇濇寔鍘熸枃鎺掔増鍜屾崲琛?
3. 濡傛灉鍥剧墖娓呮櫚浣嗘棤鏂囧瓧锛岃緭鍑?鍥剧墖涓病鏈夊彲璇嗗埆鐨勬枃瀛?
4. 濡傛灉鍥剧墖妯＄硦鏃犳硶璇嗗埆锛岃緭鍑?鍥剧墖璐ㄩ噺涓嶈冻浠ヨ瘑鍒枃瀛?
5. 鐢ㄤ腑鏂囪緭鍑鸿瘑鍒粨鏋?""
            text = await _call_vision_ai(prompt, img_b64)
            return {"ok": True, "text": text.strip(), "source": image_url, "engine": "ai_vision"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    async def analyze_video(video_url: str) -> dict:
        """瑙嗛鍒嗘瀽 鈥?鎻愬彇鍏冧俊鎭?鎴浘鍏抽敭甯?""
        try:
            tmpdir = tempfile.mkdtemp()
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", video_url],
                capture_output=True, text=True, timeout=30)
            info = json.loads(result.stdout) if result.stdout else {}
            duration = float(info.get("format", {}).get("duration", 0))
            return {"ok": True, "duration_sec": duration, "format": info.get("format", {}).get("format_name", ""), "streams": len(info.get("streams", []))}
        except FileNotFoundError:
            return {"ok": True, "note": "ffprobe鏈畨瑁咃紝浠呰繑鍥炲熀鏈俊鎭?, "url": video_url}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            try: shutil.rmtree(tmpdir, ignore_errors=True)
            except: pass

    @staticmethod
    async def detect_objects(image_url: str) -> dict:
        """鐗╀綋妫€娴?鈥?鐢?AI 璇嗗埆鍥剧墖涓殑涓昏鐗╀綋"""
        try:
            img_b64 = await _load_image(image_url)
            prompt = """璇疯瘑鍒繖寮犲浘鐗囦腑鐨勬墍鏈変富瑕佺墿浣撳拰鍦烘櫙鍏冪礌銆?
璇蜂互 JSON 鏁扮粍鏍煎紡杈撳嚭锛屾瘡涓墿浣撳寘鍚?name锛堜腑鏂囧悕锛夊拰 confidence锛?-100鐨勭疆淇″害锛夈€?
鎸夋樉钁楁€ф帓搴忥紝鏈€澶氳繑鍥?0涓€?
绀轰緥锛歔{"name": "鎵嬫満", "confidence": 95}, {"name": "妗屽瓙", "confidence": 80}]
鍙緭鍑?JSON锛屼笉瑕佸叾浠栨枃瀛椼€?""
            raw = await _call_vision_ai(prompt, img_b64)
            # 灏濊瘯瑙ｆ瀽 JSON
            try:
                # 浠庡洖澶嶄腑鎻愬彇 JSON
                import re
                m = _re.search(r'\[.*?\]', raw, _re.DOTALL)
                if m:
                    objects = json.loads(m.group())
                    return {"ok": True, "objects": objects[:10]}
            except Exception:
                pass
            return {"ok": True, "objects": [{"name": "AI鍒嗘瀽缁撴灉", "confidence": 50, "raw": raw[:200]}], "engine": "ai_vision"}
        except Exception as e:
            return {"ok": False, "objects": [], "error": str(e)}

    @staticmethod
    async def analyze_video_frames(video_url, frame_interval=5):
        """瑙嗛甯у垎鏋?鈥?鎻愬彇鍏抽敭甯у苟鐢?AI 鍒嗘瀽"""
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
                        prompt = f"杩欐槸瑙嗛绗瑊i * frame_interval}绉掔殑鍏抽敭甯э紝璇峰垪鍑虹敾闈腑鐨勪富瑕佺墿浣擄紙JSON鏁扮粍鏍煎紡锛?
                        raw = await _call_vision_ai(prompt, img_b64)
                        frames_result.append({"time_sec": i * frame_interval, "analysis": raw[:300]})
                    except Exception:
                        frames_result.append({"time_sec": i * frame_interval, "objects": []})
            return {"ok": True, "duration_sec": duration, "frames": frame_count,
                    "frame_analysis": frames_result,
                    "summary": f"{int(duration)}绉掕棰? {frame_count}甯у垎鏋愬畬鎴?}
        except FileNotFoundError:
            return {"ok": False, "error": "ffmpeg not installed"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    @staticmethod
    async def detect_faces(image_url: str) -> dict:
        """浜鸿劯妫€娴?鈥?鐢?AI 妫€娴嬪浘鐗囦腑鐨勪汉鑴告暟閲?""
        try:
            img_b64 = await _load_image(image_url)
            prompt = """璇峰垎鏋愯繖寮犲浘鐗囷細
1. 鍥剧墖涓湁鍑犲紶浜鸿劯锛?
2. 姣忓紶浜鸿劯鐨勫ぇ鑷翠綅缃紙宸?涓?鍙炽€佷笂/涓?涓嬶級
3. 姣忎釜浜虹殑澶ц嚧琛ㄦ儏锛堝井绗?涓ヨ們/鍏朵粬锛?

浠?JSON 鏍煎紡杈撳嚭锛歿"face_count": N, "details": "鍏蜂綋鎻忚堪"}
鍙緭鍑?JSON锛屼笉瑕佸叾浠栨枃瀛椼€?""
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
        """鍒嗘瀽鍥剧墖鍐呭 鈥?鐢?AI 妯″瀷缁煎悎鍒嗘瀽"""
        try:
            url = image_url or image_path
            img_b64 = await _load_image(url)
            prompt = """璇︾粏鍒嗘瀽杩欏紶鍥剧墖锛屾寜浠ヤ笅鏍煎紡杈撳嚭锛?
1锛夊浘鐗囦富浣擄細鎻忚堪鏍稿績鍐呭
2锛変富瑕佺墿浣擄細鍒楀嚭鍙鐗╀綋
3锛夎瘑鍒埌鐨勬枃瀛楋細鎻愬彇鎵€鏈夊彲瑙佹枃瀛?
4锛夐鑹茶壊璋冿細涓昏壊璋冨拰閰嶈壊
5锛夊浘鐗囪川閲忥細娓呮櫚搴︺€佹瀯鍥捐瘎浠?
6锛夐€傚悎鍒嗙被锛氶€傚悎鍦ㄥ摢涓晢鍝佺被鐩笅鍞崠
7锛変紭鍖栧缓璁細濡備綍鏀硅繘杩欏紶鍥剧墖

鐢ㄤ腑鏂囧洖绛旓紝绠€娲佷笓涓氥€?""
            analysis = await _call_vision_ai(prompt, img_b64)
            return {"ok": True, "analysis": analysis, "analyzed_at": datetime.now().isoformat(), "source": url}
        except Exception as e:
            return {"ok": False, "analysis": f"鍒嗘瀽澶辫触: {str(e)[:200]}", "source": image_url or image_path}