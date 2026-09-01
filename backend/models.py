"""SQLAlchemy 表模型：users / products。"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    # 只存 bcrypt 哈希，永远不存明文
    password_hash = Column(String(128), nullable=False)
    # "admin" 或 "user"
    role = Column(String(16), nullable=False, default="user")
    created_at = Column(DateTime, default=datetime.now)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    description = Column(Text, default="")
    image_url = Column(String(512), default="")
    created_at = Column(DateTime, default=datetime.now)
