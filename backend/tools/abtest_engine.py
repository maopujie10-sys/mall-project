''"A/B -- ++AI''"
import time, random, hashlib
from collections import defaultdict
from typing import Dict, List
from tools.logger import get_logger

logger = get_logger("abtest")

class ABTestEngine:
    ''"A/B''"
    _experiments: Dict[str, Dict] = {}
    _results: Dict[str, List[Dict]] = defaultdict(list)

    @classmethod
    def create_experiment(cls, name: str, variants: List[str], traffic_split: List[float] = None) -> str:
        ''''''
        exp_id = hashlib.md5(f"{name}:{time.time()}".encode()).hexdigest()[:8]
        if not traffic_split:
            traffic_split = [1.0 / len(variants)] * len(variants)
        cls._experiments[exp_id] = {
            "name": name, "variants": variants, "traffic_split": traffic_split,
            "created_at": time.time(), "status": "running",
            "assignments": Counter(), "metrics": {v: defaultdict(list) for v in variants}
        }
        return exp_id

    @classmethod
    def assign_variant(cls, exp_id: str, user_id: str) -> str:
        ''''''
        exp = cls._experiments.get(exp_id)
        if not exp:
            return "control"

        
        h = int(hashlib.md5(f"{exp_id}:{user_id}".encode()).hexdigest(), 16)
        cum = 0
        for i, split in enumerate(exp["traffic_split"]):
            cum += split
            if h / (2**128) < cum:
                variant = exp["variants"][i]
                exp["assignments"][variant] += 1
                return variant

        return exp["variants"][-1]

    @classmethod
    def record_metric(cls, exp_id: str, variant: str, metric_name: str, value: float):
        ''''''
        if exp_id in cls._experiments:
            cls._experiments[exp_id]["metrics"][variant][metric_name].append(value)

    @classmethod
    async def analyze(cls, exp_id: str) -> Dict:
        ''"AI''"
        exp = cls._experiments.get(exp_id)
        if not exp:
            return {"ok": False, "error": ''}

        analysis = {"experiment": exp["name"], "variants": {}}

        for variant in exp["variants"]:
            metrics = exp["metrics"].get(variant, {})
            variant_stats = {}
            for mname, values in metrics.items():
                if values:
                    variant_stats[mname] = {
                        "mean": round(sum(values) / len(values), 2),
                        "count": len(values),
                        "min": round(min(values), 2),
                        "max": round(max(values), 2)
                    }
            analysis["variants"][variant] = {
                "sample_size": exp["assignments"].get(variant, 0),
                "metrics": variant_stats
            }

        # AI
        try:
            from agents.multi_model import ModelRouter
            resp = await ModelRouter.smart_chat(messages=[{"role":"user","content":f"A/B,:\n{json.dumps(analysis, ensure_ascii=False)}"}], mode="fast")
            analysis["ai_decision"] = resp.get("content", '')
        except:
            analysis["ai_decision"] = "AI,"

        return {"ok": True, **analysis}

    @classmethod
    def get_all_experiments(cls) -> List[Dict]:
        return [{"id": eid, "name": e["name"], "status": e["status"], "variants": e["variants"]}
                for eid, e in cls._experiments.items()]

    @classmethod
    def save(cls):
        ''"SQLite''"
        from tools.memory_store import memory_store
        import json
        data = {"experiments": cls._experiments}
        memory_store.set_knowledge("abtest_data", json.dumps(data, ensure_ascii=False, default=str))

    @classmethod
    def load(cls):
        ''"SQLite''"
        from tools.memory_store import memory_store
        import json
        try:
            data = memory_store.get_knowledge("abtest_data")
            if data:
                d = json.loads(data)
                cls._experiments.update(d.get("experiments", {}))
            return True
        except:
            return False

abtest_engine = ABTestEngine()

try:
    ABTestEngine.load()
except:
    pass
