"""
Model Loại sự cố - Phân loại các loại sự cố trong trường.
Ví dụ: quạt hỏng, đèn hỏng, máy chiếu hỏng, vòi nước rò rỉ...
"""

from sqlalchemy import Column, Integer, String, Boolean, Text
from app.database import Base


class IncidentType(Base):
    __tablename__ = "incident_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)           # Tên loại sự cố
    # Mức nghiêm trọng mặc định: 1 = nhẹ, 5 = rất nghiêm trọng
    default_severity = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=True)            # Mô tả chi tiết
    # Sự cố liên quan đến an toàn → tự động ưu tiên khẩn cấp
    is_safety_critical = Column(Boolean, default=False)

    def __repr__(self):
        return f"<IncidentType {self.name} (safety={self.is_safety_critical})>"
