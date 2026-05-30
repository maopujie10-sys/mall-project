"""数据库连接模块"""
import pymysql
from config import DB_CONFIG

def get_db():
    """获取MySQL数据库连接"""
    return pymysql.connect(
        host=DB_CONFIG.get("host", "127.0.0.1"),
        port=int(DB_CONFIG.get("port", 3306)),
        user=DB_CONFIG.get("user", "root"),
        password=DB_CONFIG.get("password", "Root@123"),
        database=DB_CONFIG.get("name", "mall"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.Cursor
    )