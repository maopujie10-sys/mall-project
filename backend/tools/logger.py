"""统一日志系统 — 控制台+文件双输出,自动轮转,支持级别过滤"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 全局logger实例
_loggers = {}

def get_logger(name: str = "friday", level: str = None) -> logging.Logger:
    """获取或创建logger"""
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    
    # 从环境变量获取级别,默认INFO
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    logger.setLevel(getattr(logging, level, logging.INFO))
    
    # 避免重复添加handler
    if logger.handlers:
        _loggers[name] = logger
        return logger

    # 格式化: [2026-05-29 12:00:00] [INFO] [module] message
    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)-5s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 控制台输出
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    # 文件输出(自动轮转,单文件最大10MB,保留5个)
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

    # 错误日志单独输出
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
    """初始化全局日志配置"""
    logger = get_logger("friday")
    logger.info("日志系统初始化完成")
    return logger

# 快捷日志函数
def info(msg, *args):
    get_logger().info(msg, *args)

def warn(msg, *args):
    get_logger().warning(msg, *args)

def error(msg, *args):
    get_logger().error(msg, *args)

def debug(msg, *args):
    get_logger().debug(msg, *args)
