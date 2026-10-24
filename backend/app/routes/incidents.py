"""
Route Quản lý Sự cố - Báo cáo, danh sách, chi tiết, cập nhật trạng thái, phân công, upload ảnh.
"""

import os
import uuid
import aiofiles
from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentUpdate, StatusUpdate, AssignRequest
from app.services import incident_service
from app.middleware.auth_middleware import get_current_user, require_role
from app.utils.helpers import api_response
from app.config import UPLOAD_DIR

router = APIRouter(prefix="/incidents", tags=["Sự cố"])


@router.post("", summary="Tạo báo cáo sự cố mới")
def create_incident(
    data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tạo báo cáo sự cố mới. Hệ thống sẽ tự động tính điểm ưu tiên và xếp hạng.
    Học sinh, nhân viên hoặc admin đều có thể báo cáo sự cố.
    """
    incident = incident_service.create_incident(
        db=db,
        data=data.model_dump(),
        reporter_id=current_user.id
    )
    incident_detail = incident_service.get_incident_by_id(db, incident.id)
    return api_response(
        success=True,
        data=incident_detail,
        message="Báo cáo sự cố thành công"
    )


@router.get("", summary="Lấy danh sách sự cố (phân trang, lọc, sắp xếp)")
def get_incidents(
    status: Optional[str] = Query(None, description="Lọc theo trạng thái"),
    type_id: Optional[int] = Query(None, description="Lọc theo loại sự cố"),
    location_id: Optional[int] = Query(None, description="Lọc theo địa điểm"),
    priority_level: Optional[str] = Query(None, description="Lọc theo mức ưu tiên (normal, high, urgent, emergency)"),
    search: Optional[str] = Query(None, description="Tìm kiếm từ khóa theo tiêu đề hoặc mô tả"),
    assigned_to: Optional[int] = Query(None, description="Lọc theo ID nhân viên phụ trách (-1 nếu chưa phân công)"),
    building: Optional[str] = Query(None, description="Lọc theo tòa nhà (Tòa A, Tòa B...)"),
    overdue_only: bool = Query(False, description="Chỉ lấy sự cố quá hạn (> 72h chưa giải quyết)"),
    sort_by: str = Query("priority_score", description="Trường sắp xếp (priority_score, reported_at)"),
    sort_order: str = Query("desc", description="Thứ tự sắp xếp (asc, desc)"),
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(20, ge=1, le=500, description="Kích thước trang"),
    my_reports: bool = Query(False, description="Chỉ lấy các sự cố do người dùng hiện tại báo cáo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách sự cố.
    - Học sinh có thể lọc báo cáo của chính mình qua query `my_reports=true`.
    - Nhân viên và Admin có thể lọc đa chiều (tìm kiếm, tòa nhà, loại sự cố, người phụ trách, quá hạn).
    """
    reporter_id = current_user.id if my_reports else None

    result = incident_service.get_incidents(
        db=db,
        status_filter=status,
        type_filter=type_id,
        location_filter=location_id,
        priority_filter=priority_level,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
        reporter_id=reporter_id,
        search=search,
        assigned_to=assigned_to,
        building=building,
        overdue_only=overdue_only,
    )
    return api_response(
        success=True,
        data=result,
        message="Lấy danh sách sự cố thành công"
    )


@router.get("/{incident_id}", summary="Xem chi tiết sự cố")
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thông tin chi tiết một sự cố cùng toàn bộ tiến trình lịch sử trạng thái.
    """
    incident = incident_service.get_incident_by_id(db, incident_id)
    return api_response(
        success=True,
        data=incident,
        message="Lấy chi tiết sự cố thành công"
    )


@router.patch("/{incident_id}/status", summary="Cập nhật trạng thái sự cố")
def update_status(
    incident_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("staff", "admin"))
):
    """
    Cập nhật trạng thái xử lý sự cố (Dành cho Nhân viên CSVC và Admin).
    Các trạng thái: received, assigned, in_progress, resolved, closed.
    """
    updated = incident_service.update_incident_status(
        db=db,
        incident_id=incident_id,
        new_status=data.status,
        user_id=current_user.id,
        notes=data.notes,
        resolution_notes=data.resolution_notes
    )
    return api_response(
        success=True,
        data=updated,
        message="Cập nhật trạng thái thành công"
    )


@router.patch("/{incident_id}/assign", summary="Phân công nhân viên xử lý sự cố")
def assign_incident(
    incident_id: int,
    data: AssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("staff", "admin"))
):
    """
    Phân công người xử lý sự cố.
    """
    assigned = incident_service.assign_incident(
        db=db,
        incident_id=incident_id,
        assigned_to_id=data.assigned_to,
        user_id=current_user.id
    )
    return api_response(
        success=True,
        data=assigned,
        message="Phân công xử lý thành công"
    )


@router.post("/{incident_id}/confirm", summary="Học sinh xác nhận kết quả xử lý")
def confirm_resolution(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Người báo cáo xác nhận sự cố đã được khắc phục hoàn tất.
    """
    confirmed = incident_service.confirm_resolution(
        db=db,
        incident_id=incident_id,
        user_id=current_user.id
    )
    return api_response(
        success=True,
        data=confirmed,
        message="Xác nhận sự cố thành công"
    )


@router.get("/{incident_id}/history", summary="Lấy lịch sử trạng thái của sự cố")
def get_incident_history(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách các lần thay đổi trạng thái của sự cố.
    """
    history = incident_service.get_incident_history(db, incident_id)
    return api_response(
        success=True,
        data=history,
        message="Lấy lịch sử trạng thái thành công"
    )


@router.put("/{incident_id}", summary="Cập nhật thông tin chi tiết sự cố")
def update_incident(
    incident_id: int,
    data: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "staff"))
):
    """
    Cập nhật tiêu đề, mô tả, mức độ nghiêm trọng, phòng học... và tính lại điểm P.
    """
    updated = incident_service.update_incident_info(
        db=db,
        incident_id=incident_id,
        data=data.model_dump(exclude_unset=True),
        user_id=current_user.id
    )
    detail = incident_service.get_incident_by_id(db, incident_id)
    return api_response(
        success=True,
        data=detail,
        message="Cập nhật thông tin sự cố thành công"
    )


@router.delete("/{incident_id}", summary="Xóa sự cố khỏi hệ thống (Admin)")
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    """
    Admin xóa sự cố và toàn bộ lịch sử liên quan.
    """
    res = incident_service.delete_incident(db, incident_id)
    return api_response(
        success=True,
        data=res,
        message="Đã xóa sự cố thành công"
    )



@router.post("/upload-image", summary="Upload hình ảnh minh họa sự cố")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload hình ảnh minh chứng sự cố, lưu vào thư mục static uploads.
    Trả về URL đường dẫn tương đối của ảnh.
    """
    # Kiểm tra loại file
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng ảnh không hợp lệ (chỉ hỗ trợ JPG, PNG, WEBP, GIF)"
        )

    # Đảm bảo thư mục upload tồn tại
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Đặt tên file ngẫu nhiên tránh trùng lặp
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    return api_response(
        success=True,
        data={"url": f"/uploads/{filename}", "filename": filename},
        message="Upload hình ảnh thành công"
    )
