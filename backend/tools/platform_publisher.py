"""Multi-Platform Publisher - Real API clients for TikTok/YouTube/Instagram/Facebook/Bilibili/Kuaishou/XHS
Set env vars with your API credentials. Unconfigured platforms auto-fallback to mock.
"""
import asyncio, json, os, hashlib, secrets, base64
from tools.logger import get_logger
logger = get_logger("platform_publisher")

def env(k,d=""): return os.getenv(k,d)

CFG = {
    "tiktok": {"ck":env("TIKTOK_CLIENT_KEY"),"cs":env("TIKTOK_CLIENT_SECRET"),"at":env("TIKTOK_ACCESS_TOKEN"),"rt":env("TIKTOK_REFRESH_TOKEN"),"cid":env("TIKTOK_CREATOR_ID"),"base":"https://open.tiktokapis.com/v2","scope":"video.upload,video.publish"},
    "youtube":{"cid":env("YOUTUBE_CLIENT_ID"),"cs":env("YOUTUBE_CLIENT_SECRET"),"at":env("YOUTUBE_ACCESS_TOKEN"),"rt":env("YOUTUBE_REFRESH_TOKEN"),"chid":env("YOUTUBE_CHANNEL_ID"),"base":"https://www.googleapis.com/youtube/v3","up":"https://www.googleapis.com/upload/youtube/v3/videos","scope":"https://www.googleapis.com/auth/youtube.upload"},
    "instagram":{"aid":env("INSTAGRAM_APP_ID"),"as":env("INSTAGRAM_APP_SECRET"),"at":env("INSTAGRAM_ACCESS_TOKEN"),"uid":env("INSTAGRAM_USER_ID"),"base":"https://graph.facebook.com/v19.0","scope":"instagram_basic,instagram_content_publish"},
    "facebook":{"aid":env("FACEBOOK_APP_ID"),"as":env("FACEBOOK_APP_SECRET"),"at":env("FACEBOOK_ACCESS_TOKEN"),"pid":env("FACEBOOK_PAGE_ID"),"base":"https://graph.facebook.com/v19.0","scope":"pages_manage_posts"},
    "bilibili":{"cid":env("BILIBILI_CLIENT_ID"),"cs":env("BILIBILI_CLIENT_SECRET"),"at":env("BILIBILI_ACCESS_TOKEN"),"base":"https://member.bilibili.com/openplatform"},
    "kuaishou":{"aid":env("KUAISHOU_APP_ID"),"as":env("KUAISHOU_APP_SECRET"),"at":env("KUAISHOU_ACCESS_TOKEN"),"base":"https://open.kuaishou.com"},
    "xiaohongshu":{"aid":env("XHS_APP_ID"),"as":env("XHS_APP_SECRET"),"at":env("XHS_ACCESS_TOKEN"),"base":"https://openapi.xiaohongshu.com"},
}

NAMES = {"tiktok":"TikTok","youtube":"YouTube Shorts","instagram":"Instagram Reels","facebook":"Facebook Reels","bilibili":"Bilibili","kuaishou":"Kuaishou","xiaohongshu":"RED"}

class PlatformPublisher:
    def __init__(self,pid): self.pid=pid; self.cfg=CFG.get(pid,{}); self._http=None
    @property
    def ok(self): return bool(self.cfg.get("at") or self.cfg.get("ck") or self.cfg.get("cid") or self.cfg.get("aid"))
    @property
    def name(self): return NAMES.get(self.pid,self.pid)
    async def http(self):
        if not self._http:
            import httpx; self._http=httpx.AsyncClient(timeout=120)
        return self._http
    def cred_status(self):
        ks=["client_key","client_id","app_id","access_token"];set_=[k for k in ks if self.cfg.get(k[:3] if k.startswith("ac") else k[:2])]
        return {"platform":self.pid,"configured":len(set_)>0,"name":self.name}

async def publish_one(pid, video_path, title, desc="", tags="", schedule=""):
    cfg=CFG.get(pid,{})
    if not cfg.get("at") and not cfg.get("ck") and not cfg.get("cid") and not cfg.get("aid"):
        return {"ok":True,"platform":NAMES.get(pid,pid),"video_id":hashlib.md5(f"{title}{pid}".encode()).hexdigest()[:12],"status":"published","url":"","message":f"[Mock] Set {pid.upper()}_ACCESS_TOKEN env var to publish for real"}
    try:
        import httpx
        async with httpx.AsyncClient(timeout=120) as h:
            if pid=="tiktok":
                return await _tiktok(h,cfg,video_path,title,desc,tags)
            elif pid=="youtube":
                return await _youtube(h,cfg,video_path,title,desc,tags)
            elif pid=="instagram":
                return await _instagram(h,cfg,video_path,title,desc,tags)
            elif pid=="facebook":
                return await _facebook(h,cfg,video_path,title,desc,tags)
            else:
                return await _generic(h,cfg,pid,video_path,title,desc,tags)
    except FileNotFoundError:
        return {"ok":False,"error":f"File not found: {video_path}"}
    except Exception as e:
        logger.error(f"{pid} error: {e}")
        return {"ok":False,"error":str(e)}

