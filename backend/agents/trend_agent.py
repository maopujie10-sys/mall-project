锘?""Trend Agent 鈥?鐑偣鐩戞帶 / 鑸嗘儏鍒嗘瀽 / 瓒嬪娍棰勬祴
鐩戞帶锛氭姈闊?B绔?寰崥/X/YouTube/Google Trends"""
import httpx
import asyncio
from datetime import datetime
from dataclasses import dataclass

@dataclass
class TrendItem:
    platform: str
    rank: int
    title: str
    hot_score: int
    url: str
    category: str = ""
    fetched_at: str = ""


    @staticmethod
    async def fetch_youtube_trends(region: str = "US", limit: int = 10) -> list:
        """YouTube 鐑棬瑙嗛"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.get(f"https://www.youtube.com/feed/trending?gl={region}",
                    headers={"User-Agent":"Mozilla/5.0"})
                if r.status_code == 200:
                    import re
                    titles = re.findall(r'"title":{"runs":[{"text":"([^"]+)"', r.text)[:limit]
                    return [{"title": t, "source": "youtube", "rank": i+1} for i, t in enumerate(titles)]
        except: pass
        return []

    @staticmethod
    async def fetch_google_trends(keywords: list = None, limit: int = 10) -> list:
        """Google Trends 鐑棬鎼滅储"""
        keywords = keywords or ["AI","tech","shop","fashion"]
        try:
            import httpx
            results = []
            for kw in keywords[:5]:
                async with httpx.AsyncClient(timeout=15) as c:
                    r = await c.get(f"https://trends.google.com/trends/explore?q={kw}",
                        headers={"User-Agent":"Mozilla/5.0"})
                    results.append({"keyword": kw, "status": "available" if r.status_code==200 else "blocked"})
            return results
        except: return []

    @staticmethod
    async def fetch_x_trends(limit: int = 10) -> list:
        """X (Twitter) 瓒嬪娍"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.get("https://nitter.net/",
                    headers={"User-Agent":"Mozilla/5.0"})
                if r.status_code == 200:
                    import re
                    trends = re.findall(r'title="([^"]+)"', r.text)[:limit]
                    return [{"title": t, "source": "x", "rank": i+1} for i, t in enumerate(trends)]
        except: pass
        return []

    @staticmethod
    async def predict_trend(topic: str) -> dict:
        """瓒嬪娍棰勬祴 鈥?鍩轰簬鍏抽敭璇嶅垎鏋愮儹搴﹁蛋鍚?""
        scores = {"涓婂崌": 0, "绋冲畾": 0, "涓嬮檷": 0}
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"https://www.google.com/search?q={topic}",
                    headers={"User-Agent":"Mozilla/5.0"})
                text = r.text.lower()
                if "trending" in text or "popular" in text: scores["涓婂崌"] += 30
                if "news" in text: scores["绋冲畾"] += 20
                if "old" in text or "archive" in text: scores["涓嬮檷"] += 15
        except: pass
        predicted = max(scores, key=scores.get)
        return {"topic": topic, "predicted": predicted, "confidence": scores[predicted], "scores": scores}

