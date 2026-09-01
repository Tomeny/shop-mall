"""后台管理路由：全部仅限管理员（Depends(require_admin)）。

说明：密码是 bcrypt 单向哈希，无法"查看"明文，
所以这里只提供用户列表（账号+注册时间）和重置密码。
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import security
from database import get_db
from deps import require_admin
from models import User, Product
from schemas import ProductIn, ProductOut, ProductUpdate, UserOut, ResetPasswordIn

router = APIRouter(prefix="/api/admin", tags=["后台管理"])


# ---------- 商品管理 ----------

@router.post("/products", response_model=ProductOut, status_code=201)
def create_product(
    body: ProductIn,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    product = Product(**body.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    body: ProductUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    # 只更新请求里真正传了的字段
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    db.delete(product)
    db.commit()
    return {"message": "已下架"}


# ---------- 用户管理 ----------

@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """查看注册用户（账号 / 角色 / 注册时间）。不含密码哈希。"""
    return db.query(User).order_by(User.id).all()


@router.put("/users/{user_id}/reset-password")
def reset_password(
    user_id: int,
    body: ResetPasswordIn,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """帮用户重置密码。"""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.password_hash = security.hash_password(body.new_password)
    db.commit()
    return {"message": f"用户 {user.username} 的密码已重置"}
