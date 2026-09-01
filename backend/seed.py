"""首次启动的种子数据：管理员 admin/admin123 + 几个演示商品。"""
from sqlalchemy.orm import Session

import security
from models import User, Product


def seed(db: Session) -> None:
    # 管理员不存在才创建
    if db.query(User).filter_by(username="admin").first() is None:
        db.add(User(
            username="admin",
            password_hash=security.hash_password("admin123"),
            role="admin",
        ))

    # 商品表为空才插入演示数据
    if db.query(Product).count() == 0:
        demo_products = [
            Product(name="机械键盘 87 键", price=299.00, stock=50,
                    description="红轴，热插拔，PBT 键帽", image_url=""),
            Product(name="无线鼠标", price=99.00, stock=100,
                    description="2.4G + 蓝牙双模，静音微动", image_url=""),
            Product(name="27 寸 4K 显示器", price=1899.00, stock=20,
                    description="IPS 面板，Type-C 90W 反充", image_url=""),
            Product(name="降噪耳机", price=599.00, stock=30,
                    description="主动降噪，40 小时续航", image_url=""),
            Product(name="桌面升降支架", price=159.00, stock=40,
                    description="铝合金，承重 20kg", image_url=""),
        ]
        db.add_all(demo_products)

    db.commit()
