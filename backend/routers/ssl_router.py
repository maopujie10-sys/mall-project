锘?""SSL 璇佷功绠＄悊 鈥?鑷姩绛惧彂/缁/鐘舵€佹煡璇?""
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
    """妫€鏌ユ湰鍦拌瘉涔︽湁鏁堟€э紙openssl 鍛戒护锛?""
    fp = os.path.join(CERT_DIR, domain, "fullchain.cer")
    if not os.path.exists(fp):
        return {"ok": False, "reason": "璇佷功鏂囦欢涓嶅瓨鍦?, "days_left": 0}
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
    """閫氳繃 acme.sh 绛惧彂璇佷功锛坰tandalone 妯″紡闇€ 80 绔彛锛?""
    ac = os.path.expanduser("~/.acme.sh/acme.sh")
    if not os.path.exists(ac):
        return {"ok": False, "error": "acme.sh 鏈畨瑁咃紝璇锋墽琛? curl https://get.acme.sh | sh"}
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
        return {"ok": False, "error": "绛惧彂瓒呮椂(120s)"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/issue")
async def ssl_issue(req: SSLIssueRequest, _=Depends(verify_token)):
    """绛惧彂SSL璇佷功"""
    await handle_risk("L2", f"绛惧彂SSL: {req.domain}")
    v = _cert_valid(req.domain)
    if v.get("ok") and v.get("days_left", 0) > 60:
        return {"ok": True, "status": "already_valid", "domain": req.domain, "days_left": v["days_left"]}
    return _issue(req.domain, req.email)


@router.post("/renew")
async def ssl_renew(domain: str, _=Depends(verify_token)):
    """缁SSL璇佷功"""
    await handle_risk("L2", f"缁SSL: {domain}")
    ac = os.path.expanduser("~/.acme.sh/acme.sh")
    if not os.path.exists(ac):
        return {"ok": False, "error": "acme.sh 鏈畨瑁?}
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
    """鏌ヨSSL璇佷功鐘舵€?""
    await handle_risk("L1", "鏌ヨSSL鐘舵€?)
    if domain:
        result = _cert_valid(domain)
        result["domain"] = domain
        return result
    from routers.rotation_panel import _get_domains
    dl = _get_domains()
    return {"domains": [{"domain": d["domain"], **_cert_valid(d["domain"])} for d in dl]}


@router.get("/expiring")
async def ssl_expiring(days: int = 30, _=Depends(verify_token)):
    """鏌ヨ鍗冲皢鍒版湡鐨勮瘉涔?""
    await handle_risk("L1", "鏌ヨ鍒版湡璇佷功")
    from routers.rotation_panel import _get_domains
    dl = _get_domains()
    expiring = []
    for d in dl:
        info = _cert_valid(d["domain"])
        if not info.get("ok") or info.get("days_left", 0) <= days:
            info["domain"] = d["domain"]
            expiring.append(info)
    return {"expiring": expiring, "count": len(expiring)}
