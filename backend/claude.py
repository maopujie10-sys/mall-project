''"Claude API  -- ''"
import httpx
import json
from typing import Optional
from config import CLAUDE_API_KEY, CLAUDE_MODEL

# ===== Claude  Prompt(V5 14)=====
SYSTEM_PROMPT = ''" Claude Agent ..


1. 
2. (L1/L2/L3/L4)
3. (L1)
4. (L3)
5. (L4)
6. 
7. 
8. 
9. 
10. 
11. 
12.  SQL
13. 


{available_tools}


 JSON :
{
    "intent": '',
    "risk_level": "L1/L2/L3/L4",
    "tool": '',
    "steps": [{"step": 1, "action": "..."}],
    "response": '',
    "need_confirm": false,
    "evidence": ''
}''"

async def chat(message: str, available_tools: str = '') -> dict:
    ''" Claude API ''"
    if not CLAUDE_API_KEY:
        return {
            "intent": "unknown",
            "risk_level": "L1",
            "tool": '',
            "steps": [],
            "response": f": {message[:50]}...\nClaude API Key ,",
            "need_confirm": False,
            "evidence": '',
        }

    prompt = SYSTEM_PROMPT.format(available_tools=available_tools or '')

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
                    #  JSON 
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except (json.JSONDecodeError, KeyError):
                    pass
                return {
                    "intent": "parsed",
                    "risk_level": "L1",
                    "tool": '',
                    "steps": [{"step": 1, "action": ''}],
                    "response": content,
                    "need_confirm": False,
                    "evidence": '',
                }
            return {
                "intent": "error",
                "risk_level": "L1",
                "tool": '',
                "steps": [],
                "response": f"Claude API : {r.status_code}",
                "need_confirm": False,
                "evidence": '',
            }
    except Exception as e:
        return {
            "intent": "error",
            "risk_level": "L1",
            "tool": '',
            "steps": [],
            "response": f"Claude API : {str(e)}",
            "need_confirm": False,
            "evidence": '',
        }
