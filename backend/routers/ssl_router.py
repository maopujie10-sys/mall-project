"""SSL 证书管理 — 自动签发/续签/状态查询"""
import os
import subprocess
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from risk import handle_risk

router = APIRouter(prefix="/ssl", tags=["SSL"])
CERT_DIR = os.getenv("CERT_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "certs"))


class SSLIssueRequest(BaseModel):
    domain: str
    email: str = ""


def _cert_valid(domain: str) -> dict:
    """检查本地证书有效性（openssl 命令）"""
    fp = os.path.join(CERT_DIR, domain, "fullchain.cer")
    if not os.path.exists(fp):
        return {"ok": False, "reason": "证书文件不存在", "days_left": 0}
    try:
        r = subprocess.run(
            ["openssl", "x509", "-enddate", "-noout", "-in", fp],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode != 0:
            return {"ok": False, "reason": r.stderr.strip(), "days_left": 0}
        ed = datetime.strptime(
            r.stdout.replace("notAfter=", "").strip(), "%b %d %H:%M:%S %Y %Z"
        )
        dl = (ed - datetime.now()).days
        return {"ok": dl > 0, "days_left": dl, "expiry": ed.strftime("%Y-%m-%d")}
    except Exception as e:
        return {"ok": False, "reason": str(e), "days_left": 0}


def _issue(domain: str, email: str) -> dict:
    """通过 acme.sh 签发证书（standalone 模式需 80 端口）"""
    ac = os.path.expanduser("~/.acme.sh/acme.sh")
    if not os.path.exists(ac):
        return {"ok": False, "error": "acme.sh 未安装，请执行: curl https://get.acme.sh | sh"}
    fp = os.path.join(CERT_DIR, domain, "fullchain.cer")
    kp = os.path.join(CERT_DIR, domain, "private.key")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    cmd = [ac, "--issue", "-d", domain, "--standalone", "--keylength", "ec-256"]
    cmd += ["--fullchain-file", fp, "--key-file", kp]
    if email:
        cmd += ["--accountemail", email]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return {"ok": r.returncode == 0, "domain": domain, "detail": (r.stdout or r.stderr)[-300:]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "签发超时(120s)"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/issue")
async def ssl_issue(req: SSLIssueRequest, _=Depends(verify_token)):
    """签发SSL证书"""
    await handle_risk("L2", f"签发SSL: {req.domain}")
    v = _cert_valid(req.domain)
    if v.get("ok") and v.get("days_left", 0) > 60:
        return {"ok": True, "status": "already_valid", "domain": req.domain, "days_left": v["days_left"]}
    return _issue(req.domain, req.email)


@router.post("/renew")
async def ssl_renew(domain: str, _=Depends(verify_token)):
    """续签SSL证书"""
    await handle_risk("L2", f"续签SSL: {domain}")
    ac = os.path.expanduser("~/.acme.sh/acme.sh")
    if not os.path.exists(ac):
        return {"ok": False, "error": "acme.sh 未安装"}
    try:
        r = subprocess.run(
            [ac, "--renew", "-d", domain, "--force"],
            capture_output=True, text=True, timeout=120
        )
        return {"ok": r.returncode == 0, "domain": domain, "detail": (r.stdout or r.stderr)[-300:]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/status")
async def ssl_status(domain: str = "", _=Depends(verify_token)):
    """查询SSL证书状态"""
    await handle_risk("L1", "查询SSL状态")
    if domain:
        result = _cert_valid(domain)
        result["domain"] = domain
        return result
    from routers.rotation_panel import _get_domains
    dl = _get_domains()
    return {"domains": [{"domain": d["domain"], **_cert_valid(d["domain"])} for d in dl]}


@router.get("/expiring")
async def ssl_expiring(days: int = 30, _=Depends(verify_token)):
    """查询即将到期的证书"""
    await handle_risk("L1", "查询到期证书")
    from routers.rotation_panel import _get_domains
    dl = _get_domains()
    expiring = []
    for d in dl:
        info = _cert_valid(d["domain"])
        if not info.get("ok") or info.get("days_left", 0) <= days:
            info["domain"] = d["domain"]
            expiring.append(info)
    return {"expiring": expiring, "count": len(expiring)}
