閿?""閸欐ɑ娲挎０鍕潔 + 閺佺増宓侀懘杈ㄦ櫛 閳?闁氨鏁ゅ銉ュ徔濡€虫健"""
import re

# ===== 閺佺増宓侀懘杈ㄦ櫛 =====
def mask_sensitive(text: str) -> str:
    """閼磋鲸鏅遍弫蹇斿妳娣団剝浼呴敍姘閺堝搫褰?闁喚顔?鐎靛棛鐖?Token/API Key"""
    if not text:
        return text
    # 閹靛婧€閸? 138****1234
    text = re.sub(r'(1[3-9]\d)\d{4}(\d{4})', r'\1****\2', text)
    # 闁喚顔? a***@example.com
    text = re.sub(r'(\w)[^@]*(@\w+\.\w+)', r'\1***\2', text)
    # Token/Key: 娣囨繄鏆€閸?閸?
    text = re.sub(r'(sk-[a-zA-Z0-9]{5})[a-zA-Z0-9]+([a-zA-Z0-9]{4})', r'\1****\2', text)
    text = re.sub(r'(eyJ[a-zA-Z0-9]{10})[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)', r'\1****\2', text)
    # 鐎靛棛鐖滅€涙顔?    text = re.sub(r'"(password|secret|token|key)"\s*:\s*"[^"]+"', r'"\1":"****"', text, flags=re.IGNORECASE)
    return text


# ===== 閸欐ɑ娲挎０鍕潔 =====
def diff_text(old: str, new: str, context: int = 3) -> dict:
    """閻㈢喐鍨氶弬鍥ㄦ拱閸欐ɑ娲挎０鍕潔閿涘牏鐣濋弰鎻筰ff閿?""
    if old == new:
        return {"has_diff": False, "diff": "閺冪姴褰夐弴?}

    old_lines = old.split("\n")
    new_lines = new.split("\n")

    added = []
    removed = []
    for i, line in enumerate(new_lines):
        if i >= len(old_lines) or old_lines[i] != line:
            added.append({"line": i + 1, "content": line})
    for i, line in enumerate(old_lines):
        if i >= len(new_lines) or new_lines[i] != line:
            removed.append({"line": i + 1, "content": line})

    return {
        "has_diff": True,
        "old_length": len(old),
        "new_length": len(new),
        "added": len(added),
        "removed": len(removed),
        "added_lines": added[:10],
        "removed_lines": removed[:10],
    }


# ===== 濡剝瀚欓悽銊﹀煕濞村鐦?=====
class SimulatedUser:
    """濡剝瀚欓悽銊﹀煕濞村繗顫嶅ù瀣槸"""

    @staticmethod
    def generate_session() -> dict:
        """閻㈢喐鍨氬Ο鈩冨珯閻劍鍩涙导姘崇樈"""
        import random
        from datetime import timedelta
        pages = ["/", "/products", "/categories", "/cart", "/login", "/register"]
        return {
            "session_id": f"sim_{int(__import__('time').time())}",
            "pages_visited": random.choices(pages, k=random.randint(2, 5)),
            "duration_s": random.randint(10, 120),
            "user_agent": "Mozilla/5.0 (Simulated Agent Bot/1.0)",
        }
