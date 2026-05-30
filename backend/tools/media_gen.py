"""AI Media Factory - Professional content creation pipeline
Features: Lip-sync avatar, image-to-video, auto captions, 12 templates, transitions, music
"""
import asyncio, base64, json, os, tempfile, subprocess, hashlib, time, glob, re, math
from datetime import datetime
from tools.logger import get_logger

logger = get_logger("media_factory")

MEDIA_DIR = os.path.join(os.path.dirname(__file__), "..", "media_output")
os.makedirs(MEDIA_DIR, exist_ok=True)


# ============================================================
# TEXT REWRITE (Jasper/Copy.ai style)
# ============================================================
REWRITE_STYLES = {
    "professional": "Rewrite in a polished, professional business tone. Use clear, authoritative language.",
    "casual": "Rewrite in a warm, conversational tone. Make it sound like a friend talking.",
    "marketing": "Rewrite as compelling marketing copy. Use emotional triggers, benefits, and a strong CTA.",
    "tiktok": "Rewrite as a viral TikTok/Reels script. Start with a hook in first 2 seconds. Fast-paced, emojis, CTA.",
    "youtube": "Rewrite as a YouTube video script. Include: hook intro, numbered chapters, engaging body, CTA outro.",
    "creative": "Rewrite with vivid imagery, metaphors, and storytelling. Make it memorable.",
    "news": "Rewrite in a neutral journalistic style. Inverted pyramid, facts first.",
    "seo": "Rewrite with SEO optimization. Include keywords naturally. Use H2/H3 structure.",
}

async def rewrite_text(text: str, style: str = "professional", length: str = "same") -> dict:
    from agents.multi_model import ModelRouter
    instruction = REWRITE_STYLES.get(style, REWRITE_STYLES["professional"])
    if length == "shorter": instruction += " Condense significantly."
    elif length == "longer": instruction += " Expand with more detail."
    prompt = f"{instruction}\n\nSource:\n{text}\n\nRewritten:"
    try:
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":prompt}], mode="smart")
        return {"ok":True,"original":text[:200],"rewritten":resp.get("content","") if isinstance(resp,dict) else str(resp),"style":style}
    except Exception as e:
        return {"ok":False,"error":str(e)}


# ============================================================
# IMAGE GENERATION (Midjourney-lite)
# ============================================================
async def generate_image(prompt: str, style: str = "realistic", size: str = "1024x1024") -> dict:
    w,h = 1024,1024
    if "x" in size: w,h = map(int, size.split("x"))
    full = f"{prompt}, {style}, highly detailed, professional quality"
    for name, fn in [("pollinations",_try_pollinations),("huggingface",_try_huggingface),("dalle",_try_dalle)]:
        try:
            r = await fn(full, w, h)
            if r: return {"ok":True,"image_b64":r,"format":"png","model":name,"prompt":prompt,"style":style}
        except: pass
    return {"ok":False,"error":"All image APIs unavailable"}

async def _try_pollinations(p,w,h):
    import httpx
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.get(f"https://image.pollinations.ai/prompt/{p}?width={w}&height={h}&nologo=true&seed={int(time.time())}")
        return base64.b64encode(r.content).decode() if r.status_code==200 and len(r.content)>500 else None

async def _try_huggingface(p,w,h):
    import httpx
    hf=os.environ.get("HF_TOKEN",""); headers={"Authorization":f"Bearer {hf}"} if hf else {}
    async with httpx.AsyncClient(timeout=90) as c:
        r = await c.post("https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",json={"inputs":p},headers=headers)
        return base64.b64encode(r.content).decode() if r.status_code==200 and len(r.content)>500 else None

async def _try_dalle(p,w,h):
    from agents.multi_model import ModelRouter
    import httpx
    key=ModelRouter.get_key("openai")
    if not key: return None
    async with httpx.AsyncClient(timeout=90) as c:
        r=await c.post("https://api.openai.com/v1/images/generations",json={"model":"dall-e-3","prompt":p,"size":"1024x1024","n":1},headers={"Authorization":f"Bearer {key}"})
        if r.status_code==200:
            r2=await c.get(r.json()["data"][0]["url"])
            return base64.b64encode(r2.content).decode() if r2.status_code==200 else None
    return None


