锘?""鍐掔儫娴嬭瘯 鈥?鍚姩鍚庨獙璇佹墍鏈夋牳蹇冨姛鑳?""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

passed = 0
failed = 0

def check(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  鉁?{name}")
    else:
        failed += 1
        print(f"  鉂?{name}: {detail}")

async def main():
    global passed, failed
    print("=" * 50)
    print("Friday AI OS 鈥?鍐掔儫娴嬭瘯")
    print("=" * 50)
    
    # 1. 閰嶇疆妫€鏌?    print("\n馃搵 閰嶇疆妫€鏌?)
    from config import AGENT_TOKEN, DB_CONFIG, REDIS_DSN
    check("AGENT_TOKEN宸查厤缃?, len(AGENT_TOKEN) > 10 if AGENT_TOKEN else False)
    check("DB_HOST", bool(DB_CONFIG.get("host")))
    check("DB_NAME", bool(DB_CONFIG.get("name")))
    check("REDIS_DSN", bool(REDIS_DSN))
    
    # 2. 鏁版嵁搴撹繛鎺?    print("\n馃梽锔?鏁版嵁搴撹繛鎺?)
    try:
        import pymysql
        conn = pymysql.connect(host=DB_CONFIG["host"], port=DB_CONFIG["port"],
            user=DB_CONFIG["user"], password=DB_CONFIG["password"],
            database=DB_CONFIG["name"], connect_timeout=3)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        check("MySQL杩炴帴", True)
    except Exception as e:
        check("MySQL杩炴帴", False, str(e)[:80])
    
    # 3. Redis杩炴帴
    print("\n馃摝 Redis杩炴帴")
    try:
        import redis
        r = redis.from_url(REDIS_DSN, socket_connect_timeout=3)
        r.ping()
        r.close()
        check("Redis杩炴帴", True)
    except Exception as e:
        check("Redis杩炴帴", False, str(e)[:80])
    
    # 4. 璺敱娉ㄥ唽
    print("\n馃攢 璺敱娉ㄥ唽")
    from main import app
    routes = [r.path for r in app.routes]
    check("鍋ュ悍妫€鏌?/agent/health", "/agent/health" in str(routes) or "/agent/health/" in str(routes))
    check("AI瀵硅瘽 /agent/chat", "/agent/chat" in str(routes))
    check("宸ュ叿鍒楄〃 /agent/tools", "/agent/tools" in str(routes))
    check("鍛婅 /agent/alerts", "/agent/alerts" in str(routes) or "alert" in str(routes).lower())
    
    # 5. Agent鍙敤鎬?    print("\n馃 Agent妫€鏌?)
    agents = ["code", "devops", "vision", "trend", "memory", "heal"]
    for a in agents:
        try:
            __import__(f"agents.{a}_agent", fromlist=[""])
            check(f"Agent: {a}", True)
        except Exception as e:
            check(f"Agent: {a}", False, str(e)[:60])
    
    # 6. 宸ュ叿娉ㄥ唽
    print("\n馃敡 宸ュ叿娉ㄥ唽")
    from tools.registry import registry
    tools = registry.list_all()
    check(f"宸ュ叿鏁伴噺>50", len(tools) > 50, f"褰撳墠{len(tools)}涓?)
    check("scraper宸ュ叿", any("scraper" in t.name for t in tools))
    check("health宸ュ叿", any("health" in t.name for t in tools))
    
    # 7. 绯荤粺璧勬簮
    print("\n馃捇 绯荤粺璧勬簮")
    import psutil
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    check(f"CPU<95%", cpu < 95, f"褰撳墠{cpu}%")
    check(f"鍐呭瓨<95%", mem.percent < 95, f"褰撳墠{mem.percent}%")
    check(f"纾佺洏<95%", disk.percent < 95, f"褰撳墠{disk.percent}%")
    
    # 姹囨€?    print("\n" + "=" * 50)
    total = passed + failed
    if failed == 0:
        print(f"馃帀 鍏ㄩ儴閫氳繃! {passed}/{total}")
    else:
        print(f"鈿狅笍 {passed}/{total} 閫氳繃, {failed} 澶辫触")
    print("=" * 50)
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
