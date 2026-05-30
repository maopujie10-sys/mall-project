# ===== Friday AI OS — 统一商城前端 =====
# 多阶段构建：Vite 打包 → Nginx 部署

# Stage 1: 构建
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json ./
RUN npm install --registry=https://registry.npmmirror.com
COPY . .
RUN npm run build

# Stage 2: 运行
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx 配置（SPA fallback + API 代理由外部 nginx 处理）
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { try_files $uri $uri/ /index.html; } \
    location /manifest.json { add_header Content-Type application/manifest+json; } \
    location /sw.js { add_header Service-Worker-Allowed /; } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
