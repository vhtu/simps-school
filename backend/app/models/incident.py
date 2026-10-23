"""
Model Sự cố - Bảng chính lưu thông tin các sự cố được báo cáo.
Bao gồm thông tin sự cố, điểm ưu tiên tính toán, và trạng thái xử lý.
"""

import json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, JSON,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # === Liên kết người báo cáo ===
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # === Phân loại sự cố ===
    type_id = Column(Integer, ForeignKey("incident_types.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)

    # === Thông tin mô tả ===
    title = Column(String(200), nullable=False)          # Tiêu đề sự cố
    description = Column(Text, nullable=True)            # Mô tả chi tiết

    # === Các chỉ số đánh giá (đầu vào cho thuật toán) ===
    severity = Column(Integer, nullable=False, default=1)       # S: Mức nghiêm trọng (1-5)
    people_affected = Column(Integer, nullable=False, default=1) # Số người bị ảnh hưởng
    learning_impact = Column(Integer, nullable=False, default=1) # E: Ảnh hưởng học tập (1-5)

    # === Kết quả thuật toán ưu tiên ===
    priority_score = Column(Float, nullable=False, default=0.0)  # Điểm ưu tiên tính toán
    priority_level = Column(
        SQLEnum("normal", "high", "urgent", "emergency", name="priority_level"),
        nullable=False,
        default="normal"
    )

    # === Trạng thái xử lý ===
    # reported: đã báo cáo → received: đã tiếp nhận → assigned: đã phân công
    # → in_progress: đang xử lý → resolved: đã giải quyết
    # → confirmed: học sinh xác nhận → closed: đóng
    status = Column(
        SQLEnum(
            "reported", "received", "assigned", "in_progress",
            "resolved", "confirmed", "closed",
            name="incident_status"
        ),
        nullable=False,
        default="reported"
    )

    # === Phân công xử lý ===
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    # === Mốc thời gian ===
    reported_at = Column(DateTime, default=datetime.utcnow)
    received_at = Column(DateTime, nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)

    # === Kết quả xử lý ===
    resolution_notes = Column(Text, nullable=True)       # Ghi chú khi giải quyết

    # === Hình ảnh đính kèm ===
    # Lưu dạng JSON array: ["path1.jpg", "path2.jpg"]
    image_paths = Column(Text, nullable=True, default="[]")

    # === Quan hệ (Relationships) ===
    reporter = relationship("User", foreign_keys=[reporter_id])
    assignee = relationship("User", foreign_keys=[assigned_to])
    incident_type = relationship("IncidentType")
    location = relationship("Location")
    status_history = relationship("StatusHistory", back_populates="incident",
                                  order_by="StatusHistory.changed_at")

    def get_image_paths(self):
        """Lấy danh sách đường dẫn hình ảnh từ JSON string."""
        if self.image_paths:
            try:
                return json.loads(self.image_paths)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    def set_image_paths(self, paths: list):
        """Lưu danh sách đường dẫn hình ảnh dưới dạng JSON string."""
        self.image_paths = json.dumps(paths)

    def __repr__(self):
        return f"<Incident #{self.id}: {self.title} ({self.status})>"
