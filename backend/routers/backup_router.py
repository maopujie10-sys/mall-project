"""备份恢复系统 -- 校验+一键恢复+保留策略"""
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
    """备份列表(含校验状态)"""
    backups = []
    for f in sorted(glob.glob(os.path.join(BACKUP_DIR, "*.sql*")) + glob.glob(os.path.join(BACKUP_DIR, "*.tar*")), reverse=True):
        size = os.path.getsize(f)
        name = os.path.basename(f)
        mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M")
        # 校验文件是否存在hash
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
    """校验备份文件完整性"""
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        raise HTTPException(404, "备份文件不存在")
    file_hash = hashlib.sha256(open(backup_path, "rb").read()).hexdigest()
    hash_path = backup_path + ".sha256"
    with open(hash_path, "w") as f: f.write(file_hash)
    return {"ok": True, "file": backup_name, "hash": file_hash, "verified": True}

@router.post("/restore/{backup_name}")
async def restore_backup(backup_name: str, target_db: str = "", _=Depends(verify_token)):
    """一键恢复数据库(需审批L4)"""
    await handle_risk("L4", f"恢复数据库: {backup_name}", need_confirm=True)
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        raise HTTPException(404, "备份文件不存在")
    db = target_db or DB_CONFIG.get("name", "ai_agent")
    user = DB_CONFIG.get("user", "root")
    password = DB_CONFIG.get("password", "")
    host = DB_CONFIG.get("host", "127.0.0.1")
    port = DB_CONFIG.get("port", 3306)
    try:
        if backup_name.endswith(".sql"):
            import tempfile
            fd, cnf_path = tempfile.mkstemp(suffix='.cnf')
            with os.fdopen(fd, 'w') as f:
                f.write(f"[client]\nuser={user}\npassword={password}\nhost={host}\nport={port}\n")
            os.chmod(cnf_path, 0o600)
            try:
                result = subprocess.run(
                    ["mysql", f"--defaults-extra-file={cnf_path}", db],
                    stdin=open(backup_path, 'r'), capture_output=True, text=True, timeout=300)
            finally:
                os.unlink(cnf_path)
        else:
            result = subprocess.run(["tar", "-xzf", backup_path, "-C", "/"], capture_output=True, text=True, timeout=120)
        return {"ok": result.returncode == 0, "output": (result.stdout or result.stderr)[:500]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}

@router.delete("/cleanup")
async def cleanup_old_backups(days: int = 30, _=Depends(verify_token)):
    """清理超过N天的备份(保留最近30天)"""
    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0
    for f in glob.glob(os.path.join(BACKUP_DIR, "*")):
        try:
            if datetime.fromtimestamp(os.path.getmtime(f)) < cutoff:
                os.remove(f)
                deleted += 1
        except: pass
    return {"ok": True, "deleted": deleted, "kept_days": days}
