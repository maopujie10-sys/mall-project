锘?""鏃ュ織娌荤悊 鈥?鑷姩杞浆+淇濈暀绛栫暐+娓呯悊"""
import os, glob, logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta

LOG_DIR = os.getenv("LOG_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs"))

def setup_logging():
    """閰嶇疆缁撴瀯鍖栨棩蹇?JSON鏍煎紡+鎸夊ぇ灏忚疆杞?淇濈暀30澶?"""
    os.makedirs(LOG_DIR, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
    # 涓绘棩蹇?(100MB杞浆, 淇濈暀5涓?
    handler = RotatingFileHandler(os.path.join(LOG_DIR, "agent.log"), maxBytes=100*1024*1024, backupCount=5, encoding="utf-8")
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    # 閿欒鏃ュ織鐙珛
    err_handler = RotatingFileHandler(os.path.join(LOG_DIR, "error.log"), maxBytes=50*1024*1024, backupCount=3, encoding="utf-8")
    err_handler.setLevel(logging.ERROR)
    err_handler.setFormatter(formatter)
    root.addHandler(err_handler)
    # 鎺у埗鍙拌緭鍑?    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)
    return root

def clean_old_logs(days: int = 30):
    """娓呯悊瓒呰繃days澶╃殑鏃ュ織鏂囦欢"""
    count = 0
    cutoff = datetime.now() - timedelta(days=days)
    for f in glob.glob(os.path.join(LOG_DIR, "*.log*")) + glob.glob(os.path.join(LOG_DIR, "*.json*")):
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(f))
            if mtime < cutoff:
                os.remove(f)
                count += 1
        except: pass
    return count

def get_log_stats() -> dict:
    """鏃ュ織缁熻"""
    total_size = 0; file_count = 0
    for f in glob.glob(os.path.join(LOG_DIR, "*")):
        try:
            total_size += os.path.getsize(f)
            file_count += 1
        except: pass
    return {"log_dir": LOG_DIR, "file_count": file_count, "total_size_mb": round(total_size/(1024*1024), 1)}
