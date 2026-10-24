"""
Route Cấu hình Hệ thống - Trọng số thuật toán ưu tiên, danh mục vị trí và loại sự cố.
"""

from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.location import Location
from app.models.incident_type import IncidentType
from app.models.survey import SystemConfig
from app.schemas.incident import (
    LocationOut, LocationCreate, LocationUpdate,
    IncidentTypeOut, IncidentTypeCreate, IncidentTypeUpdate
)
from app.services import priority_service
from app.middleware.auth_middleware import get_current_user, require_role
from app.utils.helpers import api_response

router = APIRouter(prefix="/config", tags=["Cấu hình hệ thống"])


class WeightsUpdate(BaseModel):
    w1: float  # Mức nghiêm trọng (S)
    w2: float  # Số người ảnh hưởng (I)
    w3: float  # Mức rủi ro khu vực (R)
    w4: float  # Thời gian chờ (T)
    w5: float  # Ảnh hưởng học tập (E)


@router.get("/weights", summary="Lấy thông tin trọng số hiện tại của thuật toán")
def get_weights(db: Session = Depends(get_db)):
    """
    Trả về bộ trọng số (w1-w5) hiện tại và các ngưỡng phân loại ưu tiên.
    """
    weights = priority_service.get_weights(db)
    thresholds = priority_service.get_thresholds(db)
    return api_response(
        success=True,
        data={
            "weights": weights,
            "thresholds": thresholds,
            "formula": "P = w1*S + w2*I + w3*R + w4*T + w5*E"
        },
        message="Lấy thông tin trọng số thành công"
    )


@router.put("/weights", summary="Cập nhật trọng số thuật toán (Admin)")
def update_weights(
    data: WeightsUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    """
    Cập nhật bộ trọng số w1-w5. Sau khi cập nhật, tự động tính lại điểm ưu tiên
    cho tất cả các sự cố đang trong quá trình xử lý.
    """
    # Kiểm tra tổng trọng số xấp xỉ 1.0
    total = round(data.w1 + data.w2 + data.w3 + data.w4 + data.w5, 4)
    if not (0.95 <= total <= 1.05):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tổng các trọng số nên bằng 1.0 (Hiện tại: {total})"
        )

    # Lưu hoặc cập nhật trong SystemConfig
    weight_dict = {
        "w1": data.w1,
        "w2": data.w2,
        "w3": data.w3,
        "w4": data.w4,
        "w5": data.w5
    }

    for k, v in weight_dict.items():
        cfg = db.query(SystemConfig).filter(SystemConfig.key == k).first()
        if cfg:
            cfg.value = str(v)
        else:
            cfg = SystemConfig(key=k, value=str(v))
            db.add(cfg)
    db.commit()

    # Tính toán lại toàn bộ sự cố mở
    recalculated_count = priority_service.recalculate_all_open_incidents(db)

    return api_response(
        success=True,
        data={
            "weights": weight_dict,
            "recalculated_incidents": recalculated_count
        },
        message=f"Đã cập nhật trọng số và tính lại {recalculated_count} sự cố đang mở."
    )


# === QUẢN LÝ ĐỊA ĐIỂM (LOCATIONS) ===

@router.get("/locations", summary="Lấy danh sách tất cả các địa điểm")
def get_locations(db: Session = Depends(get_db)):
    """
    Lấy danh sách phòng học, khu vực chức năng trong trường.
    """
    locations = db.query(Location).order_by(Location.building, Location.name).all()
    results = [LocationOut.model_validate(loc).model_dump() for loc in locations]
    return api_response(
        success=True,
        data=results,
        message="Lấy danh sách địa điểm thành công"
    )


