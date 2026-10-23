"""
Model Lịch sử trạng thái - Ghi lại mọi thay đổi trạng thái của sự cố.
Giúp theo dõi quá trình xử lý và trách nhiệm.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class StatusHistory(Base):
    __tablename__ = "status_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    old_status = Column(String(20), nullable=True)       # Trạng thái cũ
    new_status = Column(String(20), nullable=False)      # Trạng thái mới
    notes = Column(Text, nullable=True)                  # Ghi chú khi thay đổi
    changed_at = Column(DateTime, default=datetime.utcnow)

    # === Quan hệ ===
    incident = relationship("Incident", back_populates="status_history")
    user = relationship("User")

    def __repr__(self):
        return f"<StatusHistory incident={self.incident_id}: {self.old_status}→{self.new_status}>"