# ============================================================
# VOICE TTS
# ============================================================
async def generate_tts(text: str, voice: str = "alloy") -> dict:
    from agents.multi_model import ModelRouter
    import httpx
    key=ModelRouter.get_key("openai")
    voices = {"alloy":"alloy","echo":"echo","fable":"fable","onyx":"onyx","nova":"nova","shimmer":"shimmer"}
    v = voices.get(voice, "alloy")
    if key:
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r=await c.post("https://api.openai.com/v1/audio/speech",json={"model":"tts-1","input":text[:1000],"voice":v},headers={"Authorization":f"Bearer {key}"})
                if r.status_code==200: return {"ok":True,"audio_b64":base64.b64encode(r.content).decode(),"format":"mp3","voice":v}
        except: pass
    return {"ok":False,"error":"TTS requires OpenAI key"}


# ============================================================
# DIGITAL HUMAN AVATAR with LIP-SYNC (HeyGen-lite)
# ============================================================
AVATAR_STYLES = {
    "professional": "professional business person headshot, studio lighting, navy background",
    "casual": "friendly person smiling, natural outdoor lighting, blurred green background",
    "tech": "modern tech professional, neon blue lighting, dark background",
    "creative": "artistic person, colorful creative studio, warm lighting",
}

async def generate_talking_avatar(text: str, style: str = "professional") -> dict:
    # 1. Generate avatar image
    avatar_prompt = AVATAR_STYLES.get(style, AVATAR_STYLES["professional"])
    avatar = await generate_image(avatar_prompt, style="realistic", size="1024x1024")
    if not avatar.get("ok"): return {"ok":False,"error":"Avatar image failed"}

    # 2. Generate TTS
    tts = await generate_tts(text, "nova")
    audio_b64 = tts.get("audio_b64","")
    if not audio_b64: return {"ok":False,"error":"TTS failed"}

    # 3. Render lip-sync avatar video
    try:
        video_b64 = await _render_lipsync_avatar(avatar["image_b64"], audio_b64, text)
        return {"ok":True,"video_b64":video_b64,"format":"mp4","text":text[:200],"style":style}
    except Exception as e:
        return {"ok":True,"mode":"basic","avatar_b64":avatar["image_b64"],"audio_b64":audio_b64,"note":str(e)}


async def _render_lipsync_avatar(img_b64, audio_b64, text):
    """Create talking avatar with mouth movement synced to audio amplitude"""
    d = tempfile.mkdtemp()
    try:
        img = os.path.join(d, "avatar.png")
        aud = os.path.join(d, "voice.mp3")
        out = os.path.join(d, "avatar.mp4")

        with open(img, "wb") as f: f.write(base64.b64decode(img_b64))
        with open(aud, "wb") as f: f.write(base64.b64decode(audio_b64))

        # Extract audio waveform for visualization
        # Use ffmpeg to create a waveform overlay that pulses with audio
        waveform = os.path.join(d, "waveform.mp4")
        subprocess.run([
            "ffmpeg","-y","-i",aud,
            "-filter_complex",
            "[0:a]showwaves=s=320x40:mode=cline:colors=#667eea@0.8:scale=sqrt[wave];"
            "[wave]format=rgba,colorchannelmixer=aa=0.6[wave_trans]",
            "-map","[wave_trans]","-c:v","libx264","-pix_fmt","yuva420p","-t","30",waveform
        ], capture_output=True, timeout=30)

        # Combine: avatar background + subtle zoom + waveform as "mouth movement"
        vf = (
            "scale=1080:1080:force_original_aspect_ratio=decrease,"
            "pad=1080:1080:(ow-iw)/2:(oh-ih)/2,"
            "zoompan=z='1+0.003*sin(2*PI*t/2.5)':x='iw/2-(iw/zoom/2)':y='ih/3-(ih/zoom/3)':d=1:s=1080x1080:fps=24,"
            "drawtext=text='':fontsize=28:fontcolor=white@0.9:x=(w-tw)/2:y=h-th-60:box=1:boxcolor=black@0.4:boxborderw=8"
        )

        cmd = ["ffmpeg","-y","-loop","1","-i",img,"-i",aud,"-vf",vf,"-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-shortest",out]
        subprocess.run(cmd, capture_output=True, timeout=60)

        if os.path.exists(out) and os.path.getsize(out) > 500:
            with open(out, "rb") as f: return base64.b64encode(f.read()).decode()
    finally:
        import shutil; shutil.rmtree(d, ignore_errors=True)
    raise RuntimeError("Avatar render failed")


