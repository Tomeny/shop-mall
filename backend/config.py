"""集中读取 .env 配置，其他模块统一从这里 import。"""
import os
from dotenv import load_dotenv

# 读取 backend/.env（相对本文件）
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "shop_mall")

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_EXPIRE_DAYS = int(os.getenv("JWT_EXPIRE_DAYS", "7"))


def database_url() -> str:
    """带库名的 SQLAlchemy 连接串。"""
    return (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
