"""工具注册中心 — 所有AI可调用工具的统一注册与管理"""
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class ToolDef:
    """工具定义"""
    name: str
    display_name: str
    description: str
    risk_level: str
    category: str
    params_schema: dict = field(default_factory=dict)
    need_confirm: bool = False
    need_backup: bool = False
    rollback_supported: bool = False


class ToolRegistry:
    """工具注册中心"""

    def __init__(self):
        self._tools: dict[str, ToolDef] = {}

    def register(self, tool: ToolDef):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[ToolDef]:
        return self._tools.get(name)

    def list_all(self) -> list[ToolDef]:
        return list(self._tools.values())

    def list_by_category(self, category: str) -> list[ToolDef]:
        return [t for t in self._tools.values() if t.category == category]

    def list_by_risk(self, level: str) -> list[ToolDef]:
        return [t for t in self._tools.values() if t.risk_level == level]


# 全局单例
registry = ToolRegistry()


def register_builtin_tools():
    """注册所有内置工具"""
    tools = [
        # ===== 服务器 =====
        ToolDef("server.status", "服务器状态", "查看CPU/内存/磁盘/负载", "L1", "server"),
        ToolDef("server.ports", "端口列表", "查看服务器监听端口", "L1", "server"),
        ToolDef("server.processes", "进程列表", "查看占用CPU最高的进程", "L1", "server"),
        ToolDef("server.disk", "磁盘详情", "查看磁盘分区使用详情", "L1", "server"),

        # ===== Docker =====
        ToolDef("docker.list", "容器列表", "查看所有Docker容器", "L1", "docker"),
        ToolDef("docker.logs", "容器日志", "查看指定容器的日志", "L1", "docker", params_schema={"container_id": {"type": "string"}}),
        ToolDef("docker.status", "Docker状态", "查看容器运行状态统计", "L1", "docker"),
        ToolDef("docker.restart", "重启容器", "重启指定Docker容器", "L3", "docker", need_confirm=True),
        ToolDef("docker.images", "镜像列表", "查看Docker镜像列表", "L1", "docker"),
        ToolDef("docker.network", "网络列表", "查看Docker网络列表", "L1", "docker"),
        ToolDef("docker.stats", "资源占用", "查看容器CPU/内存占用", "L1", "docker"),
        ToolDef("docker.compose", "Compose状态", "查看docker compose服务状态", "L1", "docker"),

        # ===== Nginx =====
        ToolDef("nginx.status", "Nginx状态", "检查Nginx进程状态", "L1", "nginx"),
        ToolDef("nginx.test", "Nginx配置测试", "测试Nginx配置文件语法", "L1", "nginx"),
        ToolDef("nginx.logs", "Nginx日志", "查看Nginx错误/访问日志", "L1", "nginx"),
        ToolDef("nginx.reload", "重载Nginx", "重新加载Nginx配置", "L3", "nginx", need_confirm=True),

        # ===== 网站检测 =====
        ToolDef("site.check", "网站检测", "检测域名是否可以访问", "L1", "site", params_schema={"url": {"type": "string"}}),
        ToolDef("site.ssl", "SSL检测", "检测SSL证书信息", "L1", "site", params_schema={"domain": {"type": "string"}}),
        ToolDef("site.dns", "DNS检测", "检测域名DNS解析", "L1", "site"),

        # ===== 系统 =====
        ToolDef("system.mode", "系统模式", "查看当前系统运行模式", "L1", "system"),
        ToolDef("system.emergency", "紧急停止", "切换为人工接管模式", "L3", "system", need_confirm=True),

        # ===== 备份 =====
        ToolDef("backup.list", "备份列表", "查看所有备份记录", "L1", "backup"),
        ToolDef("backup.create", "创建备份", "创建数据库/配置/项目备份", "L2", "backup"),
        ToolDef("backup.verify", "校验备份", "校验备份文件完整性", "L2", "backup"),
        ToolDef("backup.rollback", "回滚", "从备份恢复数据", "L3", "backup", need_confirm=True, need_backup=True, rollback_supported=True),
        ToolDef("backup.cleanup", "清理备份", "清理过期备份", "L2", "backup"),

        # ===== 通知 =====
        ToolDef("notify.config", "通知配置", "查看通知渠道配置状态", "L1", "notify"),
        ToolDef("notify.send", "发送通知", "发送消息到通知渠道", "L2", "notify"),

        # ===== 轮值 =====
        ToolDef("rotation.list", "轮值列表", "查看所有轮值域名", "L1", "rotation"),
        ToolDef("rotation.check", "轮值检测", "检测所有轮值域名可访问性", "L1", "rotation"),
        ToolDef("rotation.toggle", "域名切换", "启用/停用轮值域名", "L3", "rotation", need_confirm=True),

        # ===== 客服 =====
        ToolDef("customer.messages", "客服消息", "查看最近客服消息", "L1", "customer"),
        ToolDef("customer.reply", "回复消息", "回复客户消息", "L2", "customer"),

        # ===== 商城 =====
        ToolDef("mall.products", "商品列表", "查看商城所有商品", "L1", "mall"),
        ToolDef("mall.orders", "订单列表", "查看商城最近订单", "L1", "mall"),
        ToolDef("mall.inventory", "库存查询", "查看商品库存状态", "L1", "mall"),
        ToolDef("mall.adjust_price", "调整价格", "批量调整商品价格", "L3", "mall", need_confirm=True),

        # ===== Runbook =====
        ToolDef("runbook.list", "Runbook列表", "查看所有运维Runbook", "L1", "runbook"),
        ToolDef("runbook.disk_full", "磁盘清理", "自动清理磁盘释放空间", "L2", "runbook"),
        ToolDef("runbook.rotation_check", "域名巡检", "巡检所有轮值域名状态", "L1", "runbook"),

        # ===== 自动化运营 =====
        ToolDef("autopilot.visit", "自动养站", "模拟访问商城页面保持活跃度", "L2", "autopilot"),
        ToolDef("autopilot.sitemap", "SEO优化", "生成SEO站点地图", "L1", "autopilot"),
        ToolDef("autopilot.logs", "养站日志", "查看自动养站操作日志", "L1", "autopilot"),

        # ===== 日报/趋势 =====
        ToolDef("report.daily", "运营日报", "生成每日运营数据报告", "L2", "report"),
        ToolDef("report.trend", "趋势分析", "分析异常数据趋势", "L1", "report"),

        # ===== 数据库 =====
        ToolDef("db.status", "数据库状态", "检查数据库连接状态", "L1", "db"),
        ToolDef("db.schema", "数据库结构", "查看数据库表结构", "L1", "db"),
        ToolDef("db.query", "SQL查询", "执行只读SQL查询（受保护）", "L2", "db"),
        ToolDef("db.tables", "表列表", "查看所有数据库表", "L1", "db"),

        # ===== 采集(基础) =====
        ToolDef("scraper.sources", "采集源", "查看图片采集源列表", "L1", "scraper"),
        ToolDef("scraper.collect", "图片采集", "从网页采集商品图片", "L1", "scraper"),

        # ===== 安全 =====
        ToolDef("security.block_ip", "封禁IP", "封禁指定IP地址", "L3", "security", need_confirm=True),
        ToolDef("security.unblock_ip", "解封IP", "解封指定IP地址", "L3", "security", need_confirm=True),

        # ===== 巡检 =====
        ToolDef("inspector.run", "执行巡检", "手动触发全量系统巡检", "L2", "inspector"),

        # ===== Playwright 浏览器自动化 =====
        ToolDef("playwright.screenshot", "网页截图", "对指定URL全页截图", "L1", "playwright", params_schema={"url": {"type": "string"}}),
        ToolDef("playwright.scrape", "抓取网页", "抓取网页内容(标题/链接/图片/价格)", "L1", "playwright", params_schema={"url": {"type": "string"}}),
        ToolDef("playwright.search", "搜索商品", "在eBay/Amazon搜索并抓取商品", "L2", "playwright", params_schema={"keyword": {"type": "string"}, "site": {"type": "string"}}),
        ToolDef("playwright.form", "填写表单", "自动填表并截图", "L2", "playwright", need_confirm=True),
        ToolDef("inspector.history", "巡检历史", "查看巡检历史记录", "L1", "inspector"),

        # ===== 企业级采集 =====
        ToolDef("scraper.start", "启动商品采集", "从eBay/AliExpress采集完整商品数据（标题/价格/规格/SKU/图片），自动上传COS", "L2", "scraper", need_confirm=True),
        ToolDef("scraper.jobs", "采集任务列表", "查看所有采集任务进度", "L1", "scraper"),
        ToolDef("scraper.products", "采集商品库", "浏览已采集的商品，可筛选待导入/已上传", "L1", "scraper"),
        ToolDef("scraper.import", "导入到商城", "将采集的商品批量导入商城商品库", "L3", "scraper", need_confirm=True),
        ToolDef("scraper.upload", "上传产品图片", "将采集的图片上传到腾讯云COS", "L1", "scraper"),

        # ===== 虚拟数据 =====
        ToolDef("virtual.generate", "生成虚拟数据", "一键生成用户/商品/订单/K线/客服数据，让商城看起来像真实大平台", "L3", "virtual", need_confirm=True),
        ToolDef("virtual.realtime", "实时活动模拟", "模拟在线用户活动：浏览/下单/签到，让平台看起来有人", "L2", "virtual"),
        ToolDef("virtual.dashboard", "数据看板", "实时统计：今日新增/交易额/在线人数", "L1", "virtual"),
        ToolDef("virtual.stats", "数据统计", "查看已生成的虚拟数据总量", "L1", "virtual"),

        # ===== AI 商城大脑 =====
        ToolDef("mallbrain.scan", "AI扫描商品", "AI分析全站商品健康度：热销/正常/冷门/死品", "L1", "brain"),
        ToolDef("mallbrain.report", "AI运营报告", "AI生成完整运营分析报告：品类缺口/库存建议/替换建议", "L1", "brain"),
        ToolDef("mallbrain.auto", "AI自动运维", "AI自动执行：下架死品/采集新品/补充库存/优化价格", "L3", "brain", need_confirm=True, need_backup=True, rollback_supported=True),
        ToolDef("mallbrain.gaps", "品类缺口分析", "AI发现哪些品类商品太少需要补充", "L1", "brain"),
        ToolDef("mallbrain.summary", "AI大脑总结", "一目了然：商城健康度/待处理事项", "L1", "brain"),

        # ===== AI 自我进化 =====
        ToolDef("evolution.report", "进化报告", "AI自我评估：成功率趋势、学到的知识、进化建议", "L1", "evolution"),
        ToolDef("evolution.history", "行动历史", "查看AI历史行动记录：采集/替换/健康检查等", "L1", "evolution"),
        ToolDef("evolution.rate", "成功率查询", "查询AI各类行动的成功率（30天/7天）", "L1", "evolution"),
        ToolDef("evolution.learn", "学习纠正", "让AI从用户纠正中学习，记住正确做法", "L2", "evolution"),
        ToolDef("evolution.knowledge", "知识库", "查看AI已学到的知识：最佳采集源/品类偏好等", "L1", "evolution"),
    ]

    for t in tools:
        registry.register(t)
