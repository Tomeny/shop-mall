"""认证路由：注册 / 登录（公开接口，无需 token）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import security
from database import get_db
from models import User
from schemas import RegisterIn, LoginIn, TokenOut

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=body.username).first():
        raise HTTPException(status_code=400, detail="用户名已被注册")
    db.add(User(
        username=body.username,
        password_hash=security.hash_password(body.password),
        role="user",  # 注册的用户一律是普通用户
    ))
    db.commit()
    return {"message": "注册成功，请登录"}


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=body.username).first()
    if user is None or not security.verify_password(body.password, user.password_hash):
        # 故意不区分"用户不存在"和"密码错误"，避免撞库探测
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return TokenOut(
        token=security.create_token(user.id, user.username, user.role),
        username=user.username,
        role=user.role,
    )