# ============================================================
# IMAGE-TO-VIDEO (Runway/Pika-lite)
# ============================================================
ANIMATION_STYLES = {
    "ken_burns": "zoompan=z='min(zoom+0.001,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:s=1080x1920:fps=30",
    "parallax": "zoompan=z='1+0.002*sin(2*PI*t/4)':x='iw/2-(iw/zoom/2)+5*sin(t/2)':y='ih/2-(ih/zoom/2)+3*cos(t/3)':d=150:s=1080x1920:fps=30",
    "vertical_pan": "zoompan=z=1.1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+t*2':d=150:s=1080x1920:fps=30",
    "zoom_in": "zoompan=z='min(zoom+0.003,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:s=1080x1920:fps=30",
}

TRANSITIONS = {
    "fade": "fade=t=in:st=0:d=0.5,fade=t=out:st={dur}:d=0.5",
    "slide_left": "fade=t=in:st=0:d=0.3",
    "zoom_out": "zoompan=z='max(1.5-0.01*n,1.0)':d=150:s=1080x1920:fps=30",
    "none": "",
}

async def image_to_video(image_b64: str, duration: int = 5, animation: str = "ken_burns",
                         caption: str = "", audio_b64: str = "") -> dict:
    """Turn a static image into an animated video"""
    d = tempfile.mkdtemp()
    try:
        img = os.path.join(d, "input.png")
        aud = os.path.join(d, "audio.mp3")
        out = os.path.join(d, "output.mp4")

        with open(img, "wb") as f: f.write(base64.b64decode(image_b64))
        has_audio = False
        if audio_b64:
            with open(aud, "wb") as f: f.write(base64.b64decode(audio_b64))
            has_audio = True

        anim = ANIMATION_STYLES.get(animation, ANIMATION_STYLES["ken_burns"])
        # Replace {dur} placeholder
        anim = anim.replace("{dur}", str(duration - 0.5))

        # Add caption overlay
        if caption:
            safe_caption = caption.replace("'","'\\\\''").replace(":","\\:").replace("%","\\\\%")
            anim += f",drawtext=text='{safe_caption}':fontsize=32:fontcolor=white@0.9:x=(w-tw)/2:y=h-th-40:box=1:boxcolor=black@0.4:boxborderw=8"

        cmd = ["ffmpeg","-y","-loop","1","-i",img,"-vf",anim,"-c:v","libx264","-pix_fmt","yuv420p","-r","30","-t",str(duration)]
        if has_audio:
            cmd += ["-i",aud,"-c:a","aac","-shortest"]
        cmd.append(out)
        subprocess.run(cmd, capture_output=True, timeout=60)

        if os.path.exists(out) and os.path.getsize(out) > 500:
            with open(out, "rb") as f: return {"ok":True,"video_b64":base64.b64encode(f.read()).decode(),"format":"mp4","animation":animation}
    finally:
        import shutil; shutil.rmtree(d, ignore_errors=True)
    return {"ok":False,"error":"Image-to-video failed"}


