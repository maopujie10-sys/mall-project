""" -- ++GitHub"""
import os
import tarfile
import json
import subprocess
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk
from config import BACKUP_DIR

router = APIRouter(prefix="/agent/archive", tags=["Archive"])

ARCHIVE_DIR = os.path.join(BACKUP_DIR, "archives")
os.makedirs(ARCHIVE_DIR, exist_ok=True)

ARCHIVE_TARGETS = {
    "landing": {"name": '', "path": "/opt/landing"},
    "nginx-config": {"name": "Nginx", "path": "/usr/local/nginx/conf"},
    "frontend-dist": {"name": "AI", "path": "frontend/dist"},
    "h5-dist": {"name": "H5", "path": "mall-app/frontend/h5/build"},
    "memory": {"name": "AI", "path": "memory"},
    "backend": {"name": '', "path": "backend"},
    "frontend-src": {"name": '', "path": "frontend/src"},
}

class ArchiveRequest(BaseModel):
    targets: list[str] = ["memory", "backend"]  
    note: str = ''  
    push_github: bool = False

@router.get("/targets")
async def list_targets(_=Depends(verify_token)):
    ''''''
    targets = []
    for key, info in ARCHIVE_TARGETS.items():
        path = info["path"]
        exists = os.path.exists(path)
        size = "N/A"
        if exists:
            if os.path.isfile(path):
                size = f"{os.path.getsize(path) / 1024:.1f} KB"
            else:
                total = 0
                for dirpath, dirnames, filenames in os.walk(path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        if os.path.exists(fp):
                            total += os.path.getsize(fp)
                size = f"{total / 1024:.1f} KB" if total < 1024*1024 else f"{total / (1024*1024):.1f} MB"
        targets.append({**info, "id": key, "exists": exists, "size": size})
    return {"ok": True, "targets": targets}

@router.post("/create")
async def create_archive(req: ArchiveRequest, _=Depends(verify_token)):
    ''''''
    await handle_risk("L2", f": {', '.join(req.targets)}")
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"archive_{ts}.tar.gz"
    archive_path = os.path.join(ARCHIVE_DIR, archive_name)
    
    included = []
    skipped = []
    
    with tarfile.open(archive_path, "w:gz") as tar:
        for target_id in req.targets:
            if target_id not in ARCHIVE_TARGETS:
                skipped.append({"id": target_id, "reason": ''})
                continue
            
            info = ARCHIVE_TARGETS[target_id]
            path = info["path"]
            
            if not os.path.exists(path):
                skipped.append({"id": target_id, "reason": f": {path}"})
                continue
            
            arcname = target_id
            tar.add(path, arcname=arcname)
            included.append({"id": target_id, "name": info["name"], "path": path})
    
    if not included:
        os.remove(archive_path)
        return {"ok": False, "error": ''}
    
    size = os.path.getsize(archive_path)
    
    
    records = state._data.setdefault("archive_records", [])
    record = {
        "id": ts,
        "name": archive_name,
        "path": archive_path,
        "size": size,
        "size_mb": round(size / (1024*1024), 2),
        "targets": included,
        "skipped": skipped,
        "note": req.note,
        "created_at": datetime.now().isoformat(),
    }
    records.insert(0, record)
    if len(records) > 50:
        records[:] = records[:50]
    state._save()
    
    result = {"ok": True, "archive": record}
    
    # GitHub
    if req.push_github:
        try:
            # GitHub release (gh CLI)
            result_gh = subprocess.run(
                ["gh", "release", "create", f"archive-{ts}", archive_path, "--title", f" {ts}", "--notes", req.note or ''],
                capture_output=True, text=True, timeout=30,
                cwd=os.path.dirname(ARCHIVE_DIR)
            )
            result["github"] = {
                "ok": result_gh.returncode == 0,
                "output": (result_gh.stdout + result_gh.stderr)[:500]
            }
        except FileNotFoundError:
            result["github"] = {"ok": False, "error": "gh CLI"}
        except Exception as e:
            result["github"] = {"ok": False, "error": str(e)[:200]}
    
    return result

@router.get("/records")
async def list_archives(_=Depends(verify_token)):
    ''''''
    records = state._data.get("archive_records", [])
    
    for r in records:
        r["file_exists"] = os.path.exists(r.get("path", ''))
    return {"ok": True, "total": len(records), "archives": records}

@router.delete("/records/{archive_id}")
async def delete_archive(archive_id: str, _=Depends(verify_token)):
    ''''''
    await handle_risk("L3", f": {archive_id}")
    records = state._data.get("archive_records", [])
    for r in records:
        if r["id"] == archive_id:
            path = r.get("path", '')
            if os.path.exists(path):
                os.remove(path)
            records.remove(r)
            state._save()
            return {"ok": True, "deleted": archive_id}
    return {"ok": False, "error": ''}

@router.get("/storage")
async def archive_storage(_=Depends(verify_token)):
    ''''''
    total_size = 0
    total_files = 0
    if os.path.exists(ARCHIVE_DIR):
        for f in os.listdir(ARCHIVE_DIR):
            fp = os.path.join(ARCHIVE_DIR, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
                total_files += 1
    
    records = state._data.get("archive_records", [])
    return {
        "ok": True,
        "dir": ARCHIVE_DIR,
        "total_files": total_files,
        "total_size_mb": round(total_size / (1024*1024), 2),
        "records_count": len(records),
    }
