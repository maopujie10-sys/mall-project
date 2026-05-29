锘?""AI宸ヤ綔娴佸紩鎿?鈥?澶氭浠诲姟鑷姩鎷嗚В涓庢墽琛?""
import asyncio, json, re
from datetime import datetime
from state import state
from tools.registry import registry

class WorkflowEngine:
    workflows = {}

    @classmethod
    async def parse_and_execute(cls, user_input: str) -> dict:
        """瑙ｆ瀽鐢ㄦ埛鑷劧璇█杈撳叆锛屾媶瑙ｄ负宸ヤ綔娴佹楠?""
        # 鍐呯疆宸ヤ綔娴佹ā鏉?
        templates = {
            "涓嬫灦": {"steps": [
                {"tool":"product.list","params":{"status":"low_stock"},"desc":"鏌ユ壘浣庡簱瀛樺晢鍝?},
                {"tool":"product.batch_offline","params":{},"desc":"鎵归噺涓嬫灦","risk":"L3"},
                {"tool":"report.generate","params":{"type":"offline_report"},"desc":"鐢熸垚涓嬫灦鎶ュ憡"},
            ]},
            "澶囦唤": {"steps": [
                {"tool":"db.backup","params":{},"desc":"澶囦唤鏁版嵁搴?,"risk":"L3"},
                {"tool":"file.archive","params":{"type":"backup"},"desc":"褰掓。澶囦唤鏂囦欢"},
            ]},
            "閮ㄧ讲": {"steps": [
                {"tool":"git.pull","params":{},"desc":"鎷夊彇鏈€鏂颁唬鐮?,"risk":"L3"},
                {"tool":"docker.build","params":{"service":"all"},"desc":"鏋勫缓闀滃儚","risk":"L3"},
                {"tool":"docker.deploy","params":{"service":"all"},"desc":"閮ㄧ讲鏈嶅姟","risk":"L4"},
            ]},
            "宸℃": {"steps": [
                {"tool":"server.status","params":{},"desc":"妫€鏌ユ湇鍔″櫒鐘舵€?},
                {"tool":"docker.ps","params":{},"desc":"妫€鏌ocker瀹瑰櫒"},
                {"tool":"nginx.status","params":{},"desc":"妫€鏌ginx鐘舵€?},
                {"tool":"db.status","params":{},"desc":"妫€鏌ユ暟鎹簱鐘舵€?},
                {"tool":"rotation.domains","params":{},"desc":"妫€鏌ュ煙鍚嶅仴搴?},
            ]},
            "SSL": {"steps": [
                {"tool":"ssl.status","params":{},"desc":"鏌ヨSSL璇佷功鐘舵€?},
                {"tool":"ssl.renew","params":{},"desc":"缁鍒版湡鐨勮瘉涔?,"risk":"L3"},
            ]},
        }
        # 鏅鸿兘鍖归厤
        matched = None
        for keyword, wf in templates.items():
            if keyword in user_input:
                matched = {"name": f"{keyword}宸ヤ綔娴?, "steps": wf["steps"]}
                break
        if not matched:
            return {"ok": False, "error": "鏈兘璇嗗埆鐨勪换鍔＄被鍨?, "suggestions": list(templates.keys())}
        # 鍒涘缓宸ヤ綔娴両D
        wf_id = f"wf_{int(datetime.now().timestamp())}"
        cls.workflows[wf_id] = matched
        # 閫愭楠ゆ墽琛?
        results = []
        for i, step in enumerate(matched["steps"]):
            step_result = {"step": i+1, "name": step["desc"], "tool": step["tool"], "status": "running"}
            try:
                tool_result = await registry.execute(step["tool"], **(step.get("params",{})))
                step_result["status"] = "done" if tool_result.get("ok",False) else "failed"
                step_result["result"] = tool_result.get("result", tool_result.get("error",""))
            except Exception as e:
                step_result["status"] = "failed"
                step_result["error"] = str(e)
            results.append(step_result)
            # 澶辫触鍒欎腑鏂?
            if step_result["status"] == "failed":
                break
        wf_result = {"id": wf_id, "name": matched["name"], "steps": results,
                     "total": len(matched["steps"]), "completed": sum(1 for r in results if r["status"]=="done"),
                     "failed": sum(1 for r in results if r["status"]=="failed"), "time": datetime.now().isoformat()}
        state.append_data("workflow_history", wf_result, 50)
        return {"ok": True, "workflow": wf_result}
