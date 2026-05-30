"""数据库连接模块 — 使用SQLAlchemy连接池"""
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from config import DB_CONFIG

_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        host = DB_CONFIG.get("host", "127.0.0.1")
        port = int(DB_CONFIG.get("port", 3306))
        user = DB_CONFIG.get("user", "root")
        password = DB_CONFIG.get("password", "")
        db_name = DB_CONFIG.get("name", "mall")
        db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4"
        _engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
        )
    return _engine

def get_db():
    """获取MySQL数据库连接（从SQLAlchemy连接池）"""
    engine = _get_engine()
    return engine.raw_connection()