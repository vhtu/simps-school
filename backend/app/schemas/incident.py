"""
Schema Sự cố - Định nghĩa cấu trúc dữ liệu cho API quản lý sự cố.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class IncidentCreate(BaseModel):
    """Tạo sự cố mới - dữ liệu từ form báo cáo của học sinh"""
    type_id: int                           # Loại sự cố
    location_id: int                       # Địa điểm xảy ra
    title: str                             # Tiêu đề ngắn gọn
    description: Optional[str] = None      # Mô tả chi tiết
    severity: int = 1                      # Mức nghiêm trọng (1-5)
    people_affected: int = 1               # Số người bị ảnh hưởng
    learning_impact: int = 1               # Ảnh hưởng đến việc học (1-5)
    image_paths: Optional[List[str]] = []  # Đường dẫn hình ảnh


class IncidentOut(BaseModel):
    """Thông tin sự cố trả về cho client"""
    id: int
    reporter_id: int
    reporter_name: Optional[str] = None
    type_id: int
    type_name: Optional[str] = None
    location_id: int
    location_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    severity: int
    people_affected: int
    learning_impact: int
    priority_score: float
    priority_level: str
    status: str
    assigned_to: Optional[int] = None
    assignee_name: Optional[str] = None
    reported_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    assigned_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    image_paths: Optional[List[str]] = []

    model_config = {"from_attributes": True}


class StatusUpdate(BaseModel):
    """Cập nhật trạng thái sự cố"""
    status: str                            # Trạng thái mới
    notes: Optional[str] = None            # Ghi chú khi cập nhật
    resolution_notes: Optional[str] = None # Ghi chú giải quyết (khi resolved)


class AssignRequest(BaseModel):
    """Yêu cầu phân công xử lý"""
    assigned_to: int                       # ID nhân viên được phân công


class StatusHistoryOut(BaseModel):
    """Lịch sử thay đổi trạng thái"""
    id: int
    incident_id: int
    changed_by: int
    changed_by_name: Optional[str] = None
    old_status: Optional[str] = None
    new_status: str
    notes: Optional[str] = None
    changed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LocationOut(BaseModel):
    """Thông tin địa điểm"""
    id: int
    name: str
    building: Optional[str] = None
    floor: Optional[str] = None
    risk_level: int
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class LocationCreate(BaseModel):
    """Tạo địa điểm mới"""
    name: str
    building: Optional[str] = None
    floor: Optional[str] = None
    risk_level: int = 1
    description: Optional[str] = None


class IncidentTypeOut(BaseModel):
    """Thông tin loại sự cố"""
    id: int
    name: str
    default_severity: int
    description: Optional[str] = None
    is_safety_critical: bool

    model_config = {"from_attributes": True}


class IncidentTypeCreate(BaseModel):
    """Tạo loại sự cố mới"""
    name: str
    default_severity: int = 1
    description: Optional[str] = None
    is_safety_critical: bool = False
