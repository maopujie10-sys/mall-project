"""
日志工具模块 — 支持控制台+文件双输出，自动轮转
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# logger
_loggers = {}

def get_logger(name: str = "friday", level: str = None) -> logging.Logger:
    ''"logger''"
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    
    # ,INFO
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    logger.setLevel(getattr(logging, level, logging.INFO))
    
    # handler
    if logger.handlers:
        _loggers[name] = logger
        return logger

    # : [2026-05-29 12:00:00] [INFO] [module] message
    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)-5s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    # (,10MB,5)
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
    ''''''
    logger = get_logger("friday")
    logger.info('')
    return logger


def info(msg, *args):
    get_logger().info(msg, *args)

def warn(msg, *args):
    get_logger().warning(msg, *args)

def error(msg, *args):
    get_logger().error(msg, *args)

def debug(msg, *args):
    get_logger().debug(msg, *args)

logger = get_logger()
