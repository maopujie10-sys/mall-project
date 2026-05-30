"""AIAPI -- ++"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from auth import verify_token
from tools.fraud_detector import fraud_detector

router = APIRouter(prefix="/agent/fraud", tags=["FraudDetection"])


class OrderCheckRequest(BaseModel):
    id: str = ''
    amount: float = 0
    is_new_user: bool = False
    recent_order_count: int = 0
    same_ip_accounts: int = 0
    ip_country: str = ''
    ship_country: str = ''
    order_hour: int = 12
    category_avg_price: float = 0
    refund_rate: float = 0
    device_order_count: int = 1


class BatchCheckRequest(BaseModel):
    orders: list


@router.post("/check")
async def check_order(req: OrderCheckRequest, _=Depends(verify_token)):
    ''''''
    order = req.model_dump()
    result = await fraud_detector.analyze_order(order)
    return {"ok": True, "data": result}


@router.post("/quick-scan")
async def quick_scan(req: OrderCheckRequest, _=Depends(verify_token)):
    ''"(AI)''"
    result = fraud_detector.quick_scan(req.model_dump())
    return {"ok": True, "data": result}


@router.post("/batch")
async def batch_check(req: BatchCheckRequest, _=Depends(verify_token)):
    ''''''
    if not req.orders:
        raise HTTPException(400, '')
    if len(req.orders) > 100:
        raise HTTPException(400, "100")
    result = await fraud_detector.batch_analyze(req.orders)
    return {"ok": True, "data": result}


@router.get("/rules")
async def fraud_rules(_=Depends(verify_token)):
    ''''''
    return {"ok": True, "rules": fraud_detector.get_rules()}
