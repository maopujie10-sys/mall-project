"""AI 启动自检 + 长期记忆预热 — 启动即加载历史经验"""
import os
import json
from datetime import datetime
from tools.evolution import EvolutionEngine, _get_db

async def startup_self_check():
    """AI 启动时自动执行的自检流程"""
    print("[AI大脑] 🧠 启动自检中...")
    results = {}

    # 1. 内存检查
    try:
        db = _get_db()
        total_actions = db.execute("SELECT COUNT(*) FROM actions").fetchone()[0]
        total_learned = db.execute("SELECT COUNT(*) FROM learning").fetchone()[0]
        total_corrections = db.execute("SELECT COUNT(*) FROM corrections").fetchone()[0]
        db.close()
        results["memory"] = {
            "ok": True,
            "total_actions": total_actions,
            "knowledge_items": total_learned,
            "corrections": total_corrections,
            "status": "🧠 长期记忆在线" if total_actions > 0 else "📝 记忆库为空，等待首次使用",
        }
        print(f"[AI大脑] 记忆: {total_actions}条行动, {total_learned}条知识, {total_corrections}条纠正")
    except Exception as e:
        results["memory"] = {"ok": False, "error": str(e)}

    # 2. 成功率自检
    try:
        rate_30d = EvolutionEngine.get_success_rate(days=30)
        rate_7d = EvolutionEngine.get_success_rate(days=7)
        trend = "📈" if rate_7d > rate_30d else "📉" if rate_7d < rate_30d else "➡️"
        results["performance"] = {
            "ok": True,
            "success_rate_30d": rate_30d,
            "success_rate_7d": rate_7d,
            "trend": f"{trend} {'提升中' if rate_7d > rate_30d else '需关注' if rate_7d < rate_30d else '稳定'}",
        }
        print(f"[AI大脑] 成功率: 30天={rate_30d}%, 7天={rate_7d}% {trend}")
    except Exception as e:
        results["performance"] = {"ok": False, "error": str(e)}

    # 3. 未学习的纠正
    try:
        pending = EvolutionEngine.get_corrections(learned=0)
        results["pending_learning"] = {
            "ok": True,
            "count": len(pending),
            "items": pending[:5],
        }
        if pending:
            print(f"[AI大脑] ⚠️ {len(pending)}条用户纠正待学习")
        else:
            print(f"[AI大脑] ✅ 所有纠正已消化")
    except Exception as e:
        results["pending_learning"] = {"ok": False, "error": str(e)}

    # 4. 进化建议
    try:
        report = EvolutionEngine.evolve_report()
        results["evolution_suggestions"] = report.get("suggestions", [])[:3]
    except Exception:
        results["evolution_suggestions"] = []

    
    # 5. Git记忆同步 — 拉取另一端AI的记忆
    try:
        from tools.memory_sync import MemorySync
        sync_result = MemorySync.sync_pull()
        results["memory_sync"] = {
            "ok": sync_result["ok"],
            "other_identity": sync_result.get("other_identity", "unknown"),
            "other_friday": sync_result.get("other_friday_preview", "")[:100],
        }
        if sync_result["ok"]:
            print(f"[AI大脑] 🔄 已同步{sync_result.get('other_identity')}的记忆")
        else:
            print(f"[AI大脑] ⚠️ 记忆同步跳过: {sync_result.get('git_result',{}).get('detail','')}")
    except Exception as e:
        results["memory_sync"] = {"ok": False, "error": str(e)}

    all_ok = all(v.get("ok", True) for v in results.values() if isinstance(v, dict))
    summary = "✅ AI大脑启动完成，全系统正常" if all_ok else "⚠️ AI大脑启动完成，部分模块需关注"

    print(f"[AI大脑] {summary}")
    return {"ok": all_ok, "summary": summary, "details": results, "started_at": datetime.now().isoformat()}

async def startup_warmup():
    """启动预热 — 加载历史经验到工作记忆"""
    print("[AI大脑] 🔥 加载历史经验...")
    knowledge = {}
    try:
        db = _get_db()
        # 加载高价值知识
        rows = db.execute("SELECT category, key, value, score FROM learning WHERE score > 0.5 ORDER BY score DESC LIMIT 50").fetchall()
        for r in rows:
            cat = r["category"]
            if cat not in knowledge:
                knowledge[cat] = []
            knowledge[cat].append({"key": r["key"], "value": r["value"], "score": r["score"]})

        # 加载最佳策略
        best_scraper = db.execute("SELECT key, score FROM learning WHERE category='scraper_sources' ORDER BY score DESC LIMIT 5").fetchall()
        knowledge["_best_scraper_sources"] = [{"source": r["key"], "score": r["score"]} for r in best_scraper]

        db.close()
        print(f"[AI大脑] 已加载 {len(knowledge)}个领域的知识")
    except Exception as e:
        print(f"[AI大脑] 预热加载失败: {e}")

    return {"knowledge_categories": len(knowledge), "loaded": True}

# 启动时自动注册的事件
def register_startup_events():
    """注册所有启动钩子"""
    return {
        "self_check": startup_self_check,
        "warmup": startup_warmup,
    }
