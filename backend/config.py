"""配置中心 — 支持多环境"""
import os, sys
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("APP_ENV", "development")

# ===== Token =====
AGENT_TOKEN = os.getenv("X_AGENT_TOKEN", "")
if not AGENT_TOKEN or AGENT_TOKEN == "change-me-in-production":
    if ENV == "production":
        print("[Agent] 错误: X_AGENT_TOKEN 未配置，生产环境必须设置强密码")
        sys.exit(1)

# ===== Claude =====
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")

# ===== 外部服务 =====
MALL_BASE_URL = os.getenv("MALL_BASE_URL", "http://mall-app:8080")
CUSTOMER_BASE_URL = os.getenv("CUSTOMER_BASE_URL", "")
ROTATION_BASE_URL = os.getenv("ROTATION_BASE_URL", "")

# ===== 数据库 =====
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "agent_user"),
    "password": os.getenv("DB_PASSWORD", ""),
    "name": os.getenv("DB_NAME", "ai_agent"),
}
if all([DB_CONFIG["host"], DB_CONFIG["user"], DB_CONFIG["password"]]):
    DB_CONFIG["dsn"] = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['name']}?charset=utf8mb4"
else:
    DB_CONFIG["dsn"] = ""

# ===== Redis =====
REDIS_DSN = os.getenv("REDIS_DSN", "redis://localhost:6379/0")

# ===== 通知 =====
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_TO = os.getenv("SMTP_TO", "")
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK", "")
WECOM_WEBHOOK = os.getenv("WECOM_WEBHOOK", "")

# ===== SSH =====
SSH_HOST = os.getenv("SSH_HOST", "")
SSH_PORT = int(os.getenv("SSH_PORT", "22"))
SSH_USER = os.getenv("SSH_USER", "agent_user")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", "")

# ===== 路径 =====
BACKUP_DIR = os.getenv("BACKUP_DIR", os.path.join(os.path.dirname(__file__), "..", "backups"))
LOG_DIR = os.getenv("LOG_DIR", os.path.join(os.path.dirname(__file__), "..", "logs"))

# ===== AI Factory =====
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY", "")
IMAGE_API_URL = os.getenv("IMAGE_API_URL", "https://api.openai.com/v1/images/generations")
VIDEO_API_KEY = os.getenv("VIDEO_API_KEY", "")
VIDEO_API_URL = os.getenv("VIDEO_API_URL", "https://api.runwayml.com/v1/generations")

# ===== 商城数据库 =====
MALL_DB_HOST = os.getenv("MALL_DB_HOST", DB_CONFIG["host"])
MALL_DB_PORT = int(os.getenv("MALL_DB_PORT", DB_CONFIG["port"]))
MALL_DB_USER = os.getenv("MALL_DB_USER", DB_CONFIG["user"])
MALL_DB_PASSWORD = os.getenv("MALL_DB_PASSWORD", DB_CONFIG["password"])
MALL_DB_NAME = os.getenv("MALL_DB_NAME", "mall_db")
MALL_DB_DSN = f"mysql+pymysql://{MALL_DB_USER}:{MALL_DB_PASSWORD}@{MALL_DB_HOST}:{MALL_DB_PORT}/{MALL_DB_NAME}?charset=utf8mb4"

# ===== 腾讯云 COS =====
COS_SECRET_ID = os.getenv("COS_SECRET_ID", "")
COS_SECRET_KEY = os.getenv("COS_SECRET_KEY", "")
COS_BUCKET = os.getenv("COS_BUCKET", "shangchengtupian-1435149418")
COS_REGION = os.getenv("COS_REGION", "ap-singapore")
COS_DOMAIN = os.getenv("COS_DOMAIN", f"https://{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com")

# ===== 环境判断 =====
def is_production():
    return ENV == "production"

def is_development():
    return ENV == "development"

def is_staging():
    return ENV == "staging"

# 环境安全策略
def get_security_policy():
    if is_production():
        return {"auto_execute": "L1_only", "confirm_required": "L3+", "max_batch_size": 10}
    elif is_staging():
        return {"auto_execute": "L1-L2", "confirm_required": "L3+", "max_batch_size": 50}
    else:
        return {"auto_execute": "all", "confirm_required": "L4_only", "max_batch_size": 100}