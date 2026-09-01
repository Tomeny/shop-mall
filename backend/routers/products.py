"""商品浏览路由：登录即可访问（不要求 admin）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Product, User
from schemas import ProductOut, BuyIn

router = APIRouter(prefix="/api/products", tags=["商品"])


@router.get("", response_model=list[ProductOut])
def list_products(
    keyword: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """商品列表，支持按名称模糊搜索。"""
    query = db.query(Product)
    if keyword:
        query = query.filter(Product.name.contains(keyword))
    return query.order_by(Product.id.desc()).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.post("/{product_id}/buy")
def buy_product(
    product_id: int,
    body: BuyIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """购买商品：库存自动减少。登录用户即可购买。

    用 SELECT ... FOR UPDATE（行锁）锁住这条商品记录再扣库存，
    避免多人同时下单时「超卖」（库存被扣成负数）。
    """
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .with_for_update()
        .first()
    )
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    if product.stock < body.quantity:
        raise HTTPException(status_code=400, detail=f"库存不足，仅剩 {product.stock} 件")

    product.stock -= body.quantity
    db.commit()
    db.refresh(product)
    return {
        "message": "购买成功",
        "product_id": product.id,
        "quantity": body.quantity,
        "stock": product.stock,  # 购买后的剩余库存
    }
