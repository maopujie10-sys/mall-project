閿?""AI 閸氼垰濮╅懛顏咁梾 + 闂€鎸庢埂鐠佹澘绻傛０鍕劰 閳?閸氼垰濮╅崡鍐插鏉炶棄宸婚崣鑼病妤?""
import os
import json
from datetime import datetime
from tools.evolution import EvolutionEngine, _get_db

async def startup_self_check():
    """AI 閸氼垰濮╅弮鎯板殰閸斻劍澧界悰宀€娈戦懛顏咁梾濞翠胶鈻?""
    print("[AI婢堆嗗壋] 棣冾潵 閸氼垰濮╅懛顏咁梾娑?..")
    results = {}

    # 1. 閸愬懎鐡ㄥΛ鈧弻?    try:
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
            "status": "棣冾潵 闂€鎸庢埂鐠佹澘绻傞崷銊у殠" if total_actions > 0 else "棣冩憫 鐠佹澘绻傛惔鎾茶礋缁岀尨绱濈粵澶婄窡妫ｆ牗顐兼担璺ㄦ暏",
        }
        print(f"[AI婢堆嗗壋] 鐠佹澘绻? {total_actions}閺壜ゎ攽閸? {total_learned}閺夛紕鐓＄拠? {total_corrections}閺夛紕绫傚?)
    except Exception as e:
        results["memory"] = {"ok": False, "error": str(e)}

    # 2. 閹存劕濮涢悳鍥殰濡偓
    try:
        rate_30d = EvolutionEngine.get_success_rate(days=30)
        rate_7d = EvolutionEngine.get_success_rate(days=7)
        trend = "棣冩惐" if rate_7d > rate_30d else "棣冩惒" if rate_7d < rate_30d else "閴冣槄绗?
        results["performance"] = {
            "ok": True,
            "success_rate_30d": rate_30d,
            "success_rate_7d": rate_7d,
            "trend": f"{trend} {'閹绘劕宕屾稉? if rate_7d > rate_30d else '闂団偓閸忚櫕鏁? if rate_7d < rate_30d else '缁嬪啿鐣?}",
        }
        print(f"[AI婢堆嗗壋] 閹存劕濮涢悳? 30婢?{rate_30d}%, 7婢?{rate_7d}% {trend}")
    except Exception as e:
        results["performance"] = {"ok": False, "error": str(e)}

    # 3. 閺堫亜顒熸稊鐘垫畱缁剧姵顒?    try:
        pending = EvolutionEngine.get_corrections(learned=0)
        results["pending_learning"] = {
            "ok": True,
            "count": len(pending),
            "items": pending[:5],
        }
        if pending:
            print(f"[AI婢堆嗗壋] 閳跨媴绗?{len(pending)}閺夛紕鏁ら幋椋庣眰濮濓絽绶熺€涳缚绡?)
        else:
            print(f"[AI婢堆嗗壋] 閴?閹碘偓閺堝绫傚锝呭嚒濞戝牆瀵?)
    except Exception as e:
        results["pending_learning"] = {"ok": False, "error": str(e)}

    # 4. 鏉╂稑瀵插楦款唴
    try:
        report = EvolutionEngine.evolve_report()
        results["evolution_suggestions"] = report.get("suggestions", [])[:3]
    except Exception:
        results["evolution_suggestions"] = []

    
    # 5. Git鐠佹澘绻傞崥灞绢劄 閳?閹峰褰囬崣锔跨缁旂枆I閻ㄥ嫯顔囪箛?    try:
        from tools.memory_sync import MemorySync
        sync_result = MemorySync.sync_pull()
        results["memory_sync"] = {
            "ok": sync_result["ok"],
            "other_identity": sync_result.get("other_identity", "unknown"),
            "other_friday": sync_result.get("other_friday_preview", "")[:100],
        }
        if sync_result["ok"]:
            print(f"[AI婢堆嗗壋] 棣冩敡 瀹告彃鎮撳顨乻ync_result.get('other_identity')}閻ㄥ嫯顔囪箛?)
        else:
            print(f"[AI婢堆嗗壋] 閳跨媴绗?鐠佹澘绻傞崥灞绢劄鐠哄疇绻? {sync_result.get('git_result',{}).get('detail','')}")
    except Exception as e:
        results["memory_sync"] = {"ok": False, "error": str(e)}

    all_ok = all(v.get("ok", True) for v in results.values() if isinstance(v, dict))
    summary = "閴?AI婢堆嗗壋閸氼垰濮╃€瑰本鍨氶敍灞藉弿缁崵绮哄锝呯埗" if all_ok else "閳跨媴绗?AI婢堆嗗壋閸氼垰濮╃€瑰本鍨氶敍宀勫劥閸掑棙膩閸ф娓堕崗铏暈"

    print(f"[AI婢堆嗗壋] {summary}")
    return {"ok": all_ok, "summary": summary, "details": results, "started_at": datetime.now().isoformat()}

async def startup_warmup():
    """閸氼垰濮╂０鍕劰 閳?閸旂姾娴囬崢鍡楀蕉缂佸繘鐛欓崚鏉夸紣娴ｆ粏顔囪箛?""
    print("[AI婢堆嗗壋] 棣冩暉 閸旂姾娴囬崢鍡楀蕉缂佸繘鐛?..")
    knowledge = {}
    try:
        db = _get_db()
        # 閸旂姾娴囨妯圭幆閸婅偐鐓＄拠?        rows = db.execute("SELECT category, key, value, score FROM learning WHERE score > 0.5 ORDER BY score DESC LIMIT 50").fetchall()
        for r in rows:
            cat = r["category"]
            if cat not in knowledge:
                knowledge[cat] = []
            knowledge[cat].append({"key": r["key"], "value": r["value"], "score": r["score"]})

        # 閸旂姾娴囬張鈧担宕囩摜閻?        best_scraper = db.execute("SELECT key, score FROM learning WHERE category='scraper_sources' ORDER BY score DESC LIMIT 5").fetchall()
        knowledge["_best_scraper_sources"] = [{"source": r["key"], "score": r["score"]} for r in best_scraper]

        db.close()
        print(f"[AI婢堆嗗壋] 瀹告彃濮炴潪?{len(knowledge)}娑擃亪顣崺鐔烘畱閻儴鐦?)
    except Exception as e:
        print(f"[AI婢堆嗗壋] 妫板嫮鍎归崝鐘烘祰婢惰精瑙? {e}")

    return {"knowledge_categories": len(knowledge), "loaded": True}

# 閸氼垰濮╅弮鎯板殰閸斻劍鏁為崘宀€娈戞禍瀣╂
def register_startup_events():
    """濞夈劌鍞介幍鈧張澶婃儙閸斻劑鎸€?""
    return {
        "self_check": startup_self_check,
        "warmup": startup_warmup,
    }
