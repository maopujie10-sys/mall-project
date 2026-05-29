"""Memory Sync Engine — 跨设备/跨AI记忆同步
通过Git仓库同步FRIDAY.md + memory/目录，实现电脑和服务器AI共享记忆"""

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
    """记忆同步引擎"""

    @staticmethod
    def _run_git(args: list, timeout: int = 15) -> tuple:
        """执行git命令"""
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
        """识别当前运行环境：local（电脑）或 server（服务器）"""
        hostname = os.uname().nodename if hasattr(os, "uname") else os.getenv("COMPUTERNAME", "unknown")
        if any(kw in hostname.lower() for kw in ["server", "vps", "cloud", "ecs", "prod"]):
            return "server"
        return "local"

    @staticmethod
    def generate_friday_md() -> str:
        """生成FRIDAY.md — AI自我描述文档"""
        identity = MemorySync.identify_self()
        emoji = "💻" if identity == "local" else "🖥️"

        content = f"""# {emoji} Friday AI OS — 数字生命体档案

> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')} | 运行环境: {identity}

## 🧬 AI人格画像

"""
        # 如果人格引擎可用
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
            content += f"\n*(人格引擎暂不可用: {e})*\n"

        content += f"""
## 📋 最近上下文

"""
        # 添加上下文记忆
        try:
            from tools.memory_personality import PersonalityEngine
            context = PersonalityEngine.get_context()
            for item in context[:10]:
                content += f"- [{item['category']}] **{item['key']}**: {item['value'][:200]}\n"
        except Exception:
            content += "*(暂无上下文记忆)*\n"

        content += f"""
## 📝 最近日记

"""
        try:
            from tools.memory_personality import PersonalityEngine
            journals = PersonalityEngine.get_journal_history(3)
            for j in journals:
                content += f"- **{j['date']}** {j.get('mood','')} — {j.get('summary','')[:150] if j.get('summary') else ''}\n"
        except Exception:
            content += "*(暂无日记)*\n"

        content += f"""
## 🔄 同步说明

- 本文件由 AI 自动生成和维护
- 电脑端写入 `FRIDAY.md`，服务器端写入 `FRIDAY_SERVER.md`
- git push/pull 后双方可见对方记忆
- `memory/` 目录存放详细日记和交接文档

---
*Friday AI OS v3.0 · 超级AI数字生命体*
"""
        return content

    @staticmethod
    def export_memory_files() -> dict:
        """导出memory/目录下的Markdown文件"""
        MEMORY_DIR.mkdir(exist_ok=True)
        files_created = []

        # 导出最新日记
        try:
            from tools.memory_personality import PersonalityEngine
            journals = PersonalityEngine.get_journal_history(7)
            for j in journals:
                filename = f"daily-{j['date']}.md"
                filepath = MEMORY_DIR / filename
                md = f"# 📝 Friday AI 日记 — {j['date']}\n\n"
                md += f"心情: {j.get('mood', '😐')}\n\n"
                md += f"## 摘要\n{j.get('summary', '')}\n\n"
                if j.get('highlights'):
                    md += "## 亮点\n"
                    for h in json.loads(j['highlights']) if isinstance(j['highlights'], str) else j['highlights']:
                        md += f"- {h}\n"
                if j.get('learnings'):
                    md += "## 学到的\n"
                    for l in json.loads(j['learnings']) if isinstance(j['learnings'], str) else j['learnings']:
                        md += f"- {l}\n"
                filepath.write_text(md, encoding="utf-8")
                files_created.append(str(filepath.relative_to(ROOT)))
        except Exception as e:
            pass

        # 导出HANDOFF
        try:
            from tools.memory_personality import PersonalityEngine
            handoff = PersonalityEngine.generate_handoff()
            filepath = MEMORY_DIR / "handoff.md"
            md = "# 🤝 AI HANDOFF 交接文档\n\n"
            md += f"生成时间: {handoff.get('generated_at', '')}\n\n"
            md += "## 人格状态\n"
            p = handoff.get('personality', {})
            md += f"- 类型: {p.get('type', '')}\n"
            md += f"- 阶段: {p.get('stage', '')}\n\n"
            md += "## 关键上下文\n"
            for ctx in handoff.get('key_context', []):
                md += f"- [{ctx['category']}] {ctx['key']}: {ctx['value'][:150]}\n"
            md += "\n## 下一步建议\n"
            for step in handoff.get('next_steps', []):
                md += f"- {step}\n"
            filepath.write_text(md, encoding="utf-8")
            files_created.append(str(filepath.relative_to(ROOT)))
        except Exception:
            pass

        return {"files": files_created, "count": len(files_created)}

    @staticmethod
    def sync_push() -> dict:
        """推送到GitHub — 共享记忆给另一端的AI"""
        identity = MemorySync.identify_self()

        # 生成文档
        friday_content = MemorySync.generate_friday_md()
        target_file = FRIDAY_LOCAL if identity == "local" else FRIDAY_SERVER
        target_file.write_text(friday_content, encoding="utf-8")

        # 导出memory
        export_result = MemorySync.export_memory_files()

        # Git操作
        results = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # git add
        ok, out, err = MemorySync._run_git(["add", "FRIDAY.md", "FRIDAY_SERVER.md", "memory/"])
        results.append({"step": "add", "ok": ok, "detail": out or err})

        # git commit
        if ok:
            msg = f"[Friday AI {identity}] 记忆同步 — {timestamp}"
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
        """从GitHub拉取 — 获取另一端AI的最新记忆"""
        # git pull
        ok, out, err = MemorySync._run_git(["pull", "origin", "HEAD"], timeout=30)

        result = {"step": "pull", "ok": ok, "detail": out or err}

        # 读取另一端FRIDAY
        identity = MemorySync.identify_self()
        other_file = FRIDAY_SERVER if identity == "local" else FRIDAY_LOCAL
        other_memory = ""
        if other_file.exists():
            other_memory = other_file.read_text(encoding="utf-8")[:2000]

        # 读取memory目录
        memory_files = []
        if MEMORY_DIR.exists():
            for f in MEMORY_DIR.glob("*.md"):
                memory_files.append({
                    "name": f.name,
                    "size": f.stat().st_size,
                    "preview": f.read_text(encoding="utf-8")[:300] if f.stat().st_size < 10000 else "(文件较大)"
                })

        return {
            "ok": ok,
            "identity": identity,
            "other_identity": "server" if identity == "local" else "local",
            "other_friday_preview": other_memory[:500] if other_memory else "(对方还没有FRIDAY文件)",
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