class TrendAgent:
    """鐑偣鐩戞帶Agent"""

    PLATFORMS = {
        "weibo": {"name": "寰崥鐑悳", "icon": "馃摙", "color": "#ff4d4f"},
        "douyin": {"name": "鎶栭煶鐑偣", "icon": "馃幍", "color": "#010101"},
        "bilibili": {"name": "B绔欑儹闂?, "icon": "馃摵", "color": "#fb7299"},
        "zhihu": {"name": "鐭ヤ箮鐑", "icon": "馃挕", "color": "#0084ff"},
        "twitter": {"name": "X/Twitter", "icon": "馃惁", "color": "#1da1f2"},
        "youtube": {"name": "YouTube", "icon": "鈻讹笍", "color": "#ff0000"},
    }

    @staticmethod
    async def fetch_trends(platform: str = None) -> dict:
        """鑾峰彇鐑偣鏁版嵁 (妯℃嫙/API)"""
        now = datetime.now().isoformat()
        results = {}

        platforms_to_fetch = [platform] if platform else list(TrendAgent.PLATFORMS.keys())

        for pf in platforms_to_fetch:
            if pf not in TrendAgent.PLATFORMS:
                continue
            # 妯℃嫙鐑偣鏁版嵁锛堢敓浜х幆澧冩帴鍏ョ湡瀹濧PI锛?            results[pf] = {
                "platform": pf,
                "name": TrendAgent.PLATFORMS[pf]["name"],
                "icon": TrendAgent.PLATFORMS[pf]["icon"],
                "color": TrendAgent.PLATFORMS[pf]["color"],
                "trends": [
                    {
                        "rank": i + 1,
                        "title": _get_sample_trend(pf, i),
                        "hot_score": 1000000 - i * 80000,
                        "url": f"https://{pf}.com/trend/{i}",
                        "category": ["绉戞妧", "濞变箰", "绀句細", "璐㈢粡", "浣撹偛"][i % 5],
                    }
                    for i in range(15)
                ],
                "fetched_at": now,
            }

        return {
            "ok": True,
            "platforms": results,
            "fetched_at": now,
        }

    @staticmethod
    async def analyze_trend(keyword: str) -> dict:
        """鍒嗘瀽鎸囧畾鍏抽敭璇嶇殑鐑害瓒嬪娍"""
        return {
            "keyword": keyword,
            "hot_score": 850000,
            "trend_direction": "up",
            "related_topics": [f"{keyword}鏂板搧", f"{keyword}浼樻儬", f"{keyword}璇勬祴"],
            "suggested_action": f"寤鸿鍦ㄥ晢鍩庝笂鏋秢keyword}鐩稿叧鍟嗗搧",
            "analyzed_at": datetime.now().isoformat(),
        }

    @staticmethod
    async def predict_hot(category: str = "绉戞妧") -> list:
        """棰勬祴鍗冲皢鐑棬鐨勫搧绫?鍏抽敭璇?""
        predictions = {
            "绉戞妧": ["AI鎵嬫満", "鎶樺彔灞?, "AR鐪奸暅", "鏅鸿兘鎵嬭〃", "鏃犵嚎鍏呯數"],
            "缇庡": ["闃叉檼闇?, "绮惧崕娑?, "闈㈣啘", "鍙ｇ孩", "绮夊簳娑?],
            "鏈嶉グ": ["闃叉檼琛?, "杩愬姩闉?, "T鎭?, "杩炶。瑁?, "娼墝"],
            "椋熷搧": ["鍋ュ悍闆堕", "铔嬬櫧妫?, "姘旀场姘?, "閫熼", "鍜栧暋"],
        }
        return predictions.get(category, predictions["绉戞妧"])

def _get_sample_trend(platform: str, index: int) -> str:
    samples = {
        "weibo": ["鏌愭槑鏄熷畼瀹ｆ亱鎯?, "楂樿€冩垚缁╁叕甯?, "鏂版斂绛栧嚭鍙?, "鐑棬缁艰壓寮€鎾?, "绉戞妧鏂板搧鍙戝竷"],
        "douyin": ["#鎸戞垬璇濋 鐖嗙伀鍏ㄧ綉", "鑸炶箞鎸戞垬", "缇庨鎺㈠簵", "鏃呮父鏀荤暐", "钀屽疇鏃ュ父"],
        "bilibili": ["鏂扮暘涓婄嚎", "娓告垙瀹炲喌", "楝肩暅瑙嗛", "鏁扮爜璇勬祴", "绾綍鐗囨帹鑽?],
        "zhihu": ["濡備綍鐪嬪緟...", "鏈夊摢浜涙帹鑽?..", "鎬庢牱璇勪环...", "涓轰粈涔?..", "濡備綍瀛︿範..."],
        "twitter": ["Breaking News", "Tech Launch", "Sports Update", "Music Release", "AI Trends"],
        "youtube": ["Music Video Premiere", "Tech Review", "Gaming Stream", "Tutorial", "Vlog"],
    }
    platform_samples = samples.get(platform, samples["weibo"])
    return platform_samples[index % len(platform_samples)]