async def _tiktok(h,cfg,vp,title,desc,tags):
    headers={"Authorization":f"Bearer {cfg['at']}","Content-Type":"application/json"}
    r1=await h.post(f"{cfg['base']}/video/upload",headers=headers,json={"source":"FILE_UPLOAD","video_name":f"{title[:100]}.mp4"})
    d=r1.json();ui=d.get("data",{});
    if not ui.get("upload_url"): return {"ok":False,"error":f"TikTok init: {d.get('error',{}).get('message','')}"}
    with open(vp,"rb") as f: await h.put(ui["upload_url"],content=f.read(),headers={"Content-Type":"video/mp4"})
    pid=ui.get("publish_id","")
    r2=await h.post(f"{cfg['base']}/video/publish",headers=headers,json={"publish_id":pid,"post_info":{"title":title[:150],"description":(desc or title)[:4000],"privacy_level":"PUBLIC_TO_EVERYONE"}})
    d2=r2.json();ok=d2.get("data",{}).get("status") in ("PROCESSING","PUBLISH_COMPLETE")
    return {"ok":ok,"platform":"TikTok","video_id":pid,"status":"published" if ok else "failed","url":f"https://www.tiktok.com/@{cfg.get('cid','user')}/video/{pid}"}

async def _youtube(h,cfg,vp,title,desc,tags):
    size=os.path.getsize(vp);snippet={"title":title[:100],"description":f"#Shorts {(desc or title)[:5000]}","tags":["shorts"],"categoryId":"22"}
    body={"snippet":snippet,"status":{"privacyStatus":"public","selfDeclaredMadeForKids":False}}
    r1=await h.post(f"{cfg['up']}?uploadType=resumable&part=snippet,status",headers={"Authorization":f"Bearer {cfg['at']}","X-Upload-Content-Type":"video/mp4","X-Upload-Content-Length":str(size)},json=body)
    up_url=r1.headers.get("Location","")
    if not up_url: return {"ok":False,"error":"YouTube upload init failed"}
    with open(vp,"rb") as f: r2=await h.put(up_url,content=f.read(),headers={"Content-Type":"video/mp4","Content-Length":str(size)})
    vid=r2.json().get("id","")
    return {"ok":True,"platform":"YouTube Shorts","video_id":vid,"status":"published","url":f"https://www.youtube.com/shorts/{vid}"}

async def _instagram(h,cfg,vp,title,desc,tags):
    cap=f"{(desc or title)[:2200]}\n.\n{' '.join('#'+t.strip() for t in (tags or '').split(',')[:10] if t.strip())}"
    r1=await h.post(f"{cfg['base']}/{cfg['uid']}/media",params={"media_type":"REELS","video_url":vp,"caption":cap,"share_to_feed":"true","access_token":cfg["at"]})
    cid=r1.json().get("id","")
    if not cid: return {"ok":False,"error":"Instagram container failed"}
    await asyncio.sleep(5)
    r2=await h.post(f"{cfg['base']}/{cfg['uid']}/media_publish",params={"creation_id":cid,"access_token":cfg["at"]})
    mid=r2.json().get("id",cid)
    return {"ok":True,"platform":"Instagram Reels","video_id":mid,"status":"published","url":f"https://www.instagram.com/reel/{mid}/"}

async def _facebook(h,cfg,vp,title,desc,tags):
    with open(vp,"rb") as f:
        r=await h.post(f"{cfg['base']}/{cfg['pid']}/videos",files={"source":(os.path.basename(vp),f,"video/mp4")},data={"title":title[:255],"description":(desc or title)[:5000],"access_token":cfg["at"]})
    vid=r.json().get("id","")
    return {"ok":True,"platform":"Facebook Reels","video_id":vid,"status":"published","url":f"https://www.facebook.com/reel/{vid}"}

async def _generic(h,cfg,pid,vp,title,desc,tags):
    with open(vp,"rb") as f:
        files={"video":(os.path.basename(vp),f,"video/mp4")}
        data={"title":title[:80],"description":(desc or title)[:1000]}
        r=await h.post(cfg.get("base","")+"/video/upload",headers={"Authorization":f"Bearer {cfg.get('at','')}"},files=files,data=data)
    result=r.json()
    return {"ok":result.get("code",0)==0 or result.get("result")==1,"platform":NAMES.get(pid,pid),"video_id":result.get("data",{}).get("video_id","") or result.get("id",""),"status":"published","message":"Published"}

async def publish_all(video_path, title, desc="", tags="", platforms=None, schedule=""):
    if not platforms: platforms=["tiktok","youtube"]
    results=[]
    for pid in platforms[:8]:
        r=await publish_one(pid, video_path, title, desc, tags, schedule)
        results.append(r)
    return results

def all_cred_status():
    return [PlatformPublisher(pid).cred_status() for pid in CFG]