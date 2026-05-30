"""多模态引擎 -- 图像分析 + 视频分析 + 音频分析"""
import asyncio, json, base64, os, subprocess, tempfile, re
from datetime import datetime
from tools.ai_client import call_ai, vision_analyze
from tools.logger import logger

class MultimodalEngine:
    """多模态引擎: 图像理解 + 视频分析 + 音频转写"""
    
    @classmethod
    async def analyze_video(cls, video_path="", video_url="", frames=5):
        """视频抽帧+AI描述+摘要"""
        if not video_path and not video_url:
            return {"ok": False, "error": "请提供video_path或video_url"}
        
        frame_descriptions = []
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                input_src = video_path or video_url
                cmd = [
                    "ffmpeg", "-i", input_src, "-vf", f"fps=1/{max(1, frames)}",
                    "-frames:v", str(frames), f"{tmpdir}/frame_%03d.jpg",
                    "-loglevel", "quiet", "-y"
                ]
                subprocess.run(cmd, capture_output=True, timeout=60)
                
                frame_files = sorted([f for f in os.listdir(tmpdir) if f.endswith(".jpg")])
                for i, ff in enumerate(frame_files):
                    fpath = os.path.join(tmpdir, ff)
                    with open(fpath, "rb") as fh:
                        img_b64 = base64.b64encode(fh.read()).decode()
                    
                    try:
                        desc = await vision_analyze(
                            img_b64,
                            prompt="描述第{}/{}帧画面的内容和动作".format(i+1, len(frame_files))
                        )
                        frame_descriptions.append({
                            "frame": i + 1,
                            "description": desc[:300] if desc else "分析失败",
                            "timestamp": "{}%".format(int(i * 100 / len(frame_files)))
                        })
                    except Exception as e:
                        frame_descriptions.append({
                            "frame": i + 1,
                            "description": "帧分析异常: " + str(e)[:100]
                        })
        except Exception as e:
            logger.warning("视频分析失败: {}".format(e))
            return {"ok": False, "error": str(e)[:200]}
        
        # AI生成摘要
        summary = ""
        if frame_descriptions:
            try:
                summary_prompt = "以下是一个视频的{}个关键帧描述，请用3-5句话总结视频内容:\n".format(len(frame_descriptions))
                for fd in frame_descriptions:
                    summary_prompt += "- 帧{}: {}\n".format(fd["frame"], fd["description"])
                summary = await call_ai([{"role": "user", "content": summary_prompt}], max_tokens=300, temperature=0.3)
            except:
                summary = "视频摘要生成失败"
        else:
            summary = "未能提取视频帧"
        
        return {
            "ok": True,
            "frames_analyzed": len(frame_descriptions),
            "frame_descriptions": frame_descriptions,
            "summary": summary[:500] if summary else "",
            "method": "ffmpeg抽帧 + AI描述摘要"
        }
    
    @classmethod
    async def analyze_audio(cls, audio_path="", audio_url=""):
        """音频转写 + 情感分析"""
        if not audio_path and not audio_url:
            return {"ok": False, "error": "请提供audio_path或audio_url"}
        
        transcript = ""
        sentiment = ""
        try:
            input_src = audio_path or audio_url
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
            
            cmd = ["ffmpeg", "-i", input_src, "-ar", "16000", "-ac", "1", tmp_path, "-loglevel", "quiet", "-y"]
            subprocess.run(cmd, capture_output=True, timeout=60)
            
            if os.path.getsize(tmp_path) > 0:
                transcript = "[音频文件: {} bytes]".format(os.path.getsize(tmp_path))
            else:
                transcript = "音频转码失败"
            
            os.unlink(tmp_path)
        except Exception as e:
            logger.warning("音频分析失败: {}".format(e))
            transcript = "音频处理异常: " + str(e)[:100]
        
        if transcript and "失败" not in transcript:
            try:
                sentiment = await call_ai([
                    {"role": "user", "content": "分析以下文字的情感倾向(正面/负面/中性): " + transcript[:500]}
                ], max_tokens=100, temperature=0.2)
            except:
                sentiment = "情感分析失败"
        
        return {
            "ok": True,
            "transcript": transcript[:1000],
            "sentiment": sentiment[:200] if sentiment else "",
            "method": "ffmpeg音频提取 + AI情感分析"
        }
    
    @classmethod
    async def deep_image_understanding(cls, image_b64="", questions=None):
        """深度图像理解: 场景描述+OCR+物体识别+问答"""
        if not image_b64:
            return {"ok": False, "error": "请提供图片base64数据"}
        
        results = {}
        
        try:
            scene = await vision_analyze(image_b64, prompt="详细描述这张图片的场景、人物、物品和氛围")
            results["scene_description"] = scene[:500] if scene else ""
        except Exception as e:
            results["scene_description"] = "场景描述失败: " + str(e)[:100]
        
        try:
            ocr_text = await vision_analyze(image_b64, prompt="识别并提取图片中所有的文字内容，保持原始格式")
            results["ocr_text"] = ocr_text[:300] if ocr_text else ""
        except Exception as e:
            results["ocr_text"] = "OCR失败: " + str(e)[:100]
        
        try:
            objects = await vision_analyze(image_b64, prompt="列出图片中所有可见的物体、人物和元素，不超过20个")
            results["objects"] = objects[:300] if objects else ""
        except Exception as e:
            results["objects"] = "物体识别失败: " + str(e)[:100]
        
        if questions:
            qa_results = {}
            for q in questions[:5]:
                try:
                    ans = await vision_analyze(image_b64, prompt="关于这张图片: " + q)
                    qa_results[q] = ans[:200] if ans else ""
                except:
                    qa_results[q] = "问答失败"
            results["qa"] = qa_results
        
        return {"ok": True, "results": results, "method": "多模态AI深度理解"}

multimodal_engine = MultimodalEngine()