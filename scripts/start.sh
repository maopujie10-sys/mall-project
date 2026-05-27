#!/bin/bash
cd /opt/mall
docker-compose up -d
echo "=== 启动状态 ==="
docker-compose ps
