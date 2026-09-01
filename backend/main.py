"""shop-mall 后端入口。

启动流程：
1. 连 MySQL（不带库名）执行 CREATE DATABASE IF NOT EXISTS shop_mall
2. 建表（表不存在才建）
3. 灌种子数据（admin/admin123 + 演示商品）
4. 挂载路由 + 开 CORS

运行：uvicorn main:app --reload --port 8000
文档：http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text

import config
import database
import seed
from routers import auth, products, admin, upload
from routers.upload import UPLOAD_DIR


def create_database() -> None:
    """先连不指定库的 MySQL，确保 shop_mall 库存在（utf8mb4）。"""
    server_url = (
        f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}"
        f"@{config.DB_HOST}:{config.DB_PORT}/?charset=utf8mb4"
    )
    server_engine = create_engine(server_url)
    with server_engine.connect() as conn:
        conn.execute(text(
            f"CREATE DATABASE IF NOT EXISTS {config.DB_NAME} "
            "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        ))
        conn.commit()
    server_engine.dispose()


def init_data() -> None:
    database.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    try:
        seed.seed(db)
    finally:
        db.close()


app = FastAPI(title="shop-mall", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(admin.router)
app.include_router(upload.router)

# 上传的图片通过 /uploads/<文件名> 访问
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
def root():
    return {"app": "shop-mall", "docs": "/docs"}


# uvicorn 直接跑 main.py 时（python main.py）也会先初始化
create_database()
init_data()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
