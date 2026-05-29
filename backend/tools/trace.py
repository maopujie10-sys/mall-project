锘?""鍏ㄩ摼璺姹傝拷韪?+ 鍏ㄥ眬寮傚父澶勭悊 鈥?trace_id璐┛姣忎釜璇锋眰,鍑洪棶棰樼瀹氫綅"""
import time, uuid, traceback, json
from datetime import datetime
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from tools.logger import get_logger

logger = get_logger("trace")

# 璇锋眰杩借釜瀛樺偍锛堢幆褰㈢紦鍐插尯锛?
_trace_buffer = []
MAX_TRACE = 1000
_slow_threshold_ms = 1000  # 鎱㈣姹傞槇鍊?


class TraceContext:
    """璇锋眰杩借釜涓婁笅鏂?""
    __slots__ = ("trace_id", "path", "method", "start_time", "status", "error")

    def __init__(self, trace_id: str = ""):
        self.trace_id = trace_id or self._gen_id()
        self.path = ""
        self.method = ""
        self.start_time = 0.0
        self.status = "processing"
        self.error = ""

    @staticmethod
    def _gen_id() -> str:
        return uuid.uuid4().hex[:12]

    def to_dict(self) -> dict:
        elapsed = round((time.time() - self.start_time) * 1000, 1) if self.start_time else 0
        return {
            "trace_id": self.trace_id,
            "path": self.path,
            "method": self.method,
            "elapsed_ms": elapsed,
            "status": self.status,
            "error": self.error[:200] if self.error else "",
            "time": datetime.now().isoformat(),
        }


async def trace_middleware(request: Request, call_next):
    """鍏ㄩ摼璺姹傝拷韪腑闂翠欢 鈥?姣忎釜璇锋眰鍒嗛厤trace_id"""
    trace_ctx = TraceContext()
    trace_ctx.path = request.url.path
    trace_ctx.method = request.method
    trace_ctx.start_time = time.time()

    # 娉ㄥ叆trace_id鍒皉equest state
    request.state.trace_id = trace_ctx.trace_id
    request.state.trace_start = trace_ctx.start_time

    # 璁板綍璇锋眰
    logger.info(f"[{trace_ctx.trace_id}] 鈫?{request.method} {request.url.path}")

    try:
        response = await call_next(request)
        elapsed = round((time.time() - trace_ctx.start_time) * 1000, 1)
        trace_ctx.status = "ok"

        # 鍦ㄥ搷搴斿ご娉ㄥ叆trace_id
        response.headers["X-Trace-Id"] = trace_ctx.trace_id
        response.headers["X-Response-Time-Ms"] = str(elapsed)

        # 鎱㈣姹傚憡璀?
        if elapsed > _slow_threshold_ms:
            logger.info(f"[{trace_ctx.trace_id}] 鈿狅笍 鎱㈣姹?{elapsed}ms {request.url.path}")
            trace_ctx.status = "slow"

        _add_trace(trace_ctx.to_dict())
        return response

    except Exception as e:
        elapsed = round((time.time() - trace_ctx.start_time) * 1000, 1)
        trace_ctx.status = "error"
        trace_ctx.error = str(e)[:500]
        _add_trace(trace_ctx.to_dict())

        # 鍏ㄥ眬寮傚父澶勭悊
        logger.info(f"[{trace_ctx.trace_id}] 鉂?寮傚父 {elapsed}ms {request.url.path}: {str(e)[:200]}")
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "鏈嶅姟鍣ㄥ唴閮ㄩ敊璇?,
                "trace_id": trace_ctx.trace_id,
                "detail": str(e)[:200] if isinstance(e, (ValueError, KeyError, TypeError)) else "璇锋煡鐪嬫棩蹇?,
            },
            headers={"X-Trace-Id": trace_ctx.trace_id}
        )


def _add_trace(trace_dict: dict):
    """娣诲姞杩借釜璁板綍鍒扮幆褰㈢紦鍐插尯"""
    global _trace_buffer
    _trace_buffer.append(trace_dict)
    if len(_trace_buffer) > MAX_TRACE:
        _trace_buffer = _trace_buffer[-MAX_TRACE:]


def get_recent_traces(limit: int = 100, status_filter: str = "") -> list:
    """鑾峰彇鏈€杩戣拷韪褰?""
    traces = list(_trace_buffer)
    if status_filter:
        traces = [t for t in traces if t.get("status") == status_filter]
    return traces[-limit:]


def get_trace_stats() -> dict:
    """杩借釜缁熻"""
    if not _trace_buffer:
        return {"total": 0}
    total = len(_trace_buffer)
    ok = sum(1 for t in _trace_buffer if t.get("status") == "ok")
    errors = sum(1 for t in _trace_buffer if t.get("status") == "error")
    slow = sum(1 for t in _trace_buffer if t.get("status") == "slow")
    elapsed = [t.get("elapsed_ms", 0) for t in _trace_buffer if t.get("elapsed_ms")]
    return {
        "total_requests": total,
        "ok": ok,
        "errors": errors,
        "slow_requests": slow,
        "error_rate": round(errors / max(total, 1), 4),
        "avg_response_ms": round(sum(elapsed) / max(len(elapsed), 1), 1) if elapsed else 0,
        "max_response_ms": round(max(elapsed), 1) if elapsed else 0,
        "p99_response_ms": round(sorted(elapsed)[int(len(elapsed)*0.99)], 1) if len(elapsed) > 100 else (max(elapsed) if elapsed else 0),
    }
