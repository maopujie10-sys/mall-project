"""API Key 管理 API — 后台增删改查+热切换"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tools.key_manager import key_manager
from auth import verify_token

router = APIRouter(prefix="/agent/keys", tags=["APIKeys"])

class KeyRequest(BaseModel):
    env_key: str
    value: str
    name: str = ""
    description: str = ""

@router.get("/list")
async def keys_list(_=Depends(verify_token)):
    return {"ok": True, "keys": key_manager.get_all()}

@router.post("/set")
async def keys_set(req: KeyRequest, _=Depends(verify_token)):
    key_manager.set_key(req.env_key, req.value, req.name, req.description)
    return {"ok": True, "message": f"{req.env_key} 已保存"}

@router.delete("/{env_key}")
async def keys_delete(env_key: str, _=Depends(verify_token)):
    ok = key_manager.delete_key(env_key)
    return {"ok": ok, "message": "已删除" if ok else "不存在"}

@router.post("/toggle/{env_key}")
async def keys_toggle(env_key: str, _=Depends(verify_token)):
    ok = key_manager.toggle_key(env_key)
    return {"ok": ok, "message": "已切换" if ok else "不存在"}

@router.get("/status")
async def keys_status(_=Depends(verify_token)):
    return key_manager.get_status()
