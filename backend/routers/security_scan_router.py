"""安全扫描 API"""
from fastapi import APIRouter, Depends
from tools.security_scanner import security_scanner
from auth import verify_token

router = APIRouter(prefix="/agent/security-scan", tags=["SecurityScan"])

@router.post("/full")
async def scan_full(_=Depends(verify_token)):
    return await security_scanner.full_scan()

@router.get("/quick")
async def scan_quick(_=Depends(verify_token)):
    checks = [await security_scanner.check_env_leaks(), await security_scanner.check_auth_config()]
    return {"ok": True, "checks": checks}
