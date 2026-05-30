"""AI工具箱 -- 代码解释器 / 联网搜索 / 图片生成 / 用量统计 / 评测"""
import json, os, sys, io, re, base64, asyncio, subprocess, tempfile, shutil
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from auth import verify_token

router = APIRouter(prefix="/agent/tools", tags=["Tools"])
USAGE_DB = Path(__file__).parent.parent / "data" / "usage.db"

def _udb():
    USAGE_DB.parent.mkdir(parents=True, exist_ok=True)
    import sqlite3
    c = sqlite3.connect(str(USAGE_DB))
    c.execute("CREATE TABLE IF NOT EXISTS usage(id INTEGER PRIMARY KEY AUTOINCREMENT,model TEXT,tokens_in INTEGER,tokens_out INTEGER,cost REAL, endpoint TEXT, owner TEXT DEFAULT 'admin', created TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS evals(id INTEGER PRIMARY KEY AUTOINCREMENT,question TEXT,answer TEXT,score REAL,feedback TEXT,owner TEXT DEFAULT 'admin',created TEXT)")
    c.commit(); return c

# ===== 1. 代码解释器 =====
class CodeRequest(BaseModel):
    code: str
    language: str = "python"  # python | sql
    timeout: int = 15

SAFE_BUILTINS = {"print","len","range","int","float","str","list","dict","set","tuple","bool","sum","min","max","sorted","enumerate","zip","map","filter","abs","round","type","isinstance","len","json","datetime","math","statistics","collections","itertools","re","random","hashlib","base64","csv","io","StringIO","BytesIO"}

@router.post("/code")
async def run_code(req: CodeRequest, _=Depends(verify_token)):
    """安全沙箱执行Python/SQL代码"""
    if req.language == "sql":
        try:
            from config import MALL_DB_HOST, MALL_DB_USER, MALL_DB_PASSWORD, MALL_DB_NAME
            import pymysql
            conn = pymysql.connect(host=MALL_DB_HOST, user=MALL_DB_USER, password=MALL_DB_PASSWORD, database=MALL_DB_NAME, charset='utf8mb4', connect_timeout=5)
            cursor = conn.cursor()
            cursor.execute(req.code[:2000])
            rows = cursor.fetchall()[:50]
            cols = [d[0] for d in cursor.description] if cursor.description else []
            conn.close()
            result = {"columns": cols, "rows": [list(r) for r in rows], "row_count": len(rows)}
            _track("code-sql", 0, 0, 0)
            return {"ok": True, "language": "sql", "result": json.dumps(result, ensure_ascii=False, default=str)}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    # Python沙箱
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        code_clean = req.code.replace('\r\n','\n')[:5000]
        # AST白名单验证 -- 只允许安全的AST节点
        import ast
        ALLOWED_NODES = {
            ast.Expr, ast.Assign, ast.Name, ast.Constant, ast.Num, ast.Str,
            ast.BinOp, ast.UnaryOp, ast.Compare, ast.BoolOp, ast.IfExp,
            ast.If, ast.For, ast.While, ast.List, ast.Dict, ast.Tuple, ast.Set,
            ast.Call, ast.Attribute, ast.Subscript, ast.Slice, ast.Index,
            ast.Return, ast.FunctionDef, ast.arguments, ast.arg,
            ast.Module, ast.Pass, ast.Break, ast.Continue,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
            ast.Eq, ast.NotEq, ast.Lt, ast.Gt, ast.LtE, ast.GtE,
            ast.And, ast.Or, ast.Not, ast.In, ast.NotIn, ast.Is, ast.IsNot,
            ast.ListComp, ast.DictComp, ast.GeneratorExp,
            ast.Load, ast.Store, ast.Del, ast.AugAssign,
        }
        tree = ast.parse(code_clean)
        for node in ast.walk(tree):
            if type(node) not in ALLOWED_NODES:
                return {"ok": False, "error": f"禁止的代码结构: {type(node).__name__}"}

        old_stdout = sys.stdout; sys.stdout = stdout
        old_stderr = sys.stderr; sys.stderr = stderr

        import math, statistics, datetime as dt, re as re_m, random as rnd, json as j, collections, itertools, hashlib, base64 as b64, csv

        safe_globals = {
            "__builtins__": {k: __builtins__[k] for k in SAFE_BUILTINS if k in __builtins__},
            "math": math, "statistics": statistics, "datetime": dt, "re": re_m,
            "random": rnd, "json": j, "collections": collections, "itertools": itertools,
            "hashlib": hashlib, "base64": b64, "csv": csv,
        }

        exec(code_clean, safe_globals)
        output = stdout.getvalue()
        _track("code-python", 0, 0, 0)
        return {"ok": True, "language": "python", "output": output[:5000], "error": stderr.getvalue()[:1000]}
    except Exception as e:
        return {"ok": False, "language": "python", "error": str(e), "output": stdout.getvalue()[:2000]}
    finally:
        sys.stdout = old_stdout; sys.stderr = old_stderr

# ===== 2. 联网搜索 =====
class SearchRequest(BaseModel):
    query: str
    num: int = 5

