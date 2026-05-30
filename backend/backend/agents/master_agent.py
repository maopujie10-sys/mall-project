"""Master Agent -- Friday AI OS centralized agent orchestrator"""
import json, httpx, time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from config import MALL_BASE_URL

@dataclass
class Task:
    id: str
    goal: str
    steps: list = field(default_factory=list)
    status: str = "pending"
    result: dict = field(default_factory=dict)
    created_at: str = ""
    completed_at: str = ""

# ===== Ecommerce & Mall Integration =====
ECOMMERCE_TOOLS = {
    "analyze_product": "Analyze product performance and suggest improvements",
    "check_inventory": "Check inventory levels and predict stockouts",
    "price_optimize": "Suggest optimal pricing based on competitors",
    "generate_listing": "Generate optimized product listing content",
    "customer_insight": "Analyze customer behavior and segments",
    "order_analysis": "Analyze order patterns and anomalies",
    "market_trend": "Identify trending products and categories",
}

MALL_TOOLS = {
    "get_products": "Query product catalog with filters",
    "get_orders": "Query orders with status and date filters",
    "get_users": "Query user list with search",
    "audit_product": "Approve or reject product listing",
    "handle_refund": "Process refund requests",
    "check_kyc": "Review KYC verification status",
    "view_logistics": "Track order logistics",
}

