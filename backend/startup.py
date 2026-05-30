''"AI  +  -- ''"
import os
import json
from datetime import datetime
from tools.evolution import EvolutionEngine, _get_db

async def startup_self_check():
    ''"AI ''"
    print("[AI]  ...")
    results = {}

    # 1. 
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
            "status": " " if total_actions > 0 else " ,",
        }
        print(f"[AI] : {total_actions}, {total_learned}, {total_corrections}")
    except Exception as e:
        results["memory"] = {"ok": False, "error": str(e)}

    # 2. 
    try:
        rate_30d = EvolutionEngine.get_success_rate(days=30)
        rate_7d = EvolutionEngine.get_success_rate(days=7)
        trend = "" if rate_7d > rate_30d else "" if rate_7d < rate_30d else ""
        results["performance"] = {
            "ok": True,
            "success_rate_30d": rate_30d,
            "success_rate_7d": rate_7d,
            "trend": f"{trend} {'' if rate_7d > rate_30d else '' if rate_7d < rate_30d else ''}",
        }
        print(f"[AI] : 30={rate_30d}%, 7={rate_7d}% {trend}")
    except Exception as e:
        results["performance"] = {"ok": False, "error": str(e)}

    # 3. 
    try:
        pending = EvolutionEngine.get_corrections(learned=0)
        results["pending_learning"] = {
            "ok": True,
            "count": len(pending),
            "items": pending[:5],
        }
        if pending:
            print(f"[AI]  {len(pending)}")
        else:
            print(f"[AI]  ")
    except Exception as e:
        results["pending_learning"] = {"ok": False, "error": str(e)}

    # 4. 
    try:
        report = EvolutionEngine.evolve_report()
        results["evolution_suggestions"] = report.get("suggestions", [])[:3]
    except Exception:
        results["evolution_suggestions"] = []

    
    # 5. Git -- AI
    try:
        from tools.memory_sync import MemorySync
        sync_result = MemorySync.sync_pull()
        results["memory_sync"] = {
            "ok": sync_result["ok"],
            "other_identity": sync_result.get("other_identity", "unknown"),
            "other_friday": sync_result.get("other_friday_preview", '')[:100],
        }
        if sync_result["ok"]:
            print(f"[AI]  {sync_result.get('other_identity')}")
        else:
            print(f"[AI]  : {sync_result.get('git_result',{}).get('detail','')}")
    except Exception as e:
        results["memory_sync"] = {"ok": False, "error": str(e)}

    all_ok = all(v.get("ok", True) for v in results.values() if isinstance(v, dict))
    summary = " AI," if all_ok else " AI,"

    print(f"[AI] {summary}")
    return {"ok": all_ok, "summary": summary, "details": results, "started_at": datetime.now().isoformat()}

async def startup_warmup():
    ''" -- ''"
    print("[AI]  ...")
    knowledge = {}
    try:
        db = _get_db()
        
        rows = db.execute("SELECT category, key, value, score FROM learning WHERE score > 0.5 ORDER BY score DESC LIMIT 50").fetchall()
        for r in rows:
            cat = r["category"]
            if cat not in knowledge:
                knowledge[cat] = []
            knowledge[cat].append({"key": r["key"], "value": r["value"], "score": r["score"]})

        
        best_scraper = db.execute("SELECT key, score FROM learning WHERE category='scraper_sources' ORDER BY score DESC LIMIT 5").fetchall()
        knowledge["_best_scraper_sources"] = [{"source": r["key"], "score": r["score"]} for r in best_scraper]

        db.close()
        print(f"[AI]  {len(knowledge)}")
    except Exception as e:
        print(f"[AI] : {e}")

    return {"knowledge_categories": len(knowledge), "loaded": True}


def register_startup_events():
    ''''''
    return {
        "self_check": startup_self_check,
        "warmup": startup_warmup,
    }
