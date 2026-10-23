"""
Model Thông báo (Notification) - Lưu trữ và điều phối thông báo cho Admin & Nhân viên CSVC.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Người nhận cụ thể (nếu có)
    target_role = Column(String(20), nullable=True, index=True)       # Vai trò nhận: "admin", "staff", "all"
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    priority_level = Column(String(20), default="normal")             # "emergency", "urgent", "high", "normal"
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    incident = relationship("Incident", foreign_keys=[incident_id])

    def __repr__(self):
        return f"<Notification id={self.id} title='{self.title}' role='{self.target_role}' read={self.is_read}>"
