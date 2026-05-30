''" +  -- ''"
import re

# =====  =====
def mask_sensitive(text: str) -> str:
    ''":///Token/API Key''"
    if not text:
        return text
    # : 138****1234
    text = re.sub(r'(1[3-9]\d)\d{4}(\d{4})', r'\1****\2', text)
    # : a***@example.com
    text = re.sub(r'(\w)[^@]*(@\w+\.\w+)', r'\1***\2', text)
    # Token/Key: 44
    text = re.sub(r'(sk-[a-zA-Z0-9]{5})[a-zA-Z0-9]+([a-zA-Z0-9]{4})', r'\1****\2', text)
    text = re.sub(r'(eyJ[a-zA-Z0-9]{10})[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)', r'\1****\2', text)
    
    text = re.sub(r''(password|secret|token|key)"\s*:\s*"[^"]+'', r''\1":"****'', text, flags=re.IGNORECASE)
    return text


# =====  =====
def diff_text(old: str, new: str, context: int = 3) -> dict:
    ''"(diff)''"
    if old == new:
        return {"has_diff": False, "diff": ''}

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


# =====  =====
class SimulatedUser:
    ''''''

    @staticmethod
    def generate_session() -> dict:
        ''''''
        import random
        from datetime import timedelta
        pages = ["/", "/products", "/categories", "/cart", "/login", "/register"]
        return {
            "session_id": f"sim_{int(__import__('time').time())}",
            "pages_visited": random.choices(pages, k=random.randint(2, 5)),
            "duration_s": random.randint(10, 120),
            "user_agent": "Mozilla/5.0 (Simulated Agent Bot/1.0)",
        }
