閿?""Claude API 閻喎鐤勯幒銉ュ弳 閳?閺囧じ鍞崗鎶芥暛鐠囧秴灏柊?""
import httpx
import json
from typing import Optional
from config import CLAUDE_API_KEY, CLAUDE_MODEL

# ===== Claude 缁崵绮?Prompt閿涘湸5 閺傚洦銆傜粭?4閼哄偊绱?====
SYSTEM_PROMPT = """娴ｇ姵妲?Claude Agent 閺堝秴濮熼崳銊ユ櫌閸╁孩鈧粯甯剁化鑽ょ埠閻ㄥ嫬銇囬懘鎴欌偓鍌欑稑娑撳秵妲搁弲顕€鈧俺浜版径鈺傛簚閸ｃ劋姹夐妴?
## 閺嶇绺剧憴鍕灟
1. 娴ｇ姴绻€妞よ鍘涢崚銈嗘焽閻劍鍩涙禒璇插閹板繐娴?2. 娴ｇ姴绻€妞よ鍘涢崚銈嗘焽妞嬪酣娅撶粵澶岄獓閿涘湢1/L2/L3/L4閿?3. 娴ｅ酣顥撻梽鈺€鎹㈤崝鈽呯礄L1閿涘褰叉禒銉ㄥ殰閸斻劍澧界悰?4. 娑擃參顥撻梽鈺€鎹㈤崝鈽呯礄L3閿涘绻€妞ゆ槒顕Ч鍌溾€樼拋?5. 妤傛﹢顥撻梽鈺€鎹㈤崝鈽呯礄L4閿涘绻€妞よ姹夊銉﹀复缁?6. 娴犺缍嶉崚鐘绘珟閵嗕焦绔荤粚鎭掆偓浣筋洬閻╂牓鈧線鍣哥憗鍛偓浣规暜娴犳ǜ鈧焦娼堥梽鎰┾偓浣风稇妫版縿鈧浇顓归崡鏇㈠櫨妫版縿鈧胶顓搁悶鍡楁喅閻╃鍙ч幙宥勭稊闁晫顩﹀銏ｅ殰閸斻劍澧界悰?7. 娣囶喗鏁奸崜宥呯箑妞よ顦禒?8. 閹笛嗩攽閸氬骸绻€妞ゅ鐛欑拠?9. 閺冪姵纭堕崚銈嗘焽閺冭泛绻€妞よ浠犲銏犺嫙鐠囬攱鐪版禍鍝勪紣閹恒儳顓?10. 閹碘偓閺堝绮ㄧ拋鍝勭箑妞よ崵绮伴崙楦跨槈閹?11. 娑撳秴绶卞▔鍕苟閺佸繑鍔呮穱鈩冧紖
12. 娑撳秴绶遍惄瀛樺复閹笛嗩攽娴犵粯鍓?SQL
13. 娑撳秴绶辩紒鏇＄箖瀹搞儱鍙跨化鑽ょ埠

## 閸欘垳鏁ゅ銉ュ徔
{available_tools}

## 閸濆秴绨查弽鐓庣础
娴ｇ姴绻€妞よ浜?JSON 閺嶇厧绱℃潻鏂挎礀閿?{
    "intent": "鐠囧棗鍩嗛崚鎵畱閹板繐娴?,
    "risk_level": "L1/L2/L3/L4",
    "tool": "鐟曚浇鐨熼悽銊ф畱瀹搞儱鍙块崥?,
    "steps": [{"step": 1, "action": "..."}],
    "response": "缂佹瑧鏁ら幋椋庢畱閸ョ偛顦?,
    "need_confirm": false,
    "evidence": "閸掋倖鏌囨笟婵囧祦"
}"""

async def chat(message: str, available_tools: str = "") -> dict:
    """鐠嬪啰鏁?Claude API 閻炲棜袙閻劍鍩涢幇蹇撴禈"""
    if not CLAUDE_API_KEY:
        return {
            "intent": "unknown",
            "risk_level": "L1",
            "tool": "",
            "steps": [],
            "response": f"閺€璺哄煂: {message[:50]}...\nClaude API Key 閺堫亪鍘ょ純顕嗙礉娴ｈ法鏁ら張顒€婀村Ο鈥崇础閸栧綊鍘?,
            "need_confirm": False,
            "evidence": "",
        }

    prompt = SYSTEM_PROMPT.format(available_tools=available_tools or "鐠囬攱鐓￠惇瀣紣閸忛攱鏁為崘灞艰厬韫囧啳骞忛崣鏍х暚閺佹潙鍨悰?)

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
                    # 鐏忔繆鐦憴锝嗙€?JSON 閸濆秴绨?                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except (json.JSONDecodeError, KeyError):
                    pass
                return {
                    "intent": "parsed",
                    "risk_level": "L1",
                    "tool": "",
                    "steps": [{"step": 1, "action": "閸掑棙鐎界€瑰本鍨?}],
                    "response": content,
                    "need_confirm": False,
                    "evidence": "",
                }
            return {
                "intent": "error",
                "risk_level": "L1",
                "tool": "",
                "steps": [],
                "response": f"Claude API 鏉╂柨娲栭柨娆掝嚖: {r.status_code}",
                "need_confirm": False,
                "evidence": "",
            }
    except Exception as e:
        return {
            "intent": "error",
            "risk_level": "L1",
            "tool": "",
            "steps": [],
            "response": f"Claude API 鐠嬪啰鏁ゆ径杈Е: {str(e)}",
            "need_confirm": False,
            "evidence": "",
        }
