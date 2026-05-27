"""Agent Controller — 意图识别/工具匹配/任务编排"""
import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import verify_token
from state import state
from risk import handle_risk
from tools.registry import registry
from config import MALL_BASE_URL

router = APIRouter(prefix="/agent", tags=["Agent"])

class ChatRequest(BaseModel):
    message: str

class ConfirmRequest(BaseModel):
    taskId: str
    approved: bool

class HandoverRequest(BaseModel):
    reason: str = ""

# ===== 意图匹配规则 =====
INTENT_RULES = [
    # 服务器
    (["服务器状态", "服务器", "server status", "cpu", "内存", "负载"], "server.status", "L1"),
    (["端口", "端口列表"], "server.ports", "L1"),
    (["进程", "占用"], "server.processes", "L1"),

    # Docker
    (["docker", "容器"], "docker.list", "L1"),
    (["容器日志", "docker日志"], "docker.logs", "L1"),
    (["重启", "restart"], "docker.restart", "L2"),

    # Nginx
    (["nginx状态", "nginx状态"], "nginx.status", "L1"),
    (["nginx配置", "nginx -t"], "nginx.test", "L1"),
    (["nginx日志"], "nginx.logs", "L1"),
    (["重载nginx", "reload nginx"], "nginx.reload", "L2"),

    # 网站
    (["网站检测", "网站检查", "能不能访问", "打不开"], "site.check", "L1"),
    (["ssl", "证书"], "site.ssl", "L1"),
    (["dns", "域名解析"], "site.dns", "L1"),

    # 系统
    (["当前模式", "系统模式", "什么模式"], "system.mode", "L1"),
    (["紧急", "停止"], "system.emergency", "L2"),

    # 备份
    (["备份列表", "有哪些备份"], "backup.list", "L1"),
    (["创建备份", "备份一下"], "backup.create", "L2"),

    # 通知
    (["通知配置"], "notify.config", "L1"),

    # 轮值
    (["轮值列表", "轮值域名"], "rotation.list", "L1"),
    (["轮值检测"], "rotation.check", "L1"),
    (["域名切换", "停用域名", "启用域名"], "rotation.toggle", "L2"),

    # 客服
    (["客服消息", "客户消息"], "customer.messages", "L1"),

    # 商城
    (["商品列表", "商城商品"], "mall.products", "L1"),
    (["订单列表", "商城订单"], "mall.orders", "L1"),

    # 通用
    (["help", "帮助", "支持"], "_help", "L1"),
    (["状态", "status", "概况"], "site.check", "L1"),

    # 采集
    (["采集", "采集商品", "爬虫", "抓取商品", "帮我采集"], "scraper.start", "L2"),
    (["采集任务", "采集进度"], "scraper.jobs", "L1"),
    (["采集结果", "已采集", "采集商品列表", "采集库"], "scraper.products", "L1"),
    (["导入商品", "上架采集", "导入商城"], "scraper.import", "L3"),
    (["上传图片", "上传COS", "图片传云"], "scraper.upload", "L1"),

    # 虚拟数据
    (["生成数据","造数据","虚拟数据","填充数据","模拟数据","造假数据","生成用户","生成商品"], "virtual.generate", "L3"),
    (["实时活动","模拟在线","模拟用户","在线人数","活跃度"], "virtual.realtime", "L2"),
    (["数据看板","今日统计","平台数据","交易额","在线"], "virtual.dashboard", "L1"),
    (["数据统计","虚拟数据统计"], "virtual.stats", "L1"),

    # AI 商城大脑
    (["AI运维","自动运维","帮我运维","商城大脑","AI管理商城","全自动运营"], "mallbrain.summary", "L1"),
    (["扫描商品","商品健康","哪些产品好卖","产品分析","商品分析","热销","死品","好不好卖"], "mallbrain.scan", "L1"),
    (["运营报告","商城报告","分析报告","诊断商城","商城诊断","运营分析"], "mallbrain.report", "L1"),
    (["自动执行","自动优化","自动替换","自动补货","AI自动管理"], "mallbrain.auto", "L3"),
    (["品类缺口","哪些品类少","缺什么","补充品类"], "mallbrain.gaps", "L1"),

    # AI 自我进化
    (["进化报告","AI学得怎么样","AI表现","进化状态","自我评估"], "evolution.report", "L1"),
    (["行动历史","AI做了什么","历史记录","执行记录","操作日志"], "evolution.history", "L1"),
    (["成功率","AI行不行","准确率","成功多少"], "evolution.rate", "L1"),
    (["AI学习","记住","纠正","学一下","记住这个","下次注意"], "evolution.learn", "L2"),
    (["知识库","AI知道什么","学了什么","AI知识"], "evolution.knowledge", "L1"),
]


