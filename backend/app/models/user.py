"""
Model Người dùng - Quản lý thông tin tài khoản và phân quyền.
Có 3 vai trò: student (học sinh), staff (nhân viên), admin (quản trị viên).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    # Vai trò: student = học sinh, staff = nhân viên xử lý, admin = quản trị viên
    role = Column(
        SQLEnum("student", "staff", "admin", name="user_role"),
        nullable=False,
        default="student"
    )
    class_name = Column(String(20), nullable=True)   # Lớp học (chỉ cho học sinh)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)  # Xóa mềm: đặt False thay vì xóa thật

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
