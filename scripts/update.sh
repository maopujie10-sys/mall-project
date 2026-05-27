#!/bin/bash
set -e
cd /opt/mall
echo "备份当前版本..."
./scripts/backup.sh
echo "更新mall-app..."
docker-compose up -d --no-deps --build mall-app
sleep 15
STATUS=$(curl -s http://localhost:8080/agent/health -H "X-Agent-Token: ${AGENT_TOKEN}" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['status'])" 2>/dev/null || echo "fail")
if [ "$STATUS" = "running" ]; then
    echo "更新成功"
else
    echo "更新失败，自动回滚..."
    docker-compose up -d --no-deps mall-app
fi
