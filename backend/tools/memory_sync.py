"""Memory Sync Engine -- 璺ㄨ澶?璺ˋI璁板繂鍚屾
閫氳繃Git浠撳簱鍚屾FRIDAY.md + memory/鐩綍,瀹炵幇鐢佃剳鍜屾湇鍔″櫒AI鍏变韩璁板繂"""

import os
import json
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path

ROOT = Path(os.getenv('PROJECT_ROOT', Path(__file__).resolve().parent.parent.parent))
MEMORY_DIR = ROOT / "memory"
FRIDAY_LOCAL = ROOT / "FRIDAY.md"
FRIDAY_SERVER = ROOT / "FRIDAY_SERVER.md"

class MemorySync:
    """璁板繂鍚屾寮曟搸"""

    @classmethod
    def push_to_wechat(cls, message: str) -> dict:
        """推送记忆到微信"""
        try:
            import os, httpx
            token = os.getenv("WECHAT_TOKEN","")
            if not token: return {"ok":False,"error":"未配置WECHAT_TOKEN"}
            resp = httpx.post(f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={token}", json={"touser":"admin","msgtype":"text","text":{"content":f"[Friday记忆] {message[:500]}"}}, timeout=10)
            return {"ok":resp.status_code==200,"platform":"wechat"}
        except Exception as e: return {"ok":False,"error":str(e)}

    @classmethod
    def push_to_telegram(cls, message: str) -> dict:
        """推送记忆到Telegram"""
        try:
            import os, httpx
            token = os.getenv("TELEGRAM_BOT_TOKEN","")
            if not token: return {"ok":False,"error":"未配置TELEGRAM_BOT_TOKEN"}
            resp = httpx.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":os.getenv("TELEGRAM_CHAT_ID",""),"text":f"[Friday记忆] {message[:1000]}"}, timeout=10)
            return {"ok":resp.status_code==200,"platform":"telegram"}
        except Exception as e: return {"ok":False,"error":str(e)}

    @classmethod
    def sync_all_platforms(cls, message: str) -> dict:
        """同步到所有平台"""
        results = {}
        results["wechat"] = cls.push_to_wechat(message)
        results["telegram"] = cls.push_to_telegram(message)
        results["local"] = cls.sync_push({"message":message,"timestamp":__import__("time").time()})
        return {"ok":True,"results":results}

    @staticmethod
    def _run_git(args: list, timeout: int = 15) -> tuple:
        """鎵цgit鍛戒护"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)

    @staticmethod
    def identify_self() -> str:
        """璇嗗埆褰撳墠杩愯鐜:local(鐢佃剳)鎴?server(鏈嶅姟鍣?"""
        hostname = os.uname().nodename if hasattr(os, "uname") else os.getenv("COMPUTERNAME", "unknown")
        if any(kw in hostname.lower() for kw in ["server", "vps", "cloud", "ecs", "prod"]):
            return "server"
        return "local"

    @staticmethod
    def generate_friday_md() -> str:
        """生成FRIDAY.md -- AI自我描述文档"""
        identity = MemorySync.identify_self()
        emoji = "💻" if identity == "local" else "🖥️"

        content = f"""# {emoji} Friday AI OS -- 数字生命体档案

> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')} | 运行环境: {identity}

## 🧬 AI人格画像

"""
        # 濡傛灉浜烘牸寮曟搸鍙敤
        try:
            from tools.memory_personality import PersonalityEngine
            personality = PersonalityEngine.get_personality()
            content += f"- **人格类型**: {personality.get('personality_type', '萌芽期')}\n"
            content += f"- **主导特质**: {personality.get('dominant_name', '')}\n"
            content += f"- **进化阶段**: {personality.get('evolution_stage', '🌱 萌芽期')}\n"
            content += f"- **交互次数**: {personality.get('total_interactions', 0)}\n"
            content += f"- **近7日活跃**: {personality.get('recent_7d_interactions', 0)}次\n"

            if personality.get('traits'):
                content += "\n### 人格维度\n\n"
                for key, info in sorted(personality['traits'].items(), key=lambda x: x[1]['value'], reverse=True):
                    bar = "█" * int(info['value'] * 20) + "░" * (20 - int(info['value'] * 20))
                    content += f"- {info['icon']} **{info['name']}**: {bar} {info['value']:.0%}\n"
        except Exception as e:
            content += f"\n*(浜烘牸寮曟搸鏆備笉鍙敤: {e})*\n"

        content += f"""
## 馃搵 鏈€杩戜笂涓嬫枃

"""
        # 娣诲姞涓婁笅鏂囪蹇?
        try:
            from tools.memory_personality import PersonalityEngine
            context = PersonalityEngine.get_context()
            for item in context[:10]:
                content += f"- [{item['category']}] **{item['key']}**: {item['value'][:200]}\n"
        except Exception:
            content += "*(鏆傛棤涓婁笅鏂囪蹇?*\n"

        content += f"""
## 馃摑 鏈€杩戞棩璁?

"""
        try:
            from tools.memory_personality import PersonalityEngine
            journals = PersonalityEngine.get_journal_history(3)
            for j in journals:
                content += f"- **{j['date']}** {j.get('mood','')} -- {j.get('summary','')[:150] if j.get('summary') else ''}\n"
        except Exception:
            content += "*(鏆傛棤鏃ヨ)*\n"

        content += f"""
## 馃攧 鍚屾璇存槑

- 鏈枃浠剁敱 AI 鑷姩鐢熸垚鍜岀淮鎶?
- 鐢佃剳绔啓鍏?`FRIDAY.md`,鏈嶅姟鍣ㄧ鍐欏叆 `FRIDAY_SERVER.md`
- git push/pull 鍚庡弻鏂瑰彲瑙佸鏂硅蹇?
- `memory/` 鐩綍瀛樻斁璇︾粏鏃ヨ鍜屼氦鎺ユ枃妗?

---
*Friday AI OS v3.0 - 瓒呯骇AI鏁板瓧鐢熷懡浣?
"""
        return content

    @staticmethod
    def export_memory_files() -> dict:
        """瀵煎嚭memory/鐩綍涓嬬殑Markdown鏂囦欢"""
        MEMORY_DIR.mkdir(exist_ok=True)
        files_created = []

        # 瀵煎嚭鏈€鏂版棩璁?
        try:
            from tools.memory_personality import PersonalityEngine
            journals = PersonalityEngine.get_journal_history(7)
            for j in journals:
                filename = f"daily-{j['date']}.md"
                filepath = MEMORY_DIR / filename
                md = f"# 馃摑 Friday AI 鏃ヨ -- {j['date']}\n\n"
                md += f"蹇冩儏: {j.get('mood', '馃槓')}\n\n"
                md += f"## 鎽樿\n{j.get('summary', '')}\n\n"
                if j.get('highlights'):
                    md += "## 浜偣\n"
                    for h in json.loads(j['highlights']) if isinstance(j['highlights'], str) else j['highlights']:
                        md += f"- {h}\n"
                if j.get('learnings'):
                    md += "## 瀛﹀埌鐨刓n"
                    for l in json.loads(j['learnings']) if isinstance(j['learnings'], str) else j['learnings']:
                        md += f"- {l}\n"
                filepath.write_text(md, encoding="utf-8")
                files_created.append(str(filepath.relative_to(ROOT)))
        except Exception as e:
            pass

        # 瀵煎嚭HANDOFF
        try:
            from tools.memory_personality import PersonalityEngine
            handoff = PersonalityEngine.generate_handoff()
            filepath = MEMORY_DIR / "handoff.md"
            md = "# 馃 AI HANDOFF 浜ゆ帴鏂囨。\n\n"
            md += f"鐢熸垚鏃堕棿: {handoff.get('generated_at', '')}\n\n"
            md += "## 浜烘牸鐘舵€乗n"
            p = handoff.get('personality', {})
            md += f"- 绫诲瀷: {p.get('type', '')}\n"
            md += f"- 闃舵: {p.get('stage', '')}\n\n"
            md += "## 鍏抽敭涓婁笅鏂嘰n"
            for ctx in handoff.get('key_context', []):
                md += f"- [{ctx['category']}] {ctx['key']}: {ctx['value'][:150]}\n"
            md += "\n## 涓嬩竴姝ュ缓璁甛n"
            for step in handoff.get('next_steps', []):
                md += f"- {step}\n"
            filepath.write_text(md, encoding="utf-8")
            files_created.append(str(filepath.relative_to(ROOT)))
        except Exception:
            pass

        return {"files": files_created, "count": len(files_created)}

    @staticmethod
    def sync_push() -> dict:
        """鎺ㄩ€佸埌GitHub -- 鍏变韩璁板繂缁欏彟涓€绔殑AI"""
        identity = MemorySync.identify_self()

        # 鐢熸垚鏂囨。
        friday_content = MemorySync.generate_friday_md()
        target_file = FRIDAY_LOCAL if identity == "local" else FRIDAY_SERVER
        target_file.write_text(friday_content, encoding="utf-8")

        # 瀵煎嚭memory
        export_result = MemorySync.export_memory_files()

        # Git鎿嶄綔
        results = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # git add
        ok, out, err = MemorySync._run_git(["add", "FRIDAY.md", "FRIDAY_SERVER.md", "memory/"])
        results.append({"step": "add", "ok": ok, "detail": out or err})

        # git commit
        if ok:
            msg = f"[Friday AI {identity}] 璁板繂鍚屾 -- {timestamp}"
            ok, out, err = MemorySync._run_git(["commit", "-m", msg, "--allow-empty"])
            results.append({"step": "commit", "ok": ok, "detail": out or err})

        # git push
        if ok:
            ok, out, err = MemorySync._run_git(["push", "origin", "HEAD"], timeout=30)
            results.append({"step": "push", "ok": ok, "detail": out or err})

        return {
            "identity": identity,
            "timestamp": timestamp,
            "exported_files": export_result.get("files", []),
            "git_results": results,
            "success": all(r["ok"] for r in results),
        }

    @staticmethod
    def sync_pull() -> dict:
        """从GitHub拉取 -- 获取另一端AI的最新记忆"""
        # git pull
        ok, out, err = MemorySync._run_git(["pull", "origin", "HEAD"], timeout=30)

        result = {"step": "pull", "ok": ok, "detail": out or err}

        # 璇诲彇鍙︿竴绔疐RIDAY
        identity = MemorySync.identify_self()
        other_file = FRIDAY_SERVER if identity == "local" else FRIDAY_LOCAL
        other_memory = ""
        if other_file.exists():
            other_memory = other_file.read_text(encoding="utf-8")[:2000]

        # 璇诲彇memory鐩綍
        memory_files = []
        if MEMORY_DIR.exists():
            for f in MEMORY_DIR.glob("*.md"):
                memory_files.append({
                    "name": f.name,
                    "size": f.stat().st_size,
                    "preview": f.read_text(encoding="utf-8")[:300] if f.stat().st_size < 10000 else "(鏂囦欢杈冨ぇ)"
                })

        return {
            "ok": ok,
            "identity": identity,
            "other_identity": "server" if identity == "local" else "local",
            "other_friday_preview": other_memory[:500] if other_memory else "(瀵规柟杩樻病鏈塅RIDAY鏂囦欢)",
            "memory_files": memory_files,
            "git_result": result,
        }


def _save_sync():
    from tools.memory_store import memory_store
    import json
    try:
        data = {"last_push": getattr(MemorySync,"_last_push",0), "last_pull": getattr(MemorySync,"_last_pull",0)}
        memory_store.set_knowledge("memory_sync_state", "", json.dumps(data))
    except: pass
def _load_sync():
    from tools.memory_store import memory_store
    import json
    try:
        raw = memory_store.get_knowledge("memory_sync_state")
        if raw and isinstance(raw,list) and raw:
            d = json.loads(raw[0][2] if isinstance(raw[0],tuple) else str(raw[0]))
            MemorySync._last_push = d.get("last_push",0)
            MemorySync._last_pull = d.get("last_pull",0)
    except: pass
try: _load_sync()
except: pass
