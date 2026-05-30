"""Resilience utilities - Retry with backoff, timeout, circuit breaker"""
import asyncio
import functools
import time
from tools.logger import get_logger

logger = get_logger("resilience")

# Circuit breaker state
_circuit_state = {}

def with_retry(max_retries=3, base_delay=0.5, timeout=30):
    """Decorator: retry on exception with exponential backoff"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    last_error = TimeoutError(f"{func.__name__} timeout after {timeout}s")
                    logger.warning(f"Retry {attempt+1}/{max_retries}: {func.__name__} timeout")
                except Exception as e:
                    last_error = e
                    logger.warning(f"Retry {attempt+1}/{max_retries}: {func.__name__} {e}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
            raise last_error or RuntimeError(f"{func.__name__} failed after {max_retries} retries")
        return wrapper
    return decorator

def circuit_breaker(name, failure_threshold=5, recovery_timeout=60):
    """Circuit breaker: stop calling after N failures, auto-recover"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            state = _circuit_state.setdefault(name, {"failures": 0, "last_fail": 0, "open": False})
            if state["open"]:
                if time.time() - state["last_fail"] < recovery_timeout:
                    raise RuntimeError(f"Circuit {name} OPEN - too many failures")
                state["open"] = False
                state["failures"] = 0
                logger.info(f"Circuit {name} HALF-OPEN - testing")
            try:
                result = await func(*args, **kwargs)
                state["failures"] = 0
                return result
            except Exception as e:
                state["failures"] += 1
                state["last_fail"] = time.time()
                if state["failures"] >= failure_threshold:
                    state["open"] = True
                    logger.error(f"Circuit {name} OPEN - {state['failures']} failures")
                raise
        return wrapper
    return decorator

def safe_call(default=None):
    """Decorator: catch all exceptions and return default"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{func.__name__} failed: {e}")
                return default
        return wrapper
    return decorator