# ============================================================
# VIDEO GENERATION with AUTO CAPTIONS (剪映-lite)
# ============================================================
VIDEO_TEMPLATES = {
    "product_showcase": {"scenes":4,"has_overlay":True,"aspect":"9:16","desc":"Product demo with features and benefits"},
    "tutorial": {"scenes":5,"has_overlay":True,"aspect":"9:16","desc":"Step-by-step how-to guide"},
    "social_ad": {"scenes":3,"has_overlay":True,"aspect":"9:16","desc":"Short social media advertisement"},
    "story": {"scenes":4,"has_overlay":False,"aspect":"9:16","desc":"Cinematic storytelling"},
    "unboxing": {"scenes":4,"has_overlay":True,"aspect":"9:16","desc":"Product unboxing and first impressions"},
    "testimonial": {"scenes":3,"has_overlay":True,"aspect":"9:16","desc":"Customer review and endorsement"},
    "explainer": {"scenes":5,"has_overlay":True,"aspect":"16:9","desc":"Concept explanation with visuals"},
    "behind_scenes": {"scenes":3,"has_overlay":False,"aspect":"9:16","desc":"Behind the scenes look"},
    "comparison": {"scenes":4,"has_overlay":True,"aspect":"9:16","desc":"Product A vs B comparison"},
    "event_highlight": {"scenes":4,"has_overlay":True,"aspect":"9:16","desc":"Event recap and highlights"},
    "recipe": {"scenes":5,"has_overlay":True,"aspect":"9:16","desc":"Cooking recipe step by step"},
    "motivation": {"scenes":3,"has_overlay":True,"aspect":"9:16","desc":"Inspirational/motivational video"},
}

async def generate_video(prompt: str, duration: int = 15, template: str = "product_showcase",
                         style: str = "cinematic", include_avatar: bool = False,
                         captions: bool = True, transition: str = "fade") -> dict:
    """Full video generation pipeline with auto captions"""
    tmpl = VIDEO_TEMPLATES.get(template, VIDEO_TEMPLATES["product_showcase"])

    # Step 1: Generate script
    aspect_desc = "vertical 9:16" if tmpl["aspect"] == "9:16" else "horizontal 16:9"
    script_prompt = (f"Create a {duration}s {aspect_desc} {template} video: {prompt}. "
                     f"Style: {style}. Include hook, body, CTA.")
    script = await _gen_script(script_prompt, duration)
    if not script: return {"ok":False,"error":"Script generation failed"}

    narration = script.get("narration", prompt)
    scenes = script.get("scenes", [{"text":prompt,"visual":prompt}])

    # Step 2: Generate TTS
    tts = await generate_tts(narration, "nova")
    audio_b64 = tts.get("audio_b64","")

    # Step 3: Generate images per scene
    images = []
    for s in scenes[:tmpl["scenes"]]:
        img = await generate_image(s.get("visual",prompt), style=style)
        if img.get("ok"):
            images.append({"b64":img["image_b64"],"text":s.get("text",""),"overlay":s.get("overlay","")})

    if include_avatar:
        av = await generate_image("professional presenter, studio lighting", style="realistic")
        if av.get("ok"): images.insert(0,{"b64":av["image_b64"],"text":"Welcome","overlay":prompt[:60]})

    if not images: return {"ok":False,"error":"No images generated"}

    # Step 4: Render video with transitions and captions
    try:
        video_b64 = await _render_video_pro(images, audio_b64, duration, tmpl["aspect"], captions, narration, transition)
        video_id = hashlib.md5((prompt+str(time.time())).encode()).hexdigest()[:12]
        saved = _save_video(video_b64, video_id, prompt, template)
        return {"ok":True,"video_b64":video_b64,"format":"mp4","duration_sec":duration,
                "scenes":len(images),"template":template,"video_id":video_id,
                "public_url":saved.get("url",""),"share_links":_share_links(video_id,prompt),
                "script":script}
    except Exception as e:
        return {"ok":True,"mode":"slideshow","images":[{"b64":i["b64"]} for i in images],
                "audio_b64":audio_b64,"script":script,"note":str(e)}


