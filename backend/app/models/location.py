"""
Model Địa điểm - Quản lý các vị trí trong trường học.
Mỗi địa điểm có mức độ rủi ro (risk_level) từ 1-5,
dùng để tính điểm ưu tiên cho sự cố.
"""

from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)          # Tên địa điểm
    building = Column(String(50), nullable=True)         # Tòa nhà
    floor = Column(String(20), nullable=True)            # Tầng
    # Mức độ rủi ro khu vực: 1 = thấp, 5 = rất cao (phòng thí nghiệm, bếp...)
    risk_level = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=True)            # Mô tả thêm

    def __repr__(self):
        return f"<Location {self.name} (risk={self.risk_level})>"
