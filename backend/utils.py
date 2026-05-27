"""变更预览 + 数据脱敏 — 通用工具模块"""
import re

# ===== 数据脱敏 =====
def mask_sensitive(text: str) -> str:
    """脱敏敏感信息：手机号/邮箱/密码/Token/API Key"""
    if not text:
        return text
    # 手机号: 138****1234
    text = re.sub(r'(1[3-9]\d)\d{4}(\d{4})', r'\1****\2', text)
    # 邮箱: a***@example.com
    text = re.sub(r'(\w)[^@]*(@\w+\.\w+)', r'\1***\2', text)
    # Token/Key: 保留前4后4
    text = re.sub(r'(sk-[a-zA-Z0-9]{5})[a-zA-Z0-9]+([a-zA-Z0-9]{4})', r'\1****\2', text)
    text = re.sub(r'(eyJ[a-zA-Z0-9]{10})[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)', r'\1****\2', text)
    # 密码字段
    text = re.sub(r'"(password|secret|token|key)"\s*:\s*"[^"]+"', r'"\1":"****"', text, flags=re.IGNORECASE)
    return text


# ===== 变更预览 =====
def diff_text(old: str, new: str, context: int = 3) -> dict:
    """生成文本变更预览（简易diff）"""
    if old == new:
        return {"has_diff": False, "diff": "无变更"}

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


# ===== 模拟用户测试 =====
class SimulatedUser:
    """模拟用户浏览测试"""

    @staticmethod
    def generate_session() -> dict:
        """生成模拟用户会话"""
        import random
        from datetime import timedelta
        pages = ["/", "/products", "/categories", "/cart", "/login", "/register"]
        return {
            "session_id": f"sim_{int(__import__('time').time())}",
            "pages_visited": random.choices(pages, k=random.randint(2, 5)),
            "duration_s": random.randint(10, 120),
            "user_agent": "Mozilla/5.0 (Simulated Agent Bot/1.0)",
        }
