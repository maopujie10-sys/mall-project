"""变更预览 — 修改前后 diff 对比

用于审批中心展示修改前后的差异。
支持文本 diff、JSON diff、配置 diff。
"""
import difflib
import json
from typing import Optional


def text_diff(before: str, after: str, context_lines: int = 3) -> str:
    """生成文本差异对比（unified diff 格式）"""
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    diff = difflib.unified_diff(
        before_lines, after_lines,
        fromfile="修改前", tofile="修改后",
        n=context_lines
    )
    return "".join(diff)


def json_diff(before: dict, after: dict) -> dict:
    """对比两个 JSON 对象，返回变更字段列表"""
    changes = []
    all_keys = set(before.keys()) | set(after.keys())
    for key in sorted(all_keys):
        old_val = before.get(key, "(不存在)")
        new_val = after.get(key, "(不存在)")
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
    """生成变更预览数据，供审批中心展示"""
    changes = json_diff(before, after)
    return {
        "action": action_name,
        "risk": risk_level,
        "before": {k: str(v)[:100] for k, v in before.items()},
        "after": {k: str(v)[:100] for k, v in after.items()},
        "changes": changes["changes"],
        "change_count": changes["count"],
        "summary": f"共 {changes['count']} 个字段发生变化",
    }
