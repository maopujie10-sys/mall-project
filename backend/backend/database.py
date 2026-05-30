''" -- SQLAlchemy ''"
import json
from datetime import datetime
from config import DB_CONFIG
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Text, DateTime, DECIMAL, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# =====  =====
class AgentTask(Base):
    __tablename__ = "agent_tasks"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    task_id = Column(String(64), unique=True, nullable=False, index=True)
    user_message = Column(Text)
    intent = Column(String(128))
    mode = Column(String(32), default="ai_control")
    risk_level = Column(String(4), default="L1")
    status = Column(String(32), default="pending")
    need_confirm = Column(Integer, default=0)
    confidence = Column(DECIMAL(4, 2))
    result_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class AgentAlert(Base):
    __tablename__ = "agent_alerts"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    alert_id = Column(String(64), unique=True, nullable=False, index=True)
    level = Column(String(4), default="P3")
    title = Column(String(256))
    detail = Column(Text)
    source = Column(String(64), default="system")
    resolved = Column(Integer, default=0)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)


# =====  =====
_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        dsn = DB_CONFIG.get("dsn")
        if dsn:
            _engine = create_engine(dsn, pool_size=5, max_overflow=10, pool_pre_ping=True)
    return _engine

def get_session():
    global _SessionLocal
    if _SessionLocal is None and get_engine():
        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal() if _SessionLocal else None

def init_db():
    ''''''
    engine = get_engine()
    if engine:
        Base.metadata.create_all(engine)
        return True
    return False

def db_available():
    ''''''
    return get_engine() is not None

# =====  =====
def save_task(task_id: str, data: dict):
    ''''''
    if not db_available():
        return False
    session = get_session()
    try:
        task = AgentTask(task_id=task_id, **{k: v for k, v in data.items() if hasattr(AgentTask, k)})
        session.add(task)
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()

def save_alert(alert_id: str, level: str, title: str, detail: str = '', source: str = "system"):
    ''''''
    if not db_available():
        return False
    session = get_session()
    try:
        alert = AgentAlert(alert_id=alert_id, level=level, title=title, detail=detail, source=source)
        session.add(alert)
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()
