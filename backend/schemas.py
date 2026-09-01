"""Pydantic 请求/响应模型（数据校验 + 出参格式）。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------- 认证 ----------

class RegisterIn(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6, max_length=64)


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    token: str
    username: str
    role: str


# ---------- 用户 ----------

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- 商品 ----------

class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    price: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)
    description: str = ""
    image_url: str = ""


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = None
    image_url: Optional[str] = None


class ProductOut(ProductIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- 管理员 ----------

class ResetPasswordIn(BaseModel):
    new_password: str = Field(min_length=6, max_length=64)
