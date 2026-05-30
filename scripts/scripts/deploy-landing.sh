#!/bin/bash
# ===== 部署落地页 + 轮值系统到 nginx =====
LANDING_DIR="/opt/landing"
NGINX_CONF="/etc/nginx/conf.d/mall.conf"

# 1. 复制落地页文件
mkdir -p $LANDING_DIR
cp -r landing/* $LANDING_DIR/

# 2. 根路径改为落地页（轮值入口），PC商城移到 /shop/
# 在 nginx 中：根 / → 落地页，/shop/ → PC商城，/h5/ → H5商城，/ai/ → AI面板
echo "部署完成。手动更新 nginx: 根路径指向 $LANDING_DIR/"