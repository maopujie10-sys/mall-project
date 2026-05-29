"""冒烟测试 — 启动后验证所有核心功能"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

passed = 0
failed = 0

def check(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name}: {detail}")

async def main():
    global passed, failed
    print("=" * 50)
    print("Friday AI OS — 冒烟测试")
    print("=" * 50)
    
    # 1. 配置检查
    print("\n📋 配置检查")
    from config import AGENT_TOKEN, DB_CONFIG, REDIS_DSN
    check("AGENT_TOKEN已配置", len(AGENT_TOKEN) > 10 if AGENT_TOKEN else False)
    check("DB_HOST", bool(DB_CONFIG.get("host")))
    check("DB_NAME", bool(DB_CONFIG.get("name")))
    check("REDIS_DSN", bool(REDIS_DSN))
    
    # 2. 数据库连接
    print("\n🗄️ 数据库连接")
    try:
        import pymysql
        conn = pymysql.connect(host=DB_CONFIG["host"], port=DB_CONFIG["port"],
            user=DB_CONFIG["user"], password=DB_CONFIG["password"],
            database=DB_CONFIG["name"], connect_timeout=3)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        check("MySQL连接", True)
    except Exception as e:
        check("MySQL连接", False, str(e)[:80])
    
    # 3. Redis连接
    print("\n📦 Redis连接")
    try:
        import redis
        r = redis.from_url(REDIS_DSN, socket_connect_timeout=3)
        r.ping()
        r.close()
        check("Redis连接", True)
    except Exception as e:
        check("Redis连接", False, str(e)[:80])
    
    # 4. 路由注册
    print("\n🔀 路由注册")
    from main import app
    routes = [r.path for r in app.routes]
    check("健康检查 /agent/health", "/agent/health" in str(routes) or "/agent/health/" in str(routes))
    check("AI对话 /agent/chat", "/agent/chat" in str(routes))
    check("工具列表 /agent/tools", "/agent/tools" in str(routes))
    check("告警 /agent/alerts", "/agent/alerts" in str(routes) or "alert" in str(routes).lower())
    
    # 5. Agent可用性
    print("\n🤖 Agent检查")
    agents = ["code", "devops", "vision", "trend", "memory", "heal"]
    for a in agents:
        try:
            __import__(f"agents.{a}_agent", fromlist=[""])
            check(f"Agent: {a}", True)
        except Exception as e:
            check(f"Agent: {a}", False, str(e)[:60])
    
    # 6. 工具注册
    print("\n🔧 工具注册")
    from tools.registry import registry
    tools = registry.list_all()
    check(f"工具数量>50", len(tools) > 50, f"当前{len(tools)}个")
    check("scraper工具", any("scraper" in t.name for t in tools))
    check("health工具", any("health" in t.name for t in tools))
    
    # 7. 系统资源
    print("\n💻 系统资源")
    import psutil
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    check(f"CPU<95%", cpu < 95, f"当前{cpu}%")
    check(f"内存<95%", mem.percent < 95, f"当前{mem.percent}%")
    check(f"磁盘<95%", disk.percent < 95, f"当前{disk.percent}%")
    
    # 汇总
    print("\n" + "=" * 50)
    total = passed + failed
    if failed == 0:
        print(f"🎉 全部通过! {passed}/{total}")
    else:
        print(f"⚠️ {passed}/{total} 通过, {failed} 失败")
    print("=" * 50)
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
