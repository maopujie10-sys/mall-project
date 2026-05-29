"""鍙樻洿棰勮 鈥?淇敼鍓嶅悗 diff 瀵规瘮

鐢ㄤ簬瀹℃壒涓績灞曠ず淇敼鍓嶅悗鐨勫樊寮傘€?鏀寔鏂囨湰 diff銆丣SON diff銆侀厤缃?diff銆?"""
import difflib
import json
from typing import Optional


def text_diff(before: str, after: str, context_lines: int = 3) -> str:
    """鐢熸垚鏂囨湰宸紓瀵规瘮锛坲nified diff 鏍煎紡锛?""
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    diff = difflib.unified_diff(
        before_lines, after_lines,
        fromfile="淇敼鍓?, tofile="淇敼鍚?,
        n=context_lines
    )
    return "".join(diff)


def json_diff(before: dict, after: dict) -> dict:
    """瀵规瘮涓や釜 JSON 瀵硅薄锛岃繑鍥炲彉鏇村瓧娈靛垪琛?""
    changes = []
    all_keys = set(before.keys()) | set(after.keys())
    for key in sorted(all_keys):
        old_val = before.get(key, "(涓嶅瓨鍦?")
        new_val = after.get(key, "(涓嶅瓨鍦?")
        if old_val != new_val:
            changes.append({
                "field": key,
                "before": str(old_val)[:200],
                "after": str(new_val)[:200],
            })
    return {"changes": changes, "count": len(changes)}


def generate_diff_preview(
    action_name: str,
    before: dict,
    after: dict,
    risk_level: str = "L3"
) -> dict:
    """鐢熸垚鍙樻洿棰勮鏁版嵁锛屼緵瀹℃壒涓績灞曠ず"""
    changes = json_diff(before, after)
    return {
        "action": action_name,
        "risk": risk_level,
        "before": {k: str(v)[:100] for k, v in before.items()},
        "after": {k: str(v)[:100] for k, v in after.items()},
        "changes": changes["changes"],
        "change_count": changes["count"],
        "summary": f"鍏?{changes['count']} 涓瓧娈靛彂鐢熷彉鍖?,
    }
