"""
Service xác thực - Xử lý logic đăng nhập, đăng ký, mã hóa mật khẩu.
"""

import bcrypt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.middleware.auth_middleware import create_access_token


def hash_password(password: str) -> str:
    """
    Mã hóa mật khẩu bằng bcrypt.
    
    Args:
        password: Mật khẩu gốc dạng plaintext
    
    Returns:
        Chuỗi mật khẩu đã mã hóa
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    So sánh mật khẩu gốc với mật khẩu đã mã hóa.
    
    Args:
        plain_password: Mật khẩu người dùng nhập
        hashed_password: Mật khẩu đã mã hóa trong database
    
    Returns:
        True nếu khớp, False nếu không
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def authenticate_user(db: Session, username: str, password: str) -> User:
    """
    Xác thực người dùng bằng username và password.
    
    Args:
        db: Database session
        username: Tên đăng nhập
        password: Mật khẩu
    
    Returns:
        Đối tượng User nếu xác thực thành công
    
    Raises:
        HTTPException: Nếu thông tin đăng nhập sai
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng"
        )
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa"
        )
    return user


def login_user(db: Session, username: str, password: str) -> dict:
    """
    Đăng nhập và trả về JWT token.
    
    Returns:
        Dict chứa access_token, token_type, và thông tin user
    """
    user = authenticate_user(db, username, password)

    # Tạo JWT token chứa thông tin người dùng
    token_data = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }
    access_token = create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "class_name": user.class_name,
            "email": user.email
        }
    }


def register_user(db: Session, user_data: dict) -> User:
    """
    Đăng ký tài khoản mới (chỉ admin được tạo).
    
    Args:
        db: Database session
        user_data: Thông tin người dùng mới
    
    Returns:
        Đối tượng User mới tạo
    """
    # Kiểm tra username đã tồn tại chưa
    existing = db.query(User).filter(User.username == user_data["username"]).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tên đăng nhập '{user_data['username']}' đã tồn tại"
        )

    # Tạo người dùng mới
    new_user = User(
        username=user_data["username"],
        password_hash=hash_password(user_data["password"]),
        full_name=user_data["full_name"],
        role=user_data.get("role", "student"),
        class_name=user_data.get("class_name"),
        email=user_data.get("email"),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
