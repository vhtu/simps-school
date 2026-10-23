"""
Schema Thống kê - Định nghĩa cấu trúc dữ liệu cho API thống kê.
"""

from pydantic import BaseModel
from typing import Optional, List


class OverviewStats(BaseModel):
    """Thống kê tổng quan"""
    total_incidents: int = 0
    by_status: dict = {}             # Số lượng theo trạng thái
    by_priority: dict = {}           # Số lượng theo mức ưu tiên
    overdue_count: int = 0           # Số sự cố quá hạn (> 72h chưa xử lý)


class LocationStats(BaseModel):
    """Thống kê theo địa điểm"""
    location_id: int
    location_name: str
    incident_count: int = 0
    avg_resolution_hours: Optional[float] = None


class TypeStats(BaseModel):
    """Thống kê theo loại sự cố"""
    type_id: int
    type_name: str
    incident_count: int = 0


class MonthlyStats(BaseModel):
    """Thống kê theo tháng"""
    month: str                       # Định dạng "YYYY-MM"
    incident_count: int = 0


class ResolutionTimeStats(BaseModel):
    """Thống kê thời gian giải quyết"""
    overall_avg_hours: Optional[float] = None
    by_priority: dict = {}           # Trung bình theo mức ưu tiên
