"""
Schema Người dùng - Định nghĩa cấu trúc dữ liệu vào/ra cho API users.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserOut(BaseModel):
    """Thông tin người dùng trả về cho client (không bao gồm mật khẩu)"""
    id: int
    username: str
    full_name: str
    role: str
    class_name: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    """Tạo người dùng mới"""
    username: str
    password: str
    full_name: str
    role: str = "student"
    class_name: Optional[str] = None
    email: Optional[str] = None


class UserUpdate(BaseModel):
    """Cập nhật thông tin người dùng"""
    full_name: Optional[str] = None
    role: Optional[str] = None
    class_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
