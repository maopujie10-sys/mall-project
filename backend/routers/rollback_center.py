"""备份与回滚管理 — 数据库备份/配置回滚/一键恢复"""
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
    """查看备份列表"""
    await handle_risk("L1", "查看备份列表")
    records = _load_backups()
    # 计算备份总大小
    total_size = 0
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
    """创建新备份（支持数据库/配置/项目）"""
    await handle_risk("L2", f"创建备份: {req.name} ({req.target})")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result = {"path": "", "success": False, "size": 0}

    if req.target == "database" and MALL_DB_HOST and MALL_DB_USER:
        # 使用 mysqldump 备份数据库
        backup_file = os.path.join(BACKUP_DIR, f"backup_{MALL_DB_NAME}_{timestamp}.sql.gz")
        dump_cmd = f'mysqldump -h {MALL_DB_HOST} -P {MALL_DB_PORT} -u {MALL_DB_USER} -p{MALL_DB_PASSWORD} {MALL_DB_NAME} 2>/dev/null | gzip > {backup_file}'
        try:
            subprocess.run(dump_cmd, shell=True, check=True, timeout=120)
            if os.path.exists(backup_file):
                result["path"] = backup_file
                result["success"] = True
                result["size"] = os.path.getsize(backup_file)
        except Exception as e:
            result["error"] = str(e)
            # 尝试不带 gzip
            backup_file = os.path.join(BACKUP_DIR, f"backup_{MALL_DB_NAME}_{timestamp}.sql")
            dump_cmd = f'mysqldump -h {MALL_DB_HOST} -P {MALL_DB_PORT} -u {MALL_DB_USER} -p{MALL_DB_PASSWORD} {MALL_DB_NAME} > {backup_file} 2>/dev/null'
            try:
                subprocess.run(dump_cmd, shell=True, check=True, timeout=120)
                if os.path.exists(backup_file):
                    result["path"] = backup_file
                    result["success"] = True
                    result["size"] = os.path.getsize(backup_file)
            except Exception as e2:
                result["error"] = f"数据库备份失败: mysqldump 不可用或连接失败"
                result["fallback"] = "请确保已安装 mysql-client 并配置 MALL_DB_* 环境变量"

    elif req.target == "nginx":
        # 备份 Nginx 配置
        backup_file = os.path.join(BACKUP_DIR, f"nginx_conf_{timestamp}.tar.gz")
        cmd = f"tar czf {backup_file} /etc/nginx 2>/dev/null && echo ok || echo fail"
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if r.stdout.strip() == "ok" and os.path.exists(backup_file):
                result["path"] = backup_file
                result["success"] = True
                result["size"] = os.path.getsize(backup_file)
        except:
            result["error"] = "Nginx 配置备份失败"

    elif req.target == "project":
        # 备份项目文件
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backup_file = os.path.join(BACKUP_DIR, f"project_{timestamp}.tar.gz")
        cmd = f"tar czf {backup_file} -C {project_dir} --exclude=node_modules --exclude=.git --exclude=__pycache__ . 2>/dev/null && echo ok || echo fail"
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            if r.stdout.strip() == "ok" and os.path.exists(backup_file):
                result["path"] = backup_file
                result["success"] = True
                result["size"] = os.path.getsize(backup_file)
        except:
            result["error"] = "项目备份失败"

    # 保存记录
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
        "expires_at": (datetime.now().timestamp() + 7 * 24 * 3600),  # 7天过期
    }
    records.insert(0, entry)
    if len(records) > 100:
        records[:] = records[:100]
    _save_backups(records)

    return entry

@router.post("/backups/{backup_id}/verify")
async def verify_backup(backup_id: str, _=Depends(verify_token)):
    """校验备份文件完整性"""
    await handle_risk("L2", "校验备份", backup_id)
    records = _load_backups()
    for r in records:
        if r["id"] == backup_id:
            path = r.get("path", "")
            if not path or not os.path.exists(path):
                r["verified"] = False
                r["verify_error"] = "备份文件不存在"
                _save_backups(records)
                return {"backup_id": backup_id, "verified": False, "error": "文件不存在"}
            size = os.path.getsize(path)
            r["verified"] = size > 0
            r["verified_at"] = datetime.now().isoformat()
            _save_backups(records)
            return {"backup_id": backup_id, "verified": True, "size_mb": round(size / 1024 / 1024, 2)}
    raise HTTPException(404, "备份记录不存在")

@router.post("/backups/{backup_id}/rollback")
async def rollback(backup_id: str, _=Depends(verify_token)):
    """执行回滚操作"""
    records = _load_backups()
    for r in records:
        if r["id"] == backup_id:
            path = r.get("path", "")
            target = r.get("target", "database")

            risk = await handle_risk("L3", f"回滚操作: {r['name']}", f"目标: {target}, 文件: {path}")
            if not risk["allowed"]:
                return risk

            if not path or not os.path.exists(path):
                return {"backup_id": backup_id, "status": "failed", "error": "备份文件不存在"}

            result = {"success": False}
            if target == "database" and path.endswith(".sql"):
                # 恢复数据库
                if MALL_DB_HOST and MALL_DB_USER:
                    try:
                        cmd = f"mysql -h {MALL_DB_HOST} -P {MALL_DB_PORT} -u {MALL_DB_USER} -p{MALL_DB_PASSWORD} {MALL_DB_NAME} < {path} 2>&1"
                        r2 = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
                        result["success"] = r2.returncode == 0
                        result["output"] = r2.stdout[:200] or r2.stderr[:200]
                    except Exception as e:
                        result["error"] = str(e)
                else:
                    result["error"] = "数据库未配置"
            elif target == "nginx" and path.endswith(".tar.gz"):
                try:
                    cmd = f"tar xzf {path} -C / 2>&1 && nginx -t 2>&1 && echo ok || echo fail"
                    r2 = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                    result["success"] = "ok" in r2.stdout
                    result["output"] = r2.stdout[:200]
                except Exception as e:
                    result["error"] = str(e)
            else:
                result["info"] = "此类型的回滚需手动执行"

            return {
                "backup_id": backup_id,
                "status": "completed" if result["success"] else "failed",
                "result": result,
                "note": "回滚完成，请验证服务是否正常",
            }
    raise HTTPException(404, "备份记录不存在")

@router.delete("/backups/{backup_id}")
async def delete_backup(backup_id: str, _=Depends(verify_token)):
    """删除备份记录"""
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
    raise HTTPException(404, "备份记录不存在")

@router.post("/cleanup")
async def cleanup_old_backups(_=Depends(verify_token)):
    """清理过期备份（保留最近7天）"""
    await handle_risk("L2", "清理过期备份")
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
