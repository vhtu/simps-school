"""
Schema xác thực - Định nghĩa cấu trúc dữ liệu cho đăng nhập/đăng ký.
"""

from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    """Yêu cầu đăng nhập"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Phản hồi đăng nhập - chứa token JWT"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class RegisterRequest(BaseModel):
    """Yêu cầu đăng ký tài khoản mới (chỉ admin tạo)"""
    username: str
    password: str
    full_name: str
    role: str = "student"          # student / staff / admin
    class_name: Optional[str] = None
    email: Optional[str] = None
