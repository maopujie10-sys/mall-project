#!/bin/bash
set -e
echo "===== 1. 部署落地页 ====="
cp -r /home/data/projects/mall/mall-project/landing/* /opt/landing/
echo "落地页已更新"

echo "===== 2. 更新 nginx landing.conf ====="
CONF="/usr/local/nginx/conf/conf.d/landing.conf"
BARE="chxhx.eu.cc drrgr.eu.cc drrimrf.eu.cc drriiu.eu.cc duomi.eu.cc dengruihan.eu.cc yyawzx.eu.cc gamed.eu.cc"
WILDCARD="chxhx.eu.cc *.chxhx.eu.cc drrgr.eu.cc *.drrgr.eu.cc drrimrf.eu.cc *.drrimrf.eu.cc drriiu.eu.cc *.drriiu.eu.cc duomi.eu.cc *.duomi.eu.cc dengruihan.eu.cc *.dengruihan.eu.cc yyawzx.eu.cc *.yyawzx.eu.cc gamed.eu.cc *.gamed.eu.cc"

cat > $CONF << 'NGINX'
# ===== 主域名 → 落地页 =====
server {
    listen 80;
    server_name tiktook.eu.cc www.tiktook.eu.cc;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name tiktook.eu.cc www.tiktook.eu.cc;

    ssl_certificate     /etc/letsencrypt/live/www.tiktook.eu.cc/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.tiktook.eu.cc/privkey.pem;
    ssl_protocols TLSv1.2;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /opt/landing;
    index index.html;

    location /rotation-engine.js { expires -1; add_header Cache-Control "no-cache, no-store, must-revalidate"; }
    location /domain-config.json { expires -1; add_header Cache-Control "no-cache, no-store, must-revalidate"; }
    location = /favicon.ico { expires 1h; }
    location / { try_files $uri $uri/ /index.html; }
}

# ===== 轮值通配符域名 → Mall 应用 =====
server {
    listen 80;
    server_name WILDCARD_PLACEHOLDER;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name WILDCARD_PLACEHOLDER;

    ssl_certificate     /etc/letsencrypt/live/www.tiktook.eu.cc/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.tiktook.eu.cc/privkey.pem;
    ssl_protocols TLSv1.2;
    ssl_ciphers HIGH:!aNULL:!MD5;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # 轮值引擎目标路径 → SPA 映射
    location = /home           { return 302 /pc/; }
    location = /login          { return 302 /pc/; }
    location = /merchantSettled { return 302 /seller/; }

    location = /favicon.ico {
        root /opt/landing;
        expires 1h;
    }
    location / { proxy_pass http://127.0.0.1:8080/; }
}
NGINX

# 替换通配符占位符
sed -i "s/WILDCARD_PLACEHOLDER/$WILDCARD/" $CONF

echo "===== 3. 测试并重载 nginx ====="
/usr/local/nginx/sbin/nginx -t && /usr/local/nginx/sbin/nginx -s reload
echo "===== 部署完成 ====="
echo "落地页: https://tiktook.eu.cc/"
echo "轮值域名示例: https://shop.chxhx.eu.cc/"
