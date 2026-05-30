#!/bin/bash
# ============================================
# 服务器首次初始化脚本
# 在全新服务器上执行一次
# ============================================
set -e

echo "============================================"
echo "  TikTokMall AI Agent — 服务器初始化"
echo "============================================"

# 系统更新
echo "[1/5] 更新系统包..."
apt-get update -y && apt-get upgrade -y

# 安装 Docker
echo "[2/5] 安装 Docker..."
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | bash
    systemctl enable docker
    systemctl start docker
fi

# 安装 Docker Compose
echo "[3/5] 安装 Docker Compose..."
if ! command -v docker compose &>/dev/null; then
    DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
    mkdir -p "$DOCKER_CONFIG/cli-plugins"
    curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o "$DOCKER_CONFIG/cli-plugins/docker-compose"
    chmod +x "$DOCKER_CONFIG/cli-plugins/docker-compose"
fi

# 创建 agent 用户
echo "[4/5] 创建 agent_user..."
if ! id -u agent_user &>/dev/null; then
    useradd -m -s /bin/bash agent_user
    # 添加到 docker 组（允许执行 docker 命令）
    usermod -aG docker agent_user
    echo "   ✅ 已创建 agent_user 用户"
    echo "   ⚠️  请设置密码: passwd agent_user"
fi

# 创建 SSH 密钥
echo "[5/5] 生成 SSH 密钥..."
if [ ! -f /home/agent_user/.ssh/id_ed25519 ]; then
    mkdir -p /home/agent_user/.ssh
    ssh-keygen -t ed25519 -f /home/agent_user/.ssh/id_ed25519 -N "" -C "agent@tiktokmall"
    chown -R agent_user:agent_user /home/agent_user/.ssh
    echo "   ✅ SSH 密钥已生成"
    echo "   🔑 公钥: /home/agent_user/.ssh/id_ed25519.pub"
    cat /home/agent_user/.ssh/id_ed25519.pub
fi

echo ""
echo "============================================"
echo "  ✅ 服务器初始化完成"
echo "  下一步: 将代码上传至 /opt/claude-agent-control"
echo "         然后执行 bash scripts/deploy.sh"
echo "============================================"
