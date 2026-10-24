"""
Route Xác thực (Auth) - Đăng nhập, đăng ký, lấy thông tin cá nhân.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, ChangePasswordRequest
from app.services import auth_service
from app.middleware.auth_middleware import get_current_user, require_role
from app.utils.helpers import api_response

router = APIRouter(prefix="/auth", tags=["Xác thực"])


@router.post("/login", summary="Đăng nhập hệ thống")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Đăng nhập bằng tên đăng nhập và mật khẩu.
    Trả về JWT token và thông tin người dùng.
    """
    result = auth_service.login_user(db, request.username, request.password)
    return api_response(
        success=True,
        data=result,
        message="Đăng nhập thành công"
    )


@router.post("/register", summary="Đăng ký tài khoản mới (Chỉ Admin)")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    """
    Tạo tài khoản mới. Chỉ tài khoản admin mới có quyền thực hiện.
    """
    new_user = auth_service.register_user(db, request.model_dump())
    return api_response(
        success=True,
        data={
            "id": new_user.id,
            "username": new_user.username,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "class_name": new_user.class_name,
            "email": new_user.email
        },
        message="Tạo tài khoản thành công"
    )


@router.get("/me", summary="Lấy thông tin tài khoản hiện tại")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Lấy thông tin người dùng đang đăng nhập dựa trên token JWT.
    """
    return api_response(
        success=True,
        data={
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "class_name": current_user.class_name,
            "email": current_user.email
        },
        message="Lấy thông tin thành công"
    )


@router.post("/change-password", summary="Đổi mật khẩu người dùng")
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Đổi mật khẩu của người dùng đang đăng nhập.
    """
    from app.services.auth_service import verify_password, hash_password
    from fastapi import HTTPException
    
    if not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không chính xác"
        )
    
    if len(request.new_password) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới phải có ít nhất 4 ký tự"
        )

    current_user.password_hash = hash_password(request.new_password)
    db.commit()
    return api_response(
        success=True,
        data={"user_id": current_user.id},
        message="Đổi mật khẩu thành công"
    )

