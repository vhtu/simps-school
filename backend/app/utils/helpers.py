"""
Hàm tiện ích - Các hàm phụ trợ dùng chung trong ứng dụng.
"""

import os
import json
from datetime import datetime
from typing import Any, Optional


def api_response(success: bool, data: Any = None, message: str = "") -> dict:
    """
    Tạo phản hồi API chuẩn cho tất cả endpoint.
    
    Định dạng thống nhất:
    {
        "success": true/false,
        "data": ...,
        "message": "..."
    }
    
    Args:
        success: Thành công hay thất bại
        data: Dữ liệu trả về
        message: Thông điệp mô tả
    
    Returns:
        Dict phản hồi chuẩn
    """
    return {
        "success": success,
        "data": data,
        "message": message
    }


def validate_severity(value: int) -> bool:
    """Kiểm tra giá trị mức nghiêm trọng hợp lệ (1-5)."""
    return 1 <= value <= 5


def validate_risk_level(value: int) -> bool:
    """Kiểm tra giá trị mức rủi ro hợp lệ (1-5)."""
    return 1 <= value <= 5


def validate_status_transition(old_status: str, new_status: str) -> bool:
    """
    Kiểm tra chuyển trạng thái hợp lệ.
    
    Luồng trạng thái:
    reported → received → assigned → in_progress → resolved → confirmed → closed
    
    Cho phép chuyển linh hoạt một số bước nhưng không cho quay lại.
    """
    # Định nghĩa các chuyển trạng thái hợp lệ
    valid_transitions = {
        "reported": ["received", "assigned"],
        "received": ["assigned", "in_progress"],
        "assigned": ["in_progress", "received"],
        "in_progress": ["resolved", "assigned"],
        "resolved": ["confirmed", "closed", "in_progress"],
        "confirmed": ["closed"],
        "closed": [],  # Không thể chuyển từ đóng
    }

    allowed = valid_transitions.get(old_status, [])
    return new_status in allowed


VALID_STATUSES = [
    "reported", "received", "assigned",
    "in_progress", "resolved", "confirmed", "closed"
]

VALID_ROLES = ["student", "staff", "admin"]

VALID_PRIORITY_LEVELS = ["normal", "high", "urgent", "emergency"]


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Định dạng datetime thành chuỗi ISO 8601."""
    if dt is None:
        return None
    return dt.isoformat()


def ensure_upload_dir():
    """Đảm bảo thư mục upload tồn tại."""
    from app.config import UPLOAD_DIR
    os.makedirs(UPLOAD_DIR, exist_ok=True)