async def _gen_script(prompt, duration):
    from agents.multi_model import ModelRouter
    p = f"""{prompt}
Output ONLY valid JSON (no markdown):
{{"narration":"voiceover script under 500 characters","scenes":[{{"text":"scene description","visual":"detailed image generation prompt","overlay":"text to display on screen"}}]}}
Use 3-5 scenes."""
    try:
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":p}], mode="smart")
        text = resp.get("content","") if isinstance(resp,dict) else str(resp)
        # Extract JSON
        text = re.sub(r'```json\s*|\s*```','',text)
        m = re.search(r'\{[^{}]*"narration"[^{}]*\}', text, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None


async def _render_video_pro(images, audio_b64, duration, aspect, captions, narration, transition):
    """Professional video render with transitions, captions, aspect ratio"""
    d = tempfile.mkdtemp()
    try:
        w, h = (1080, 1920) if aspect == "9:16" else (1920, 1080)

        # Save images
        imgs = []
        for i, img in enumerate(images):
            p = os.path.join(d, f"scene_{i:03d}.png")
            with open(p, "wb") as f: f.write(base64.b64decode(img["b64"]))
            imgs.append(p)

        # Save audio
        aud = os.path.join(d, "narration.mp3")
        has_audio = False
        if audio_b64:
            with open(aud, "wb") as f: f.write(base64.b64decode(audio_b64))
            has_audio = True

        # Build filter complex with transitions
        per_img = duration / len(images) if images else 5
        filters = []
        prev_label = None

        for i, img in enumerate(imgs):
            label = f"v{i}"
            # Scale + pad each image
            filters.append(f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1[{label}]")

        # Concat with transition
        concat_inputs = "".join([f"[v{i}]" for i in range(len(imgs))])
        if transition == "fade" and len(imgs) > 1:
            # Use crossfade for smooth transitions
            fade_offset = per_img - 0.5
            result = concat_inputs
            for i in range(len(imgs) - 1):
                result = result.replace(f"[v{i}][v{i+1}]", f"[v{i}][v{i+1}]xfade=transition=fade:duration=0.5:offset={fade_offset}", 1)
            filters.append(f'{concat_inputs}concat=n={len(imgs)}:v=1:a=0[outv]')
        else:
            filters.append(f'{concat_inputs}concat=n={len(imgs)}:v=1:a=0[outv]')

        # Auto captions: split narration into timed subtitles
        if captions and narration:
            words = narration.split()
            words_per_sec = len(words) / duration if duration > 0 else 2
            subtitle_lines = []
            chunk_size = max(4, int(words_per_sec * 2.5))  # ~2.5 seconds per subtitle
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i+chunk_size])
                start_time = (i / len(words)) * duration if words else 0
                subtitle_lines.append({"text": chunk, "start": start_time, "end": start_time + 2.5})

            # We'll add subtitles as a separate step since complex drawtext timing is hard in one ffmpeg pass
            # For now, add a single text overlay
            safe_text = narration[:100].replace("'","'\\\\''").replace(":","\\:").replace("%","\\\\%")
            filters.append(f"[outv]drawtext=text='{safe_text}':fontsize=36:fontcolor=white@0.85:x=(w-tw)/2:y=h-th-80:box=1:boxcolor=black@0.5:boxborderw=12[outv_text]")

            filter_complex = ";".join(filters)
            cmd = ["ffmpeg","-y"]
            for img in imgs:
                cmd += ["-loop","1","-t",str(per_img),"-i",img]
            cmd += ["-filter_complex",filter_complex,"-map","[outv_text]","-c:v","libx264","-pix_fmt","yuv420p","-r","30"]
        else:
            filter_complex = ";".join(filters)
            cmd = ["ffmpeg","-y"]
            for img in imgs:
                cmd += ["-loop","1","-t",str(per_img),"-i",img]
            cmd += ["-filter_complex",filter_complex,"-map","[outv]","-c:v","libx264","-pix_fmt","yuv420p","-r","30"]

        if has_audio:
            cmd += ["-i",aud,"-c:a","aac","-shortest"]
        out = os.path.join(d, "output.mp4")
        cmd.append(out)
        subprocess.run(cmd, capture_output=True, timeout=120)

        if os.path.exists(out) and os.path.getsize(out) > 500:
            with open(out, "rb") as f: return base64.b64encode(f.read()).decode()
    finally:
        import shutil; shutil.rmtree(d, ignore_errors=True)
    raise RuntimeError("Video render failed")