def _match_intent(message: str) -> tuple:
    """匹配用户意图，返回 (tool_name, risk_level) 或 (None, None)"""
    msg_lower = message.lower()
    for keywords, tool_name, risk_level in INTENT_RULES:
        for kw in keywords:
            if kw.lower() in msg_lower:
                return tool_name, risk_level
    # 模糊匹配
    if "?" in msg_lower or "？" in msg_lower:
        for keywords, tool_name, risk_level in INTENT_RULES:
            if len(keywords) > 0 and len(keywords[0]) > 0:
                for kw in keywords:
                    if len(kw) >= 2 and kw[:2] in msg_lower:
                        return tool_name, risk_level
    return None, None


@router.post("/chat")
async def agent_chat(req: ChatRequest, _=Depends(verify_token)):
    """AI对话入口 — 自动意图识别并响应"""
    tool_name, risk_level = _match_intent(req.message)

    if tool_name is None:
        tool_name = "_unknown"
        risk_level = "L1"

    tool_def = registry.get(tool_name)

    if tool_name == "_help":
        tools = registry.list_all()
        lines = [f"**可用工具 ({len(tools)}个):**"]
        for t in tools:
            lines.append(f"- [{t.risk_level}] **{t.display_name}** — {t.description}")
        response_text = "\n".join(lines)

    elif tool_name == "_tasks":
        response_text = f"任务: {len(state.tasks)}个, 待审批: {len(state.pending_approvals)}个"

    elif tool_name == "_approvals":
        response_text = f"待审批: {len(state.pending_approvals)}个, 历史: {len(state.approval_history)}个"

    elif tool_name == "_unknown":
        response_text = (
            f"🤔 未识别: {req.message[:50]}...\n"
            f"未识别到明确意图，试试说 help 查看可用工具~\n"
            f"示例: 查看服务器状态 / docker容器 / nginx状态 / 网站检测 / 备份"
        )

    else:
        category_names = {
            "server": "服务器", "docker": "Docker", "nginx": "Nginx",
            "site": "网站检测", "system": "系统", "backup": "备份",
            "notify": "通知", "rotation": "轮值", "customer": "客服",
            "mall": "商城", "scraper": "采集", "virtual": "虚拟数据",
            "brain": "AI大脑", "evolution": "AI进化",
        }
        cat = category_names.get(tool_def.category, tool_def.category) if tool_def else "未知"
        steps = [
            {"step": 1, "name": f"识别意图: {tool_def.display_name if tool_def else tool_name}", "status": "done"},
            {"step": 2, "name": f"风险评估: {risk_level}", "status": "done"},
            {"step": 3, "name": f"调用 {cat} 工具", "status": "pending"},
        ]
        response_text = (
            f"**意图**: {tool_def.display_name if tool_def else tool_name}\n"
            f"**类别**: {cat}\n"
            f"**风险等级**: {risk_level}\n"
        )
        if risk_level == "L1":
            response_text += "**状态**: AI 直接执行中..."
        elif risk_level == "L2":
            response_text += "**状态**: 直接执行，记录日志中..."
        elif risk_level == "L3":
            response_text += "**状态**: ⚠ 需要人工确认，当前需审批方可执行"
        elif risk_level == "L4":
            response_text += "**状态**: 🚨 极高风险，强制人工接管，AI不执行"
        else:
            response_text += "**状态**: 🚨 极高风险，强制人工接管"

    return {
        "task_id": f"task_{len(state.tasks)+1}",
        "response": response_text,
        "steps": steps,
        "risk_level": risk_level,
        "mode": state.mode,
    }


@router.get("/tools")
async def list_tools(_=Depends(verify_token)):
    """查看所有注册的工具"""
    tools = registry.list_all()
    return {
        "tools": [
            {
                "name": t.name,
                "display_name": t.display_name,
                "description": t.description,
                "risk_level": t.risk_level,
                "category": t.category,
            }
            for t in tools
        ],
        "count": len(tools),
    }


@router.get("/tasks")
async def list_tasks(_=Depends(verify_token)):
    await handle_risk("L1", "查看任务列表")
    return {"tasks": state.tasks[-50:], "count": len(state.tasks)}

@router.get("/tasks/{task_id}")
async def task_detail(task_id: str, _=Depends(verify_token)):
    await handle_risk("L1", "查看任务详情", task_id)
    for t in state.tasks:
        if t["id"] == task_id:
            return t
    return {"error": "任务不存在"}

@router.post("/confirm")
async def confirm_task(req: ConfirmRequest, _=Depends(verify_token)):
    result = state.decide_approval(req.taskId, req.approved)
    return {"result": "ok" if result else "not found", "detail": result}

@router.post("/handover")
async def handover(req: HandoverRequest, _=Depends(verify_token)):
    state.mode = "human_control"
    state.add_emergency("human_control", req.reason or "用户请求人工接管")
    return {"mode": "human_control", "reason": req.reason}

@router.post("/resume")
async def resume_ai(_=Depends(verify_token)):
    state.mode = "ai_control"
    state.add_emergency("ai_control", "用户恢复AI接管")
    return {"mode": "ai_control"}
