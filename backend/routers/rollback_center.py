"""备份与回滚管理"""
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from main import verify_token
from state import state

router = APIRouter(prefix="/rollback", tags=["Rollback"])

BACKUP_DIR = os.path.join(os.path.dirname(__file__), "..", "backups")
BACKUP_DB = os.path.join(BACKUP_DIR, "backup_records.json")

# Simulated backup records (persisted to JSON)
import json


def _load_backups():
    try:
        if os.path.exists(BACKUP_DB):
            with open(BACKUP_DB) as f:
                return json.load(f)
    except Exception:
        pass
    return [
        {"id": "backup_001", "time": "2026-05-24 06:00", "type": "自动", "size": "128 MB", "status": "成功", "db": "malldb"},
        {"id": "backup_002", "time": "2026-05-24 12:00", "type": "自动", "size": "131 MB", "status": "成功", "db": "malldb"},
        {"id": "backup_003", "time": "2026-05-24 18:00", "type": "自动", "size": "133 MB", "status": "成功", "db": "malldb"},
    ]


def _save_backups(backups):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    try:
        with open(BACKUP_DB, "w") as f:
            json.dump(backups, f, ensure_ascii=False)
    except Exception:
        pass


class RollbackRequest(BaseModel):
    backupId: str


@router.get("/backups")
async def get_backups(_=Depends(verify_token)):
    return _load_backups()


@router.post("/create")
async def create_backup(_=Depends(verify_token)):
    backups = _load_backups()
    n = len(backups) + 1
    new_id = f"backup_{n:03d}"
    entry = {
        "id": new_id,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": "手动",
        "size": f"{130 + n} MB",
        "status": "成功",
        "db": "malldb",
    }
    backups.append(entry)
    _save_backups(backups)
    state.add_task(f"手动备份: {new_id}", risk="L2", status="完成")
    return {"result": "ok", "backup": entry}


@router.post("/execute")
async def execute_rollback(req: RollbackRequest, _=Depends(verify_token)):
    backups = _load_backups()
    target = next((b for b in backups if b["id"] == req.backupId), None)
    if not target:
        raise HTTPException(status_code=404, detail="Backup not found")

    state.add_task(f"数据库回滚: {req.backupId} ({target['time']})", risk="L3", status="完成")
    return {
        "result": "ok",
        "message": f"已回滚至 {req.backupId} ({target['time']})",
        "backup": target,
    }
