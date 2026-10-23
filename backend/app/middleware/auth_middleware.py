"""
Middleware xác thực JWT - Xác minh token và phân quyền người dùng.
Sử dụng dependency injection của FastAPI.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, ALGORITHM
from app.database import get_db
from app.models.user import User

# Sử dụng Bearer token scheme
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT access token.
    
    Args:
        data: Dữ liệu cần mã hóa vào token (thường là user_id, username, role)
        expires_delta: Thời gian hết hạn tùy chỉnh
    
    Returns:
        Token JWT dạng string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Giải mã và xác minh token JWT.
    
    Args:
        token: Token JWT cần xác minh
    
    Returns:
        Payload đã giải mã
    
    Raises:
        HTTPException: Nếu token không hợp lệ hoặc hết hạn
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token đã hết hạn"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency: Lấy người dùng hiện tại từ JWT token.
    Sử dụng trong route: current_user: User = Depends(get_current_user)
    
    Returns:
        Đối tượng User của người dùng hiện tại
    """
    payload = verify_token(credentials.credentials)
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không chứa thông tin người dùng"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa"
        )
    return user


def require_role(*roles):
    """
    Dependency factory: Yêu cầu người dùng phải có một trong các vai trò chỉ định.
    
    Sử dụng:
        @router.get("/admin-only")
        def admin_route(user: User = Depends(require_role("admin"))):
            ...
    
    Args:
        *roles: Danh sách vai trò được phép (vd: "admin", "staff")
    
    Returns:
        Dependency function
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bạn không có quyền truy cập. Yêu cầu vai trò: {', '.join(roles)}"
            )
        return current_user
    return role_checker
