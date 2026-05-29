"""A/B测试 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tools.abtest_engine import abtest_engine
from auth import verify_token

router = APIRouter(prefix="/agent/abtest", tags=["ABTest"])

class CreateExp(BaseModel):
    name: str
    variants: list = ["A", "B"]

class AssignReq(BaseModel):
    exp_id: str
    user_id: str

class MetricReq(BaseModel):
    exp_id: str; variant: str; metric_name: str; value: float

@router.post("/create")
async def ab_create(req: CreateExp, _=Depends(verify_token)):
    exp_id = abtest_engine.create_experiment(req.name, req.variants)
    return {"ok": True, "exp_id": exp_id}

@router.post("/assign")
async def ab_assign(req: AssignReq, _=Depends(verify_token)):
    variant = abtest_engine.assign_variant(req.exp_id, req.user_id)
    return {"ok": True, "variant": variant}

@router.post("/metric")
async def ab_metric(req: MetricReq, _=Depends(verify_token)):
    abtest_engine.record_metric(req.exp_id, req.variant, req.metric_name, req.value)
    return {"ok": True}

@router.get("/analyze/{exp_id}")
async def ab_analyze(exp_id: str, _=Depends(verify_token)):
    return await abtest_engine.analyze(exp_id)

@router.get("/list")
async def ab_list(_=Depends(verify_token)):
    return {"ok": True, "experiments": abtest_engine.get_all_experiments()}