async def _execute_ecommerce(action, params, user="admin"):
    """Execute ecommerce AI actions via mall API"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            if action == "analyze_product":
                resp = await client.get(f"{MALL_BASE_URL}/api/products", params={"search": params.get("keyword", "")})
                return {"ok": True, "total": len(resp.json()) if resp.status_code == 200 else 0}
            elif action == "market_trend":
                resp = await client.get(f"{MALL_BASE_URL}/api/products/trending")
                return {"ok": True, "trends": resp.json() if resp.status_code == 200 else []}
            elif action == "order_analysis":
                resp = await client.get(f"{MALL_BASE_URL}/api/orders/stats")
                return {"ok": True, "stats": resp.json() if resp.status_code == 200 else {}}
            elif action == "customer_insight":
                resp = await client.get(f"{MALL_BASE_URL}/api/users/stats")
                return {"ok": True, "insights": resp.json() if resp.status_code == 200 else {}}
            else:
                return {"ok": False, "error": f"Unknown action: {action}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def _execute_mall(action, params, user="admin"):
    """Execute mall management actions via mall API"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            endpoints = {
                "get_products": ("GET", "/api/products"),
                "get_orders": ("GET", "/api/orders"),
                "get_users": ("GET", "/api/users"),
                "check_kyc": ("GET", "/api/kyc/list"),
            }
            if action in endpoints:
                method, url = endpoints[action]
                resp = await client.request(method, f"{MALL_BASE_URL}{url}", params=params)
                return {"ok": True, "data": resp.json()[:20] if resp.status_code == 200 else []}
            elif action == "audit_product":
                resp = await client.post(f"{MALL_BASE_URL}/api/product/audit", json=params)
                return {"ok": True, "result": resp.json()}
            elif action == "handle_refund":
                resp = await client.post(f"{MALL_BASE_URL}/api/order/refund/{params.get('order_id', '')}", json=params)
                return {"ok": True, "result": resp.json()}
            else:
                return {"ok": False, "error": f"Unknown action: {action}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ===== Mall -> Agent (webhook/listener) =====
MALL_EVENT_HANDLERS = {
    "order_created": "analyze_new_order",
    "product_listed": "check_product_quality",
    "user_registered": "welcome_new_user",
    "payment_received": "verify_transaction",
    "refund_requested": "auto_process_refund",
}

async def handle_mall_event(event_type, event_data):
    handler = MALL_EVENT_HANDLERS.get(event_type)
    if not handler:
        return {"ok": False, "error": f"No handler for {event_type}"}
    try:
        if event_type == "order_created":
            result = await _execute_mall("get_orders", {"status": "new"})
        elif event_type == "product_listed":
            result = await _execute_ecommerce("analyze_product", {"keyword": event_data.get("product_name", "")})
        elif event_type == "refund_requested":
            result = await _execute_mall("handle_refund", event_data)
        else:
            result = {"ok": True, "message": f"Event {event_type} processed"}
        try:
            from digital_lifeform import DigitalLifeform
            DigitalLifeform.record_interaction("mall_event", {"event": event_type, "result": "ok"})
        except: pass
        return result
    except Exception as e:
        return {"ok": False, "error": str(e)}

class MasterAgent:
    """Centralized agent orchestrator for Friday AI OS"""
    
    _tasks = []
    _task_counter = 0
    
    @classmethod
    async def execute(cls, agent_type, message, user="admin"):
        """Execute agent action. Supports: server, mall, devops, data, security, ecommerce, code"""
        cls._task_counter += 1
        task_id = f"task_{cls._task_counter}_{int(time.time())}"
        task = Task(id=task_id, goal=message[:100], status="running", created_at=datetime.now().isoformat())
        cls._tasks.append(task)
        
        try:
            if agent_type == "ecommerce":
                params = {"keyword": message}
                result = await _execute_ecommerce("analyze_product", params, user)
            elif agent_type == "mall":
                params = {"search": message}
                result = await _execute_mall("get_products", params, user)
            elif agent_type == "server":
                result = {"ok": True, "message": f"Server agent received: {message[:100]}"}
            elif agent_type == "devops":
                result = {"ok": True, "message": f"DevOps agent received: {message[:100]}"}
            elif agent_type == "data":
                result = {"ok": True, "message": f"Data agent received: {message[:100]}"}
            elif agent_type == "security":
                result = {"ok": True, "message": f"Security agent received: {message[:100]}"}
            elif agent_type == "code":

    @classmethod
    async def execute(cls, agent_type, message, user="admin"):
        """Execute agent action. Supports: server, mall, devops, data, security, ecommerce, code"""
        cls._task_counter += 1
        task_id = f"task_{cls._task_counter}_{int(time.time())}"
        task = Task(id=task_id, goal=message[:100], status="running", created_at=datetime.now().isoformat())
        cls._tasks.append(task)
        try:
            params = {"search": message, "keyword": message}
            if agent_type == "ecommerce":
                result = await _execute_ecommerce("analyze_product", params, user)
            elif agent_type == "mall":
                result = await _execute_mall("get_products", params, user)
            elif agent_type == "server":
                result = {"ok": True, "message": f"Server agent: {message[:100]}"}
            elif agent_type == "devops":
                result = {"ok": True, "message": f"DevOps agent: {message[:100]}"}
            elif agent_type == "data":
                result = {"ok": True, "message": f"Data agent: {message[:100]}"}
            elif agent_type == "security":
                result = {"ok": True, "message": f"Security agent: {message[:100]}"}
            else:
                result = {"ok": True, "message": f"Agent {agent_type}: {message[:100]}"}
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.now().isoformat()
            return result
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            return {"ok": False, "error": str(e)}

    @classmethod
    def get_tasks(cls, limit=20):
        return [{"id": t.id, "goal": t.goal, "status": t.status, "result": t.result} for t in cls._tasks[-limit:]]

    @classmethod
    def get_status(cls):
        return {"total": len(cls._tasks), "active": sum(1 for t in cls._tasks if t.status == "running"), "completed": sum(1 for t in cls._tasks if t.status == "completed"), "failed": sum(1 for t in cls._tasks if t.status == "failed")}

                result = {"ok": True, "message": f"Code agent received: {message[:100]}"}
            else:
                result = {"ok": False, "error": f"Unknown agent type: {agent_type}"}
            
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.now().isoformat()
            return result
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            task.completed_at = datetime.now().isoformat()
            return {"ok": False, "error": str(e)}
    
    @classmethod
    def get_tasks(cls, limit=20):
        return [t.__dict__ for t in cls._tasks[-limit:]]
    
    @classmethod
    def get_status(cls):
        return {
            "total_tasks": len(cls._tasks),
            "active": sum(1 for t in cls._tasks if t.status == "running"),
            "completed": sum(1 for t in cls._tasks if t.status == "completed"),
            "failed": sum(1 for t in cls._tasks if t.status == "failed"),
        }