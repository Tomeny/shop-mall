"""密码哈希（bcrypt）与 JWT 签发/解析。

- bcrypt 是单向哈希：数据库里永远查不到明文密码，
  管理后台只能"重置"，不能"查看"。
- JWT 载荷里放 user_id / username / role，签发后 7 天有效。
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

import config


def hash_password(plain: str) -> str:
    """明文 -> bcrypt 哈希（存库用）。"""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文与库里的哈希是否匹配。"""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_token(user_id: int, username: str, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(days=config.JWT_EXPIRE_DAYS),
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    """解析 JWT。过期/伪造会抛 jwt 异常，由 deps.py 统一转成 401。"""
    return jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
