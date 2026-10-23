"""
Route Thông báo (Notifications) - Cung cấp danh sách thông báo theo thời gian thực cho Admin & Nhân viên.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services import notification_service
from app.middleware.auth_middleware import get_current_user, require_role
from app.utils.helpers import api_response

router = APIRouter(prefix="/notifications", tags=["Thông báo"])


@router.get("", summary="Lấy danh sách thông báo của người dùng")
def get_notifications(
    unread_only: bool = Query(False, description="Chỉ lấy thông báo chưa đọc"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng thông báo tối đa"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách thông báo dành cho vai trò hiện tại (Admin / Nhân viên CSVC).
    Bao gồm số lượng thông báo chưa đọc để hiển thị trên chuông thông báo.
    """
    result = notification_service.get_user_notifications(
        db=db,
        user_role=current_user.role,
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit
    )
    return api_response(
        success=True,
        data=result,
        message="Lấy danh sách thông báo thành công"
    )


@router.patch("/{notification_id}/read", summary="Đánh dấu thông báo là đã đọc")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Đánh dấu một thông báo cụ thể là đã đọc.
    """
    success = notification_service.mark_notification_read(db, notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông báo"
        )
    return api_response(
        success=True,
        data={"id": notification_id},
        message="Đã đánh dấu thông báo là đã đọc"
    )


@router.post("/read-all", summary="Đánh dấu tất cả thông báo là đã đọc")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Đánh dấu toàn bộ thông báo của vai trò hiện tại là đã đọc.
    """
    count = notification_service.mark_all_notifications_read(
        db=db,
        user_role=current_user.role,
        user_id=current_user.id
    )
    return api_response(
        success=True,
        data={"read_count": count},
        message=f"Đã đánh dấu {count} thông báo là đã đọc"
    )