@router.post("/locations", summary="Thêm địa điểm mới (Admin)")
def create_location(
    data: LocationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    """
    Thêm địa điểm/khu vực mới trong khuôn viên trường.
    """
    location = Location(
        name=data.name,
        building=data.building,
        floor=data.floor,
        risk_level=data.risk_level,
        description=data.description
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return api_response(
        success=True,
        data=LocationOut.model_validate(location).model_dump(),
        message="Thêm địa điểm thành công"
    )


@router.put("/locations/{location_id}", summary="Cập nhật địa điểm & mức rủi ro (Admin)")
def update_location(
    location_id: int,
    data: LocationUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    """
    Cập nhật tên, tòa nhà, tầng lầu, mô tả và hệ số rủi ro R của địa điểm.
    """
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy địa điểm"
        )

    if data.name is not None:
        location.name = data.name
    if data.building is not None:
        location.building = data.building
    if data.floor is not None:
        location.floor = data.floor
    if data.risk_level is not None:
        location.risk_level = max(1, min(5, data.risk_level))
    if data.description is not None:
        location.description = data.description

    db.commit()
    db.refresh(location)

    # Tính toán lại ưu tiên các sự cố mở tại phòng này nếu mức rủi ro thay đổi
    priority_service.recalculate_all_open_incidents(db)

    return api_response(
        success=True,
        data=LocationOut.model_validate(location).model_dump(),
        message="Cập nhật địa điểm thành công"
    )


@router.delete("/locations/{location_id}", summary="Xóa địa điểm (Admin)")
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    """
    Xóa địa điểm khỏi hệ thống nếu chưa có sự cố ràng buộc.
    """
    from app.models.incident import Incident
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy địa điểm"
        )

    # Kiểm tra xem có sự cố nào gắn với địa điểm này không
    has_incidents = db.query(Incident).filter(Incident.location_id == location_id).count()
    if has_incidents > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể xóa địa điểm này vì đang có {has_incidents} sự cố liên quan"
        )

    db.delete(location)
    db.commit()
    return api_response(
        success=True,
        data={"id": location_id},
        message="Xóa địa điểm thành công"
    )



# === QUẢN LÝ LOẠI SỰ CỐ (INCIDENT TYPES) ===

@router.get("/incident-types", summary="Lấy danh sách các loại sự cố")
def get_incident_types(db: Session = Depends(get_db)):
    """
    Lấy danh mục các loại sự cố trong trường (Điện, Nước, Quạt, Bàn ghế, v.v.).
    """
    types = db.query(IncidentType).order_by(IncidentType.id).all()
    results = [IncidentTypeOut.model_validate(t).model_dump() for t in types]
    return api_response(
        success=True,
        data=results,
        message="Lấy danh mục loại sự cố thành công"
    )


@router.post("/incident-types", summary="Thêm loại sự cố mới (Admin)")
def create_incident_type(
    data: IncidentTypeCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    """
    Thêm loại sự cố mới.
    """
    inc_type = IncidentType(
        name=data.name,
        default_severity=data.default_severity,
        description=data.description,
        is_safety_critical=data.is_safety_critical
    )
    db.add(inc_type)
    db.commit()
    db.refresh(inc_type)
    return api_response(
        success=True,
        data=IncidentTypeOut.model_validate(inc_type).model_dump(),
        message="Thêm loại sự cố thành công"
    )


@router.put("/incident-types/{type_id}", summary="Cập nhật loại sự cố & quy tắc an toàn (Admin)")
def update_incident_type(
    type_id: int,
    data: IncidentTypeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    """
    Cập nhật tên, mức nghiêm trọng mặc định và quy tắc an toàn đặc biệt (Safety Override).
    """
    inc_type = db.query(IncidentType).filter(IncidentType.id == type_id).first()
    if not inc_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy loại sự cố"
        )

    if data.name is not None:
        inc_type.name = data.name
    if data.default_severity is not None:
        inc_type.default_severity = max(1, min(5, data.default_severity))
    if data.description is not None:
        inc_type.description = data.description
    if data.is_safety_critical is not None:
        inc_type.is_safety_critical = data.is_safety_critical

    db.commit()
    db.refresh(inc_type)

    # Tính toán lại ưu tiên các sự cố mở
    priority_service.recalculate_all_open_incidents(db)

    return api_response(
        success=True,
        data=IncidentTypeOut.model_validate(inc_type).model_dump(),
        message="Cập nhật loại sự cố thành công"
    )


@router.delete("/incident-types/{type_id}", summary="Xóa loại sự cố (Admin)")
def delete_incident_type(
    type_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    """
    Xóa loại sự cố khỏi hệ thống nếu chưa có sự cố ràng buộc.
    """
    from app.models.incident import Incident
    inc_type = db.query(IncidentType).filter(IncidentType.id == type_id).first()
    if not inc_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy loại sự cố"
        )

    has_incidents = db.query(Incident).filter(Incident.type_id == type_id).count()
    if has_incidents > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể xóa loại sự cố này vì đang có {has_incidents} sự cố liên quan"
        )

    db.delete(inc_type)
    db.commit()
    return api_response(
        success=True,
        data={"id": type_id},
        message="Xóa loại sự cố thành công"
    )