@router.post("/search")
async def web_search(req: SearchRequest, _=Depends(verify_token)):
    """DuckDuckGo实时搜索(无需API Key)"""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get("https://html.duckduckgo.com/html/",
                params={"q": req.query},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            if resp.status_code != 200:
                return {"ok": False, "error": f"搜索失败: HTTP {resp.status_code}"}
            
            html = resp.text
            # 简易HTML解析提取结果
            results = []
            for m in re.finditer(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', html):
                results.append({"title": m.group(2).strip(), "url": m.group(1)})
            for m in re.finditer(r'<a[^>]*class="result__snippet"[^>]*>([^<]*)</a>', html):
                idx = len([r for r in results if "snippet" not in r])
                if idx < len(results):
                    results[idx]["snippet"] = m.group(1).strip()
            
            results = results[:req.num]
            _track("search", 0, 0, 0)
            return {"ok": True, "query": req.query, "results": results, "count": len(results)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ===== 3. AI图片生成 =====
class ImageGenRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    n: int = 1

@router.post("/image-gen")
async def generate_image(req: ImageGenRequest, _=Depends(verify_token)):
    """DALL-E图片生成"""
    from config import OPENAI_API_KEY, OPENAI_BASE_URL
    if not OPENAI_API_KEY:
        return {"ok": False, "error": "需要配置OPENAI_API_KEY"}
    try:
        import httpx
        base = OPENAI_BASE_URL or "https://api.openai.com/v1"
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(f"{base}/images/generations",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json={"model": "dall-e-3", "prompt": req.prompt, "n": min(req.n, 1), "size": req.size, "quality": "standard"})
            if r.status_code == 200:
                d = r.json()
                images = [img.get("url") or img.get("b64_json") for img in d.get("data", [])]
                _track("dall-e-3", d.get("usage",{}).get("prompt_tokens",0), d.get("usage",{}).get("total_tokens",0), 0.04)
                return {"ok": True, "images": images}
            return {"ok": False, "error": f"DALL-E: {r.status_code} {r.text[:200]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ===== 4. 用量统计 =====
@router.get("/usage")
async def get_usage(days: int = 30, _=Depends(verify_token)):
    c = _udb()
    rows = c.execute("SELECT model,SUM(tokens_in),SUM(tokens_out),SUM(cost),COUNT(*) FROM usage WHERE created > datetime('now',?) GROUP BY model", (f'-{days} days',)).fetchall()
    total = c.execute("SELECT SUM(tokens_in),SUM(tokens_out),SUM(cost) FROM usage").fetchone()
    by_day = c.execute("SELECT date(created),SUM(tokens_in)+SUM(tokens_out),SUM(cost) FROM usage WHERE created > datetime('now',?) GROUP BY date(created) ORDER BY date(created)", (f'-{days} days',)).fetchall()
    c.close()
    models = [{"model":r[0],"tokens_in":r[1]or 0,"tokens_out":r[2]or 0,"cost":round(r[3]or 0,4),"calls":r[4]} for r in rows]
    daily = [{"date":r[0],"tokens":r[1]or 0,"cost":round(r[2]or 0,4)} for r in by_day]
    return {"ok":True,"models":models,"total_tokens_in":total[0]or 0,"total_tokens_out":total[1]or 0,"total_cost":round(total[2]or 0,4),"daily":daily}

def _track(model, ti, to, cost):
    try:
        c = _udb()
        c.execute("INSERT INTO usage(model,tokens_in,tokens_out,cost,endpoint,created) VALUES(?,?,?,?,'api',datetime('now'))",(model,ti,to,cost))
        c.commit();c.close()
    except: pass

# ===== 5. 评测体系 =====
class EvalRequest(BaseModel):
    question: str
    answer: str
    expected: str = ""

@router.post("/eval")
async def evaluate_answer(req: EvalRequest, _=Depends(verify_token)):
    """AI回答质量自动评分(1-10)"""
    from config import OPENAI_API_KEY, OPENAI_BASE_URL
    if not OPENAI_API_KEY:
        return {"ok": False, "error": "需要API Key"}
    try:
        import httpx
        base = OPENAI_BASE_URL or "https://api.openai.com/v1"
        prompt = f"评分标准:准确性/完整性/相关性/简洁性 各25分.\n问题:{req.question}\n回答:{req.answer}"
        if req.expected: prompt += f"\n期望答案:{req.expected}"
        prompt += "\n请给出总分(1-10)和简短评语.格式:分数: X/10 评语: ..."
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(f"{base}/chat/completions",
                headers={"Authorization":f"Bearer {OPENAI_API_KEY}","Content-Type":"application/json"},
                json={"model":"gpt-3.5-turbo","messages":[{"role":"system","content":"你是AI评测专家."},{"role":"user","content":prompt}],"temperature":0.3,"max_tokens":200})
            if r.status_code == 200:
                d = r.json()
                result = d.get("choices",[{}])[0].get("message",{}).get("content","")
                score_match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*10', result)
                score = float(score_match.group(1)) if score_match else 5.0
                c2 = _udb()
                c2.execute("INSERT INTO evals(question,answer,score,feedback,created) VALUES(?,?,?,?,datetime('now'))",(req.question[:500],req.answer[:500],score,result[:500]))
                c2.commit();c2.close()
                return {"ok":True,"score":score,"feedback":result}
        return {"ok":False,"error":f"API:{r.status_code}"}
    except Exception as e:
        return {"ok":False,"error":str(e)}

@router.get("/eval/history")
async def eval_history(_=Depends(verify_token)):
    c = _udb()
    rows = c.execute("SELECT question,answer,score,feedback,created FROM evals ORDER BY id DESC LIMIT 30").fetchall()
    avg = c.execute("SELECT AVG(score) FROM evals").fetchone()[0]
    c.close()
    return {"ok":True,"items":[{"question":r[0][:100],"answer":r[1][:100],"score":r[2],"feedback":r[3],"time":r[4]} for r in rows],"avg_score":round(avg or 0,1)}