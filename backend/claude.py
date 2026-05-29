"""Claude API 真实接入 — 替代关键词匹配"""
import httpx
import json
from typing import Optional
from config import CLAUDE_API_KEY, CLAUDE_MODEL

# ===== Claude 系统 Prompt（V5 文档第14节）=====
SYSTEM_PROMPT = """你是 Claude Agent 服务器商城总控系统的大脑。你不是普通聊天机器人。

## 核心规则
1. 你必须先判断用户任务意图
2. 你必须先判断风险等级（L1/L2/L3/L4）
3. 低风险任务（L1）可以自动执行
4. 中风险任务（L3）必须请求确认
5. 高风险任务（L4）必须人工接管
6. 任何删除、清空、覆盖、重装、支付、权限、余额、订单金额、管理员相关操作都禁止自动执行
7. 修改前必须备份
8. 执行后必须验证
9. 无法判断时必须停止并请求人工接管
10. 所有结论必须给出证据
11. 不得泄露敏感信息
12. 不得直接执行任意 SQL
13. 不得绕过工具系统

## 可用工具
{available_tools}

## 响应格式
你必须以 JSON 格式返回：
{
    "intent": "识别到的意图",
    "risk_level": "L1/L2/L3/L4",
    "tool": "要调用的工具名",
    "steps": [{"step": 1, "action": "..."}],
    "response": "给用户的回复",
    "need_confirm": false,
    "evidence": "判断依据"
}"""

async def chat(message: str, available_tools: str = "") -> dict:
    """调用 Claude API 理解用户意图"""
    if not CLAUDE_API_KEY:
        return {
            "intent": "unknown",
            "risk_level": "L1",
            "tool": "",
            "steps": [],
            "response": f"收到: {message[:50]}...\nClaude API Key 未配置，使用本地模式匹配",
            "need_confirm": False,
            "evidence": "",
        }

    prompt = SYSTEM_PROMPT.format(available_tools=available_tools or "请查看工具注册中心获取完整列表")

    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": CLAUDE_MODEL or "claude-3-5-sonnet-latest",
                    "max_tokens": 1024,
                    "system": prompt,
                    "messages": [{"role": "user", "content": message}],
                },
            )
            if r.status_code == 200:
                content = r.json()["content"][0]["text"]
                try:
                    # 尝试解析 JSON 响应
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except (json.JSONDecodeError, KeyError):
                    pass
                return {
                    "intent": "parsed",
                    "risk_level": "L1",
                    "tool": "",
                    "steps": [{"step": 1, "action": "分析完成"}],
                    "response": content,
                    "need_confirm": False,
                    "evidence": "",
                }
            return {
                "intent": "error",
                "risk_level": "L1",
                "tool": "",
                "steps": [],
                "response": f"Claude API 返回错误: {r.status_code}",
                "need_confirm": False,
                "evidence": "",
            }
    except Exception as e:
        return {
            "intent": "error",
            "risk_level": "L1",
            "tool": "",
            "steps": [],
            "response": f"Claude API 调用失败: {str(e)}",
            "need_confirm": False,
            "evidence": "",
        }
