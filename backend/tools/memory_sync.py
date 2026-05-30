"""Memory Sync Engine - Git-based FRIDAY.md sync"""

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
    ''"''"

    @classmethod
    def push_to_wechat(cls, message: str) -> dict:
        ''''''
        try:
            import os, httpx
            token = os.getenv("WECHAT_TOKEN",'')
            if not token: return {"ok":False,"error":"WECHAT_TOKEN"}
            resp = httpx.post(f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={token}", json={"touser":"admin","msgtype":"text","text":{"content":f"[Friday] {message[:500]}"}}, timeout=10)
            return {"ok":resp.status_code==200,"platform":"wechat"}
        except Exception as e: return {"ok":False,"error":str(e)}

    @classmethod
    def push_to_telegram(cls, message: str) -> dict:
        ''"Telegram''"
        try:
            import os, httpx
            token = os.getenv("TELEGRAM_BOT_TOKEN",'')
            if not token: return {"ok":False,"error":"TELEGRAM_BOT_TOKEN"}
            resp = httpx.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":os.getenv("TELEGRAM_CHAT_ID",''),"text":f"[Friday] {message[:1000]}"}, timeout=10)
            return {"ok":resp.status_code==200,"platform":"telegram"}
        except Exception as e: return {"ok":False,"error":str(e)}

    @classmethod
    def sync_all_platforms(cls, message: str) -> dict:
        ''''''
        results = {}
        results["wechat"] = cls.push_to_wechat(message)
        results["telegram"] = cls.push_to_telegram(message)
        results["local"] = cls.sync_push({"message":message,"timestamp":__import__("time").time()})
        return {"ok":True,"results":results}

    @staticmethod
    def _run_git(args: list, timeout: int = 15) -> tuple:
        ''"git''"
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
            return False, '', str(e)

    @staticmethod
    def identify_self() -> str:
        ''":local()?server(?''"
        hostname = os.uname().nodename if hasattr(os, "uname") else os.getenv("COMPUTERNAME", "unknown")
        if any(kw in hostname.lower() for kw in ["server", "vps", "cloud", "ecs", "prod"]):
            return "server"
        return "local"

    @staticmethod
    def generate_friday_md() -> str:
        ''"FRIDAY.md -- AI''"
        identity = MemorySync.identify_self()
        emoji = "" if identity == "local" else ""

        content = f''"# {emoji} Friday AI OS -- 

>  {datetime.now().strftime('%Y-%m-%d %H:%M')} | : {identity}

##  AI

''"
        
        try:
            from tools.memory_personality import PersonalityEngine
            personality = PersonalityEngine.get_personality()
            content += f"- ****: {personality.get('personality_type', '')}\n"
            content += f"- ****: {personality.get('dominant_name', '')}\n"
            content += f"- ****: {personality.get('evolution_stage', '')}\n"
            content += f"- ****: {personality.get('total_interactions', 0)}\n"
            content += f"- **7**: {personality.get('recent_7d_interactions', 0)}\n"

            if personality.get('traits'):
                content += "\n### \n\n"
                for key, info in sorted(personality['traits'].items(), key=lambda x: x[1]['value'], reverse=True):
                    bar = "" * int(info['value'] * 20) + "" * (20 - int(info['value'] * 20))
                    content += f"- {info['icon']} **{info['name']}**: {bar} {info['value']:.0%}\n"
        except Exception as e:
            content += f"\n*(: {e})*\n"

        content += f''"
#
''"
        # ?
        try:
            from tools.memory_personality import PersonalityEngine
            context = PersonalityEngine.get_context()
            for item in context[:10]:
                content += f"- [{item['category']}] **{item['key']}**: {item['value'][:200]}\n"
        except Exception:
            content += "*(?*\n"

        content += f''"
##  ?

''"
        try:
            from tools.memory_personality import PersonalityEngine
            journals = PersonalityEngine.get_journal_history(3)
            for j in journals:
                content += f"- **{j['date']}** {j.get('mood','')} -- {j.get('summary','')[:150] if j.get('summary') else ''}\n"
        except Exception:
            content += "*()*\n"

        content += f''"
#
-  AI ?
- ?'FRIDAY.md', 'FRIDAY_SERVER.md'
- git push/pull ?
- 'memory/' ?

---
*Friday AI OS v3.0 - AI?
''"
        return content

    @staticmethod
    def export_memory_files() -> dict:
        ''"memory/Markdown''"
        MEMORY_DIR.mkdir(exist_ok=True)
        files_created = []

        # ?
        try:
            from tools.memory_personality import PersonalityEngine
            journals = PersonalityEngine.get_journal_history(7)
            for j in journals:
                filename = f"daily-{j['date']}.md"
                filepath = MEMORY_DIR / filename
                md = f"#  Friday AI  -- {j['date']}\n\n"
                md += f": {j.get('mood', '')}\n\n"
                md += f"## \n{j.get('summary', '')}\n\n"
                if j.get('highlights'):
                    md += "## \n"
                    for h in json.loads(j['highlights']) if isinstance(j['highlights'], str) else j['highlights']:
                        md += f"- {h}\n"
                if j.get('learnings'):
                    md += "## n"
                    for l in json.loads(j['learnings']) if isinstance(j['learnings'], str) else j['learnings']:
                        md += f"- {l}\n"
                filepath.write_text(md, encoding="utf-8")
                files_created.append(str(filepath.relative_to(ROOT)))
        except Exception as e:
            pass

        # HANDOFF
        try:
            from tools.memory_personality import PersonalityEngine
            handoff = PersonalityEngine.generate_handoff()
            filepath = MEMORY_DIR / "handoff.md"
            md = "#  AI HANDOFF \n\n"
            md += f": {handoff.get('generated_at', '')}\n\n"
            md += "## n"
            p = handoff.get('personality', {})
            md += f"- : {p.get('type', '')}\n"
            md += f"- : {p.get('stage', '')}\n\n"
            md += "## n"
            for ctx in handoff.get('key_context', []):
                md += f"- [{ctx['category']}] {ctx['key']}: {ctx['value'][:150]}\n"
            md += "\n## n"
            for step in handoff.get('next_steps', []):
                md += f"- {step}\n"
            filepath.write_text(md, encoding="utf-8")
            files_created.append(str(filepath.relative_to(ROOT)))
        except Exception:
            pass

        return {"files": files_created, "count": len(files_created)}

    @staticmethod
    def sync_push() -> dict:
        ''"GitHub -- AI''"
        identity = MemorySync.identify_self()

        
        friday_content = MemorySync.generate_friday_md()
        target_file = FRIDAY_LOCAL if identity == "local" else FRIDAY_SERVER
        target_file.write_text(friday_content, encoding="utf-8")

        # memory
        export_result = MemorySync.export_memory_files()

        # Git
        results = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # git add
        ok, out, err = MemorySync._run_git(["add", "FRIDAY.md", "FRIDAY_SERVER.md", "memory/"])
        results.append({"step": "add", "ok": ok, "detail": out or err})

        # git commit
        if ok:
            msg = f"[Friday AI {identity}]  -- {timestamp}"
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
        ''"GitHub -- AI''"
        # git pull
        ok, out, err = MemorySync._run_git(["pull", "origin", "HEAD"], timeout=30)

        result = {"step": "pull", "ok": ok, "detail": out or err}

        # RIDAY
        identity = MemorySync.identify_self()
        other_file = FRIDAY_SERVER if identity == "local" else FRIDAY_LOCAL
        other_memory = ''
        if other_file.exists():
            other_memory = other_file.read_text(encoding="utf-8")[:2000]

        # memory
        memory_files = []
        if MEMORY_DIR.exists():
            for f in MEMORY_DIR.glob("*.md"):
                memory_files.append({
                    "name": f.name,
                    "size": f.stat().st_size,
                    "preview": f.read_text(encoding="utf-8")[:300] if f.stat().st_size < 10000 else "()"
                })

        return {
            "ok": ok,
            "identity": identity,
            "other_identity": "server" if identity == "local" else "local",
            "other_friday_preview": other_memory[:500] if other_memory else "(RIDAY)",
            "memory_files": memory_files,
            "git_result": result,
        }


def _save_sync():
    from tools.memory_store import memory_store
    import json
    try:
        data = {"last_push": getattr(MemorySync,"_last_push",0), "last_pull": getattr(MemorySync,"_last_pull",0)}
        memory_store.set_knowledge("memory_sync_state", '', json.dumps(data))
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
