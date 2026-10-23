"""
Model Cấu hình hệ thống - Lưu các thiết lập hệ thống dạng key-value.
Dùng để lưu trọng số thuật toán (w1-w5) và ngưỡng phân loại.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), unique=True, nullable=False, index=True)  # Tên cấu hình
    value = Column(Text, nullable=False)                                # Giá trị (dạng string)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemConfig {self.key}={self.value}>"
