"""Friday AI Stress Test - Load testing for critical endpoints"""
import asyncio, time, json, sys, os
import httpx

BASE = os.environ.get("BASE_URL", "http://localhost:8000")
TOKEN = os.environ.get("AGENT_TOKEN", "friday-agent-token")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

results = {"pass": 0, "fail": 0, "times": {}}

async def test(name, method="GET", path="/", body=None, expected_status=200, timeout=15):
    """Run a single endpoint test and record timing"""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=timeout) as c:
            if method == "GET":
                r = await c.get(f"{BASE}{path}", headers=HEADERS)
            else:
                r = await c.post(f"{BASE}{path}", json=body, headers=HEADERS)
            elapsed = round((time.time() - start) * 1000, 1)
            ok = r.status_code == expected_status
            if ok:
                results["pass"] += 1
            else:
                results["fail"] += 1
            results["times"][name] = f"{elapsed}ms {'OK' if ok else 'FAIL('+str(r.status_code)+')'}"
            return ok
    except Exception as e:
        results["fail"] += 1
        results["times"][name] = f"ERROR: {str(e)[:60]}"
        return False

async def concurrent_test(name, path, n=10):
    """Run N concurrent requests to the same endpoint"""
    start = time.time()
    tasks = [test(f"{name}[{i}]", path=path) for i in range(n)]
    await asyncio.gather(*tasks)
    total = round((time.time() - start) * 1000, 1)
    results["times"][f"{name} x{n}"] = f"{total}ms total"

async def main():
    print(f"Friday AI Stress Test - {BASE}")
    print("=" * 50)

    # Health checks
    await test("health_root", path="/")
    await test("health_docs", path="/docs")
    await test("agent_status", path="/agent/status")

    # Agent endpoints
    await test("master_status", path="/agent/master/status")
    await test("lifeform_status", path="/agent/lifeform/status")
    await test("registry_tools", path="/agent/tools")
    await test("model_list", path="/agent/models")

    # RAG
    await test("rag_stats", path="/agent/rag/stats")
    await test("rag_search", path="/agent/rag/search?q=test")

    # Plugins
    await test("plugins_list", path="/agent/plugins")
    await test("plugins_categories", path="/agent/plugins/categories")

    # Workflow
    await test("workflow_templates", path="/agent/workflow/templates")
    await test("workflow_list", path="/agent/workflow/list")

    # Voice
    await test("voice_tts", method="POST", path="/agent/voice/tts",
              body={"text":"hello test","voice":"alloy"}, expected_status=200)

    # Video
    await test("video_types_not_impl", path="/agent/video/analyze-image?image_url=test")

    # Server panel
    await test("server_status", path="/server/status")
    await test("docker_ps", path="/server/docker/ps")

    # Mall
    await test("mall_products", path="/mall/products?page=1&size=10")
    await test("mall_brain", path="/agent/mall/brain/status")

    # Brain
    await test("brain_status", path="/agent/brain/status")

    # Rotation
    await test("rotation_status", path="/rotation/status")

    # Concurrent load tests
    await concurrent_test("health_concurrent", "/", 20)
    await concurrent_test("agent_concurrent", "/agent/status", 10)

    # Report
    print("\n" + "=" * 50)
    total = results["pass"] + results["fail"]
    print(f"Results: {results['pass']}/{total} passed, {results['fail']} failed")
    print(f"Success rate: {round(results['pass']/total*100,1)}%" if total else "N/A")
    print("\nTimings:")
    for k, v in sorted(results["times"].items()):
        print(f"  {k}: {v}")

    return 0 if results["fail"] == 0 else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
