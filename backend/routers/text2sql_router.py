"""Text-to-SQL API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from tools.text2sql import text2sql
from auth import verify_token

router = APIRouter(prefix="/agent/text2sql", tags=["Text2SQL"])

class SQLRequest(BaseModel):
    question: str

@router.post("/query")
async def sql_query(req: SQLRequest, _=Depends(verify_token)):
    result = await text2sql.query(req.question)
    if not result.get("ok"):
        result = text2sql.simple_query(req.question)
    return result
