import os
from dotenv import load_dotenv

load_dotenv()

AGENT_TOKEN = os.getenv("X_AGENT_TOKEN", "change-me-in-production")
MALL_BASE_URL = os.getenv("MALL_BASE_URL", "http://mall-app:8080")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

REDIS_DSN = os.getenv("REDIS_DSN", "redis://mall-redis:6379/0")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
