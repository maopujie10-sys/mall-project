#!/bin/bash
set -e
echo "===== 1. 部署落地页 ====="
cp -r /home/data/projects/mall/mall-project/landing/* /opt/landing/
echo "落地页已更新"

echo "===== 2. 配置通配符 DNS 说明 ====="
echo "请确保以下8条DNS记录已配置（Cloudflare/阿里云DNS控制台）:"
for d in chxhx.eu.cc drrgr.eu.cc drrimrf.eu.cc drriiu.eu.cc duomi.eu.cc dengruihan.eu.cc yyawzx.eu.cc gamed.eu.cc; do
  echo "  *.${d}  A  服务器IP"
done

echo "===== 3. 更新 nginx 通配符 ====="
WILDCARD="*.chxhx.eu.cc *.drrgr.eu.cc *.drrimrf.eu.cc *.drriiu.eu.cc *.duomi.eu.cc *.dengruihan.eu.cc *.yyawzx.eu.cc *.gamed.eu.cc"
CONF="/etc/nginx/conf.d/landing.conf"
cat > $CONF << NGINX
server {
    listen 80;
    listen 443 ssl;
    server_name tiktook.eu.cc www.tiktook.eu.cc;

    root /opt/landing;
    index index.html;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}

server {
    listen 80;
    listen 443 ssl;
    server_name $WILDCARD;

    root /usr/share/nginx/html/mall;
    index index.html;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
NGINX

echo "===== 4. 测试并重载 nginx ====="
nginx -t && nginx -s reload
echo "===== 部署完成 ====="
echo "落地页: https://tiktook.eu.cc/"
echo "轮值域名示例: https://shop.chxhx.eu.cc/"