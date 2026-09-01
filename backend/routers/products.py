"""商品浏览路由：登录即可访问（不要求 admin）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Product, User
from schemas import ProductOut

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
