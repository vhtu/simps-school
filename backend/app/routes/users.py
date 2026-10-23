"""
Route Quản lý Người dùng - Dành cho Quản trị viên (Admin).
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.services.auth_service import hash_password
from app.middleware.auth_middleware import require_role
from app.utils.helpers import api_response

router = APIRouter(prefix="/users", tags=["Quản lý Người dùng"])


@router.get("", summary="Lấy danh sách người dùng")
def get_users(
    role: Optional[str] = Query(None, description="Lọc theo vai trò (student, staff, admin)"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên hoặc username"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin", "staff"))
):
    """
    Lấy danh sách tài khoản trong hệ thống.
    Nhân viên và Admin có thể xem danh sách nhân viên để phân công.
    """
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) |
            (User.username.ilike(f"%{search}%"))
        )

    users = query.order_by(User.id.asc()).all()
    results = [UserOut.model_validate(u).model_dump() for u in users]
    return api_response(
        success=True,
        data=results,
        message="Lấy danh sách người dùng thành công"
    )


@router.post("", summary="Tạo người dùng mới (Admin)")
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    """
    Admin thêm tài khoản học sinh, giáo viên, nhân viên CSVC.
    """
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tên đăng nhập '{data.username}' đã tồn tại"
        )

    new_user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        class_name=data.class_name,
        email=data.email,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return api_response(
        success=True,
        data=UserOut.model_validate(new_user).model_dump(),
        message="Tạo người dùng thành công"
    )


@router.patch("/{user_id}", summary="Cập nhật thông tin người dùng (Admin)")
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    """
    Cập nhật thông tin tài khoản hoặc đặt lại mật khẩu.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng"
        )

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.role is not None:
        user.role = data.role
    if data.class_name is not None:
        user.class_name = data.class_name
    if data.email is not None:
        user.email = data.email
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password:
        user.password_hash = hash_password(data.password)

    db.commit()
    db.refresh(user)
    return api_response(
        success=True,
        data=UserOut.model_validate(user).model_dump(),
        message="Cập nhật người dùng thành công"
    )


@router.delete("/{user_id}", summary="Vô hiệu hóa người dùng (Admin)")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    """
    Vô hiệu hóa tài khoản (Soft Delete).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng"
        )
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể tự vô hiệu hóa tài khoản của chính mình"
        )

    user.is_active = False
    db.commit()
    return api_response(
        success=True,
        data={"id": user_id},
        message="Đã vô hiệu hóa tài khoản"
    )