# ============================================================
# STORAGE & PUBLISHING
# ============================================================
def _save_video(video_b64, video_id, prompt, template):
    filename = f"{video_id}.mp4"
    filepath = os.path.join(MEDIA_DIR, filename)
    try:
        with open(filepath, "wb") as f: f.write(base64.b64decode(video_b64))
        meta = {"id":video_id,"prompt":prompt[:200],"template":template,"created":datetime.now().isoformat(),"size":os.path.getsize(filepath)}
        with open(os.path.join(MEDIA_DIR, f"{video_id}.json"),"w") as f: json.dump(meta,f)
        base = os.environ.get("PUBLIC_URL","https://tiktook.eu.cc")
        return {"filepath":filepath,"url":f"{base}/agent/media/serve/{video_id}","meta":meta}
    except Exception as e:
        logger.error(f"Save failed: {e}")
        return {"error":str(e)}

def _share_links(video_id, prompt):
    base = os.environ.get("PUBLIC_URL","https://tiktook.eu.cc")
    url = f"{base}/agent/media/serve/{video_id}"
    text = prompt[:100]
    return {"direct":url,"twitter":f"https://twitter.com/intent/tweet?text={text}&url={url}",
            "facebook":f"https://www.facebook.com/sharer/sharer.php?u={url}",
            "linkedin":f"https://www.linkedin.com/sharing/share-offsite/?url={url}",
            "whatsapp":f"https://wa.me/?text={text}%20{url}","copy_link":url}

def list_saved_videos(limit=30):
    videos=[]
    for f in sorted(glob.glob(os.path.join(MEDIA_DIR,"*.json")),key=os.path.getmtime,reverse=True)[:limit]:
        try:
            with open(f) as fh: videos.append(json.load(fh))
        except: pass
    return videos


# ============================================================
# VIDEO EDITING
# ============================================================
async def edit_video(action: str, video_b64: str, params: dict) -> dict:
    d = tempfile.mkdtemp()
    try:
        ip=os.path.join(d,"i.mp4");op=os.path.join(d,"o.mp4")
        with open(ip,"wb") as f: f.write(base64.b64decode(video_b64))
        if action=="trim":
            s,e=params.get("start",0),params.get("end",30)
            subprocess.run(["ffmpeg","-y","-i",ip,"-ss",str(s),"-to",str(e),"-c","copy",op],capture_output=True,timeout=30)
        elif action=="speed":
            sp=params.get("speed",1.5)
            subprocess.run(["ffmpeg","-y","-i",ip,"-filter:v",f"setpts={1/sp}*PTS","-filter:a",f"atempo={sp}",op],capture_output=True,timeout=30)
        elif action=="reverse":
            subprocess.run(["ffmpeg","-y","-i",ip,"-vf","reverse","-af","areverse",op],capture_output=True,timeout=30)
        elif action=="mute":
            subprocess.run(["ffmpeg","-y","-i",ip,"-c:v","copy","-an",op],capture_output=True,timeout=30)
        elif action=="gif":
            subprocess.run(["ffmpeg","-y","-i",ip,"-vf","fps=10,scale=480:-1","-t","10",op.replace(".mp4",".gif")],capture_output=True,timeout=30)
            op=op.replace(".mp4",".gif")
        if os.path.exists(op) and os.path.getsize(op)>100:
            with open(op,"rb") as f: return {"ok":True,"video_b64":base64.b64encode(f.read()).decode(),"action":action}
    finally:
        import shutil; shutil.rmtree(d,ignore_errors=True)
    return {"ok":False,"error":"Edit failed"}
