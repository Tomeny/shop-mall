"""数据库引擎与 Session 工厂。

main.py 启动时会先调用 create_database() 保证库存在，
所以这里直接用带库名的连接串建 engine。
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import config

# pool_pre_ping：连接被 MySQL 掉线后自动重连
engine = create_engine(config.database_url(), pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db():
    """FastAPI 依赖：每个请求一个 Session，请求结束自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
