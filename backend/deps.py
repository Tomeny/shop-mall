"""Depends 子依赖链（本项目核心学习点）：

    get_current_user   ->  从请求头解析 JWT，查库返回 User
    require_admin      ->  依赖 get_current_user，再检查 role == "admin"

路由里写 Depends(require_admin) 时，FastAPI 会自动先跑完整条链。
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

import security
from database import get_db
from models import User

# HTTPBearer 会自动从 Authorization: Bearer <token> 里取 token
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """解析 JWT 并返回当前登录用户。任何失败都返回 401。"""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未登录或登录已过期，请先登录",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        payload = security.decode_token(credentials.credentials)
    except Exception:
        raise unauthorized

    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise unauthorized
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """只允许 role == "admin" 的用户通过，否则 403。"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user
