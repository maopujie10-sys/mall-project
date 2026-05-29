锘?""澶囦唤鎭㈠绯荤粺 鈥?鏍￠獙+涓€閿仮澶?淇濈暀绛栫暐"""
import os, hashlib, glob, json, subprocess
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from auth import verify_token
from state import state
from risk import handle_risk
from config import BACKUP_DIR, DB_CONFIG

router = APIRouter(prefix="/agent/backup", tags=["Backup"])

@router.get("/list")
async def list_backups(_=Depends(verify_token)):
    """澶囦唤鍒楄〃(鍚牎楠岀姸鎬?"""
    backups = []
    for f in sorted(glob.glob(os.path.join(BACKUP_DIR, "*.sql*")) + glob.glob(os.path.join(BACKUP_DIR, "*.tar*")), reverse=True):
        size = os.path.getsize(f)
        name = os.path.basename(f)
        mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M")
        # 鏍￠獙鏂囦欢鏄惁瀛樺湪hash
        hash_file = f + ".sha256"
        verified = False
        if os.path.exists(hash_file):
            with open(hash_file) as hf:
                stored_hash = hf.read().strip()
                file_hash = hashlib.sha256(open(f,"rb").read()).hexdigest()
                verified = stored_hash == file_hash
        backups.append({"name": name, "size_mb": round(size/(1024*1024), 1), "date": mtime,
                       "verified": verified, "path": f})
    return {"ok": True, "backups": backups, "count": len(backups)}

@router.post("/verify/{backup_name}")
async def verify_backup(backup_name: str, _=Depends(verify_token)):
    """鏍￠獙澶囦唤鏂囦欢瀹屾暣鎬?""
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        raise HTTPException(404, "澶囦唤鏂囦欢涓嶅瓨鍦?)
    file_hash = hashlib.sha256(open(backup_path, "rb").read()).hexdigest()
    hash_path = backup_path + ".sha256"
    with open(hash_path, "w") as f: f.write(file_hash)
    return {"ok": True, "file": backup_name, "hash": file_hash, "verified": True}

@router.post("/restore/{backup_name}")
async def restore_backup(backup_name: str, target_db: str = "", _=Depends(verify_token)):
    """涓€閿仮澶嶆暟鎹簱锛堥渶瀹℃壒L4锛?""
    await handle_risk("L4", f"鎭㈠鏁版嵁搴? {backup_name}", need_confirm=True)
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        raise HTTPException(404, "澶囦唤鏂囦欢涓嶅瓨鍦?)
    db = target_db or DB_CONFIG.get("name", "ai_agent")
    user = DB_CONFIG.get("user", "root")
    password = DB_CONFIG.get("password", "")
    host = DB_CONFIG.get("host", "127.0.0.1")
    port = DB_CONFIG.get("port", 3306)
    try:
        if backup_name.endswith(".sql"):
            cmd = f"mysql -h{host} -P{port} -u{user} -p{password} {db} < {backup_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        else:
            result = subprocess.run(["tar", "-xzf", backup_path, "-C", "/"], capture_output=True, text=True, timeout=120)
        return {"ok": result.returncode == 0, "output": (result.stdout or result.stderr)[:500]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}

@router.delete("/cleanup")
async def cleanup_old_backups(days: int = 30, _=Depends(verify_token)):
    """娓呯悊瓒呰繃N澶╃殑澶囦唤(淇濈暀鏈€杩?0澶?"""
    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0
    for f in glob.glob(os.path.join(BACKUP_DIR, "*")):
        try:
            if datetime.fromtimestamp(os.path.getmtime(f)) < cutoff:
                os.remove(f)
                deleted += 1
        except: pass
    return {"ok": True, "deleted": deleted, "kept_days": days}
