"""婢跺洣鍞ゆ稉搴℃礀濠婃氨搁悶閳閺佺増宓佹惔鎾愁槵娴闁秶鐤嗛崶鐐寸泊/娑撯偓闁款喗浠径""
import os, json, subprocess
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from state import state
from risk import handle_risk
from config import MALL_DB_HOST, MALL_DB_PORT, MALL_DB_USER, MALL_DB_PASSWORD, MALL_DB_NAME, BACKUP_DIR

router = APIRouter(prefix="/rollback", tags=["Rollback"])

BACKUP_FILE = os.path.join(BACKUP_DIR, "backup_records.json")

def _ensure_dirs():
    os.makedirs(BACKUP_DIR, exist_ok=True)

def _load_backups():
    _ensure_dirs()
    try:
        if os.path.exists(BACKUP_FILE):
            with open(BACKUP_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def _save_backups(records):
    _ensure_dirs()
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

class CreateBackupRequest(BaseModel):
    name: str
    type: str = "manual"
    target: str = "database"  # database / nginx / config / project

@router.get("/backups")
async def list_backups(_=Depends(verify_token)):
    """閺屻儳婀呮径鍥﹀敜閸掓""
    await handle_risk("L1", "閺屻儳婀呮径鍥﹀敜閸掓)
    records = _load_backups()
    # 侊紕鐣绘径鍥﹀敜閹銇囩亸    total_size = 0
    for r in records:
        path = r.get("path", "")
        if os.path.exists(path):
            try:
                total_size += os.path.getsize(path)
            except:
                pass
    return {"backups": records, "count": len(records), "total_size_mb": round(total_size / 1024 / 1024, 2)}

@router.post("/backups")
async def create_backup(req: CreateBackupRequest, _=Depends(verify_token)):
    """閸掓稑缂撻弬鏉款槵娴犳枻绱欓弨顖涘瘮閺佺増宓佹惔闁秶鐤妞ゅ湱娲伴敍""
    await handle_risk("L2", f"閸掓稑缂撴径鍥﹀敜: {req.name} ({req.target})")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result = {"path": "", "success": False, "size": 0}

    if req.target == "database" and MALL_DB_HOST and MALL_DB_USER:
        # 娴ｈ法鏁mysqldump 婢跺洣鍞ら弫鐗堝祦鎼        backup_file = os.path.join(BACKUP_DIR, f"backup_{MALL_DB_NAME}_{timestamp}.sql.gz")
        dump_cmd = f'mysqldump -h {MALL_DB_HOST} -P {MALL_DB_PORT} -u {MALL_DB_USER} -p{MALL_DB_PASSWORD} {MALL_DB_NAME} 2>/dev/null | gzip > {backup_file}'
        try:
            subprocess.run(dump_cmd, shell=True, check=True, timeout=120)
            if os.path.exists(backup_file):
                result["path"] = backup_file
                result["success"] = True
                result["size"] = os.path.getsize(backup_file)
        except Exception as e:
            result["error"] = str(e)
            # 鐏忔繆鐦稉宥呯敨 gzip
            backup_file = os.path.join(BACKUP_DIR, f"backup_{MALL_DB_NAME}_{timestamp}.sql")
            dump_cmd = f'mysqldump -h {MALL_DB_HOST} -P {MALL_DB_PORT} -u {MALL_DB_USER} -p{MALL_DB_PASSWORD} {MALL_DB_NAME} > {backup_file} 2>/dev/null'
            try:
                subprocess.run(dump_cmd, shell=True, check=True, timeout=120)
                if os.path.exists(backup_file):
                    result["path"] = backup_file
                    result["success"] = True
                    result["size"] = os.path.getsize(backup_file)
            except Exception as e2:
                result["error"] = f"閺佺増宓佹惔鎾愁槵娴犺棄銇戠拹 mysqldump 娑撳秴褰查悽銊﹀灗鏉╃偞甯存径杈Е"
                result["fallback"] = "囬樻穱婵嗗嚒鐎瑰顥mysql-client 楠炲爼鍘ょ純MALL_DB_* 閻滎垰顣ㄩ崣姗鍣

    elif req.target == "nginx":
        # 婢跺洣鍞Nginx 闁秶鐤        backup_file = os.path.join(BACKUP_DIR, f"nginx_conf_{timestamp}.tar.gz")
        cmd = f"tar czf {backup_file} /etc/nginx 2>/dev/null && echo ok || echo fail"
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if r.stdout.strip() == "ok" and os.path.exists(backup_file):
                result["path"] = backup_file
                result["success"] = True
                result["size"] = os.path.getsize(backup_file)
        except:
            result["error"] = "Nginx 闁秶鐤嗘径鍥﹀敜婢惰精瑙

    elif req.target == "project":
        # 婢跺洣鍞ゆい鍦窗閺傚洣娆        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backup_file = os.path.join(BACKUP_DIR, f"project_{timestamp}.tar.gz")
        cmd = f"tar czf {backup_file} -C {project_dir} --exclude=node_modules --exclude=.git --exclude=__pycache__ . 2>/dev/null && echo ok || echo fail"
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            if r.stdout.strip() == "ok" and os.path.exists(backup_file):
                result["path"] = backup_file
                result["success"] = True
                result["size"] = os.path.getsize(backup_file)
        except:
            result["error"] = "妞ゅ湱娲版径鍥﹀敜婢惰精瑙

    # 娣囨繂鐡ㄧ拋鏉跨秿
    records = _load_backups()
    entry = {
        "id": f"backup_{len(records)+1}_{int(datetime.now().timestamp())}",
        "name": req.name,
        "type": req.type,
        "target": req.target,
        "path": result.get("path", ""),
        "size_bytes": result.get("size", 0),
        "size_mb": round(result.get("size", 0) / 1024 / 1024, 2),
        "success": result.get("success", False),
        "error": result.get("error", ""),
        "created": datetime.now().isoformat(),
        "verified": False,
        "expires_at": (datetime.now().timestamp() + 7 * 24 * 3600),  # 7婢垛晞绻冮張    }
    records.insert(0, entry)
    if len(records) > 100:
        records[:] = records[:100]
    _save_backups(records)

    return entry

@router.post("/backups/{backup_id}/verify")
async def verify_backup(backup_id: str, _=Depends(verify_token)):
    """閺嶏繝鐛欐径鍥﹀敜閺傚洣娆㈢瑰本鏆ｉ幀""
    await handle_risk("L2", "閺嶏繝鐛欐径鍥﹀敜", backup_id)
    records = _load_backups()
    for r in records:
        if r["id"] == backup_id:
            path = r.get("path", "")
            if not path or not os.path.exists(path):
                r["verified"] = False
                r["verify_error"] = "婢跺洣鍞ら弬鍥︽娑撳秴鐡ㄩ崷
                _save_backups(records)
                return {"backup_id": backup_id, "verified": False, "error": "閺傚洣娆㈡稉宥呯摠閸}
            size = os.path.getsize(path)
            r["verified"] = size > 0
            r["verified_at"] = datetime.now().isoformat()
            _save_backups(records)
            return {"backup_id": backup_id, "verified": True, "size_mb": round(size / 1024 / 1024, 2)}
    raise HTTPException(404, "婢跺洣鍞ょ拋鏉跨秿娑撳秴鐡ㄩ崷)

@router.post("/backups/{backup_id}/rollback")
async def rollback(backup_id: str, _=Depends(verify_token)):
    """閹笛嗩攽閸ョ偞绮撮幙宥勭稊"""
    records = _load_backups()
    for r in records:
        if r["id"] == backup_id:
            path = r.get("path", "")
            target = r.get("target", "database")

            risk = await handle_risk("L3", f"閸ョ偞绮撮幙宥勭稊: {r['name']}", f"閻╊喗鐖 {target}, 閺傚洣娆 {path}")
            if not risk["allowed"]:
                return risk

            if not path or not os.path.exists(path):
                return {"backup_id": backup_id, "status": "failed", "error": "婢跺洣鍞ら弬鍥︽娑撳秴鐡ㄩ崷}

            result = {"success": False}
            if target == "database" and path.endswith(".sql"):
                # 閹垹顦查弫鐗堝祦鎼                if MALL_DB_HOST and MALL_DB_USER:
                    try:
                        cmd = f"mysql -h {MALL_DB_HOST} -P {MALL_DB_PORT} -u {MALL_DB_USER} -p{MALL_DB_PASSWORD} {MALL_DB_NAME} < {path} 2>&1"
                        r2 = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
                        result["success"] = r2.returncode == 0
                        result["output"] = r2.stdout[:200] or r2.stderr[:200]
                    except Exception as e:
                        result["error"] = str(e)
                else:
                    result["error"] = "閺佺増宓佹惔鎾存弓闁秶鐤
            elif target == "nginx" and path.endswith(".tar.gz"):
                try:
                    cmd = f"tar xzf {path} -C / 2>&1 && nginx -t 2>&1 && echo ok || echo fail"
                    r2 = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                    result["success"] = "ok" in r2.stdout
                    result["output"] = r2.stdout[:200]
                except Exception as e:
                    result["error"] = str(e)
            else:
                result["info"] = "濄倗琚崹瀣畱閸ョ偞绮撮棁鈧幍瀣З閹笛嗩攽"

            return {
                "backup_id": backup_id,
                "status": "completed" if result["success"] else "failed",
                "result": result,
                "note": "閸ョ偞绮寸瑰本鍨氶敍宀冾嚞妤犲矁鐦夐張宥呭閺勵垰鎯佸锝呯埗",
            }
    raise HTTPException(404, "婢跺洣鍞ょ拋鏉跨秿娑撳秴鐡ㄩ崷)

@router.delete("/backups/{backup_id}")
async def delete_backup(backup_id: str, _=Depends(verify_token)):
    """閸掔娀娅庢径鍥﹀敜佹澘缍""
    records = _load_backups()
    for i, r in enumerate(records):
        if r["id"] == backup_id:
            path = r.get("path", "")
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
            records.pop(i)
            _save_backups(records)
            return {"deleted": True, "backup_id": backup_id}
    raise HTTPException(404, "婢跺洣鍞ょ拋鏉跨秿娑撳秴鐡ㄩ崷)

@router.post("/cleanup")
async def cleanup_old_backups(_=Depends(verify_token)):
    """濞撳懐鎮婃潻鍥ㄦ埂婢跺洣鍞ら敍鍫滅箽閻ｆ瑦娓舵潻婢垛晪绱""
    await handle_risk("L2", "濞撳懐鎮婃潻鍥ㄦ埂婢跺洣鍞)
    records = _load_backups()
    now = datetime.now().timestamp()
    kept = []
    removed = 0
    for r in records:
        expires = r.get("expires_at", 0)
        if expires > 0 and now > expires:
            path = r.get("path", "")
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
            removed += 1
        else:
            kept.append(r)
    _save_backups(kept)
    return {"removed": removed, "remaining": len(kept)}

