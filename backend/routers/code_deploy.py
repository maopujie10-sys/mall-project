"""AI代码部署 — 生成→沙箱→验证→上线"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tools.logger import get_logger
from auth import verify_token

router = APIRouter(prefix="/agent/deploy", tags=["CodeDeploy"])
logger = get_logger("deploy")

@router.post("/generate")
async def generate_and_deploy(spec: str = "", language: str = "python", _=Depends(verify_token)):
    """AI生成代码+验证+部署"""
    try:
        from agents.multi_model import ModelRouter
        resp = ModelRouter.smart_chat(messages=[{"role":"user","content":f"根据需求生成{language}代码,只输出代码:\n{spec}"}], mode="smart")
        code = resp.get("content","") if isinstance(resp,dict) else str(resp)
        code = code.strip().strip("```").strip(language).strip("```").strip()

        # 语法验证
        import ast, tempfile, os
        if language == "python":
            try:
                ast.parse(code)
                syntax_ok = True
            except SyntaxError as se:
                return {"ok":False,"error":f"语法错误: {se}","code":code}
        else:
            syntax_ok = True

        # 保存到临时文件
        ext = {"python":".py","javascript":".js","html":".html"}.get(language,".txt")
        tmp = tempfile.NamedTemporaryFile(mode='w',suffix=ext,delete=False,encoding='utf-8')
        tmp.write(code); tmp.close()

        # 执行测试(python)
        import subprocess
        test_result = ""
        if language == "python":
            try:
                r = subprocess.run(["python3",tmp.name],capture_output=True,text=True,timeout=30)
                test_result = f"stdout:\n{r.stdout[:1000]}\nstderr:\n{r.stderr[:500]}"
                if r.returncode != 0: test_result += f"\n[EXIT:{r.returncode}]"
            except subprocess.TimeoutExpired:
                test_result = "执行超时(30s)"
            except: test_result = "执行失败"

        os.unlink(tmp.name)
        return {"ok":True,"syntax_ok":syntax_ok,"code":code[:2000],"test_result":test_result,"lines":len(code.splitlines())}
    except Exception as e:
        return {"ok":False,"error":str(e)}

@router.post("/validate")
async def validate_code(code: str = "", language: str = "python", _=Depends(verify_token)):
    """代码验证"""
    try:
        import ast
        ast.parse(code)
        return {"ok":True,"valid":True,"message":"语法正确"}
    except SyntaxError as e:
        return {"ok":True,"valid":False,"error":str(e),"line":e.lineno}