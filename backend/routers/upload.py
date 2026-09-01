"""图片上传路由：仅管理员可用（Depends(require_admin)）。

保存到 backend/uploads/，返回可直接访问的相对 URL（/uploads/<文件名>）。
前端通过 Vite 的 /uploads 代理访问到 FastAPI 的静态文件。
"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from deps import require_admin
from models import User

router = APIRouter(prefix="/api/admin", tags=["图片上传"])

# backend/uploads/ 目录（相对本文件上一级）
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
# 限制大小：约 5MB，防止传超大文件把磁盘占满
MAX_SIZE = 5 * 1024 * 1024


@router.post("/upload")
def upload_image(
    file: UploadFile,
    admin: User = Depends(require_admin),
):
    """上传商品图片，返回 {url}。"""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(
            status_code=400,
            detail=f"仅支持图片格式：{', '.join(sorted(ALLOWED_EXT))}",
        )

    content = file.file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="图片不能超过 5MB")

    # uuid 重命名，避免重名覆盖
    filename = f"{uuid.uuid4().hex}{ext}"
    (UPLOAD_DIR / filename).write_bytes(content)

    return {"url": f"/uploads/{filename}"}
