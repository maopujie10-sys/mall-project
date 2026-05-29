锘?""缁熶竴鏃ュ織绯荤粺 鈥?鎺у埗鍙?鏂囦欢鍙岃緭鍑?鑷姩杞浆,鏀寔绾у埆杩囨护"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 鍏ㄥ眬logger瀹炰緥
_loggers = {}

def get_logger(name: str = "friday", level: str = None) -> logging.Logger:
    """鑾峰彇鎴栧垱寤簂ogger"""
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    
    # 浠庣幆澧冨彉閲忚幏鍙栫骇鍒?榛樿INFO
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    logger.setLevel(getattr(logging, level, logging.INFO))
    
    # 閬垮厤閲嶅娣诲姞handler
    if logger.handlers:
        _loggers[name] = logger
        return logger

    # 鏍煎紡鍖? [2026-05-29 12:00:00] [INFO] [module] message
    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)-5s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 鎺у埗鍙拌緭鍑?
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    # 鏂囦欢杈撳嚭(鑷姩杞浆,鍗曟枃浠舵渶澶?0MB,淇濈暀5涓?
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, f"{name}.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    # 閿欒鏃ュ織鍗曠嫭杈撳嚭
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, "error.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(fmt)
    logger.addHandler(error_handler)

    _loggers[name] = logger
    return logger

def setup_logging():
    """鍒濆鍖栧叏灞€鏃ュ織閰嶇疆"""
    logger = get_logger("friday")
    logger.info("鏃ュ織绯荤粺鍒濆鍖栧畬鎴?)
    return logger

# 蹇嵎鏃ュ織鍑芥暟
def info(msg, *args):
    get_logger().info(msg, *args)

def warn(msg, *args):
    get_logger().warning(msg, *args)

def error(msg, *args):
    get_logger().error(msg, *args)

def debug(msg, *args):
    get_logger().debug(msg, *args)
