"""
Route Thống kê & Báo cáo - Cung cấp số liệu phân tích sự cố cho Ban Quản lý.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services import stats_service
from app.middleware.auth_middleware import require_role
from app.utils.helpers import api_response

router = APIRouter(prefix="/stats", tags=["Thống kê"])


@router.get("/overview", summary="Thống kê tổng quan")
def get_overview(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin", "staff"))
):
    """
    Lấy số liệu tổng quan: tổng số sự cố, phân bổ theo trạng thái, mức ưu tiên, và sự cố quá hạn.
    """
    stats = stats_service.get_overview_stats(db)
    return api_response(
        success=True,
        data=stats,
        message="Lấy thống kê tổng quan thành công"
    )


@router.get("/by-location", summary="Thống kê theo địa điểm")
def get_by_location(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin", "staff"))
):
    """
    Lấy số lượng sự cố và thời gian xử lý trung bình theo từng khu vực trường học.
    """
    stats = stats_service.get_stats_by_location(db)
    return api_response(
        success=True,
        data=stats,
        message="Lấy thống kê theo địa điểm thành công"
    )


@router.get("/by-type", summary="Thống kê theo loại sự cố")
def get_by_type(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin", "staff"))
):
    """
    Lấy phân bổ số lượng sự cố theo danh mục/loại sự cố.
    """
    stats = stats_service.get_stats_by_type(db)
    return api_response(
        success=True,
        data=stats,
        message="Lấy thống kê theo loại sự cố thành công"
    )


@router.get("/by-month", summary="Thống kê theo tháng")
def get_by_month(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin", "staff"))
):
    """
    Lấy xu hướng số lượng sự cố theo từng tháng (12 tháng gần nhất).
    """
    stats = stats_service.get_stats_by_month(db)
    return api_response(
        success=True,
        data=stats,
        message="Lấy thống kê theo tháng thành công"
    )


@router.get("/avg-resolution-time", summary="Thời gian giải quyết trung bình")
def get_avg_resolution_time(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin", "staff"))
):
    """
    Lấy thời gian xử lý trung bình (tính bằng giờ) chung và theo từng mức ưu tiên.
    """
    stats = stats_service.get_avg_resolution_time(db)
    return api_response(
        success=True,
        data=stats,
        message="Lấy thời gian giải quyết trung bình thành công"
    )


@router.get("/by-staff", summary="Thống kê hiệu suất theo nhân viên kỹ thuật")
def get_by_staff(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin", "staff"))
):
    """
    Lấy số lượng sự cố đã hoàn thành và đang xử lý theo từng kỹ thuật viên.
    """
    stats = stats_service.get_stats_by_staff(db)
    return api_response(
        success=True,
        data=stats,
        message="Lấy thống kê hiệu suất theo nhân viên thành công"
    )


@router.get("/maintenance-recommendations", summary="Khuyến nghị bảo trì phòng ngừa & Tối ưu ngân sách")
def get_maintenance_recommendations(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin", "staff"))
):
    """
    Phân tích tần suất hỏng hóc lặp lại để khuyến nghị thay thế thiết bị hoặc đại tu phòng học.
    """
    recommendations = stats_service.get_maintenance_recommendations(db)
    return api_response(
        success=True,
        data=recommendations,
        message="Tạo khuyến nghị bảo trì cơ sở vật chất thành công"
    )


