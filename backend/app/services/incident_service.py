"""
Service Sự cố - Xử lý logic nghiệp vụ cho quản lý sự cố.
Bao gồm: tạo, lấy, cập nhật trạng thái, phân công, xác nhận.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_
from fastapi import HTTPException, status

from app.models.incident import Incident
from app.models.incident_type import IncidentType
from app.models.location import Location
from app.models.user import User
from app.models.status_history import StatusHistory
from app.models.notification import Notification
from app.services.priority_service import recalculate_incident_priority
from app.utils.helpers import validate_status_transition


def create_incident(db: Session, data: dict, reporter_id: int) -> Incident:
    """
    Tạo sự cố mới từ báo cáo của học sinh.
    
    Quy trình:
    1. Kiểm tra loại sự cố và địa điểm hợp lệ
    2. Tạo bản ghi sự cố
    3. Tính điểm ưu tiên
    4. Ghi lịch sử trạng thái
    
    Args:
        db: Database session
        data: Thông tin sự cố (từ IncidentCreate schema)
        reporter_id: ID người báo cáo
    
    Returns:
        Đối tượng Incident mới tạo
    """
    # Kiểm tra loại sự cố tồn tại
    incident_type = db.query(IncidentType).filter(
        IncidentType.id == data["type_id"]
    ).first()
    if not incident_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Loại sự cố không tồn tại"
        )

    # Kiểm tra địa điểm tồn tại
    location = db.query(Location).filter(Location.id == data["location_id"]).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Địa điểm không tồn tại"
        )

    # Giới hạn giá trị severity và learning_impact trong khoảng 1-5
    severity = max(1, min(5, data.get("severity", incident_type.default_severity)))
    learning_impact = max(1, min(5, data.get("learning_impact", 1)))
    people_affected = max(1, data.get("people_affected", 1))

    # Tạo bản ghi sự cố mới
    incident = Incident(
        reporter_id=reporter_id,
        type_id=data["type_id"],
        location_id=data["location_id"],
        title=data["title"],
        description=data.get("description"),
        severity=severity,
        people_affected=people_affected,
        learning_impact=learning_impact,
        status="reported",
        reported_at=datetime.utcnow(),
        image_paths=json.dumps(data.get("image_paths", [])),
    )

    db.add(incident)
    db.flush()  # Để có ID cho bước tiếp theo

    # Tính điểm ưu tiên
    recalculate_incident_priority(db, incident)

    # Ghi lịch sử trạng thái đầu tiên
    history = StatusHistory(
        incident_id=incident.id,
        changed_by=reporter_id,
        old_status=None,
        new_status="reported",
        notes="Sự cố được báo cáo",
        changed_at=datetime.utcnow(),
    )
    db.add(history)

    # Tạo thông báo đến Ban Quản lý (Admin) và Kỹ thuật CSVC (Staff)
    priority_prefix = {
        "emergency": "🚨 KHẨN CẤP",
        "urgent": "⚠️ CẤP BÁCH",
        "high": "⚡ ƯU TIÊN CAO",
        "normal": "📝 BÁO CÁO MỚI"
    }.get(incident.priority_level, "📝 BÁO CÁO MỚI")

    loc_name = location.name if location else "Khuôn viên trường"
    notif_title = f"{priority_prefix}: {incident.title}"
    notif_msg = f"Sự cố mới tại {loc_name}. Mức ưu tiên: {incident.priority_level.upper()} (P = {incident.priority_score})."

    # Tạo thông báo cho Staff và Admin
    db.add(Notification(
        target_role="staff",
        incident_id=incident.id,
        title=notif_title,
        message=notif_msg,
        priority_level=incident.priority_level,
        is_read=False,
        created_at=datetime.utcnow()
    ))
    db.add(Notification(
        target_role="admin",
        incident_id=incident.id,
        title=notif_title,
        message=notif_msg,
        priority_level=incident.priority_level,
        is_read=False,
        created_at=datetime.utcnow()
    ))

    db.commit()
    db.refresh(incident)

    # Bắn thông báo tức thì ngoại vi (Zalo Webhook / Telegram Bot) nếu là sự cố cấp bách / khẩn cấp
    try:
        from app.services.alert_service import send_external_alert
        reporter = db.query(User).filter(User.id == reporter_id).first()
        reporter_name = reporter.full_name if reporter else "Học sinh"
        send_external_alert(
            db=db,
            incident=incident,
            location_name=loc_name,
            type_name=incident_type.name if incident_type else "Cơ sở vật chất",
            reporter_name=reporter_name
        )
    except Exception as e:
        # Không làm gián đoạn việc lưu sự cố nếu webhook lỗi mạng
        pass

    return incident


def get_incidents(
    db: Session,
    status_filter: Optional[str] = None,
    type_filter: Optional[int] = None,
    location_filter: Optional[int] = None,
    priority_filter: Optional[str] = None,
    sort_by: str = "priority_score",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
    reporter_id: Optional[int] = None,
    search: Optional[str] = None,
    assigned_to: Optional[int] = None,
    building: Optional[str] = None,
    overdue_only: bool = False,
) -> dict:
    """
    Lấy danh sách sự cố với bộ lọc đa chiều, tìm kiếm, sắp xếp và phân trang.
    """
    query = db.query(Incident)

    # === Áp dụng bộ lọc ===
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Incident.title.ilike(search_term),
                Incident.description.ilike(search_term)
            )
        )
    if status_filter:
        query = query.filter(Incident.status == status_filter)
    if type_filter:
        query = query.filter(Incident.type_id == type_filter)
    if location_filter:
        query = query.filter(Incident.location_id == location_filter)
    if priority_filter:
        query = query.filter(Incident.priority_level == priority_filter)
    if reporter_id:
        query = query.filter(Incident.reporter_id == reporter_id)

    # Lọc người được phân công
    if assigned_to == -1:  # Sự cố chưa có ai nhận
        query = query.filter(Incident.assigned_to == None)
    elif assigned_to:
        query = query.filter(Incident.assigned_to == assigned_to)

    # Lọc theo tòa nhà
    if building:
        query = query.join(Location).filter(Location.building == building)

    # Lọc sự cố quá hạn (> 72 giờ chưa giải quyết)
    if overdue_only:
        cutoff = datetime.utcnow() - timedelta(hours=72)
        query = query.filter(
            Incident.reported_at < cutoff,
            Incident.status.in_(["reported", "received", "assigned", "in_progress"])
        )

    # === Đếm tổng số ===
    total = query.count()

    # === Sắp xếp ===
    sort_column = getattr(Incident, sort_by, Incident.priority_score)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # === Phân trang ===
    offset = (page - 1) * page_size
    incidents = query.offset(offset).limit(page_size).all()

    # === Chuyển đổi sang dict với thông tin bổ sung ===
    result = []
    for inc in incidents:
        result.append(_incident_to_dict(db, inc))

    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


def get_incident_by_id(db: Session, incident_id: int) -> dict:
    """
    Lấy chi tiết sự cố theo ID, bao gồm lịch sử trạng thái.
    
    Args:
        db: Database session
        incident_id: ID sự cố
    
    Returns:
        Dict chứa thông tin sự cố và lịch sử
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự cố"
        )

    result = _incident_to_dict(db, incident)

    # Thêm lịch sử trạng thái
    result["status_history"] = _get_status_history(db, incident_id)

    return result


def update_incident_status(
    db: Session, incident_id: int, new_status: str,
    user_id: int, notes: Optional[str] = None,
    resolution_notes: Optional[str] = None
) -> dict:
    """
    Cập nhật trạng thái sự cố.
    
    Kiểm tra:
    1. Sự cố tồn tại
    2. Chuyển trạng thái hợp lệ
    3. Cập nhật mốc thời gian tương ứng
    
    Args:
        db: Database session
        incident_id: ID sự cố
        new_status: Trạng thái mới
        user_id: ID người thực hiện
        notes: Ghi chú
        resolution_notes: Ghi chú giải quyết
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự cố"
        )

    old_status = incident.status

    # Kiểm tra chuyển trạng thái hợp lệ
    if not validate_status_transition(old_status, new_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể chuyển từ '{old_status}' sang '{new_status}'"
        )

    # Cập nhật trạng thái
    incident.status = new_status

    # Cập nhật mốc thời gian tương ứng
    now = datetime.utcnow()
    if new_status == "received":
        incident.received_at = now
    elif new_status == "assigned":
        incident.assigned_at = now
    elif new_status == "resolved":
        incident.resolved_at = now
        if resolution_notes:
            incident.resolution_notes = resolution_notes
    elif new_status == "confirmed":
        incident.confirmed_at = now

    # Ghi lịch sử thay đổi
    history = StatusHistory(
        incident_id=incident_id,
        changed_by=user_id,
        old_status=old_status,
        new_status=new_status,
        notes=notes,
        changed_at=now,
    )
    db.add(history)
    db.commit()
    db.refresh(incident)

    return _incident_to_dict(db, incident)


def assign_incident(
    db: Session, incident_id: int, assigned_to_id: int, user_id: int
) -> dict:
    """
    Phân công sự cố cho nhân viên xử lý.
    
    Args:
        db: Database session
        incident_id: ID sự cố
        assigned_to_id: ID nhân viên được phân công
        user_id: ID người thực hiện phân công
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự cố"
        )

    # Kiểm tra nhân viên tồn tại và có vai trò phù hợp
    assignee = db.query(User).filter(User.id == assigned_to_id).first()
    if not assignee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không tìm thấy nhân viên"
        )
    if assignee.role not in ("staff", "admin"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ có thể phân công cho nhân viên hoặc quản trị viên"
        )

    # Cập nhật phân công
    old_status = incident.status
    incident.assigned_to = assigned_to_id
    incident.assigned_at = datetime.utcnow()

    # Tự động chuyển trạng thái sang "assigned" nếu đang ở "reported" hoặc "received"
    if incident.status in ("reported", "received"):
        incident.status = "assigned"

        # Ghi lịch sử
        history = StatusHistory(
            incident_id=incident_id,
            changed_by=user_id,
            old_status=old_status,
            new_status="assigned",
            notes=f"Phân công cho {assignee.full_name}",
            changed_at=datetime.utcnow(),
        )
        db.add(history)

    db.commit()
    db.refresh(incident)
    return _incident_to_dict(db, incident)


def confirm_resolution(db: Session, incident_id: int, user_id: int) -> dict:
    """
    Học sinh xác nhận sự cố đã được giải quyết.
    
    Chỉ cho phép:
    - Người báo cáo xác nhận sự cố của mình
    - Sự cố phải ở trạng thái "resolved"
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự cố"
        )

    # Kiểm tra quyền: chỉ người báo cáo mới được xác nhận
    if incident.reporter_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ người báo cáo mới có thể xác nhận giải quyết"
        )

    # Kiểm tra trạng thái: phải đang ở "resolved"
    if incident.status != "resolved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sự cố phải ở trạng thái 'đã giải quyết' để xác nhận"
        )

    # Cập nhật trạng thái
    incident.status = "confirmed"
    incident.confirmed_at = datetime.utcnow()

    history = StatusHistory(
        incident_id=incident_id,
        changed_by=user_id,
        old_status="resolved",
        new_status="confirmed",
        notes="Học sinh xác nhận đã giải quyết",
        changed_at=datetime.utcnow(),
    )
    db.add(history)
    db.commit()
    db.refresh(incident)
    return _incident_to_dict(db, incident)


def get_incident_history(db: Session, incident_id: int) -> list:
    """Lấy lịch sử thay đổi trạng thái của sự cố."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự cố"
        )
    return _get_status_history(db, incident_id)


# === Hàm nội bộ ===

def _incident_to_dict(db: Session, incident: Incident) -> dict:
    """Chuyển đối tượng Incident thành dict với thông tin bổ sung."""
    # Lấy tên người báo cáo
    reporter = db.query(User).filter(User.id == incident.reporter_id).first()
    reporter_name = reporter.full_name if reporter else None

    # Lấy tên loại sự cố
    inc_type = db.query(IncidentType).filter(
        IncidentType.id == incident.type_id
    ).first()
    type_name = inc_type.name if inc_type else None

    # Lấy tên địa điểm
    location = db.query(Location).filter(Location.id == incident.location_id).first()
    location_name = location.name if location else None

    # Lấy tên người được phân công
    assignee_name = None
    if incident.assigned_to:
        assignee = db.query(User).filter(User.id == incident.assigned_to).first()
        assignee_name = assignee.full_name if assignee else None

    # Parse image_paths từ JSON string
    image_paths = incident.get_image_paths()

    return {
        "id": incident.id,
        "reporter_id": incident.reporter_id,
        "reporter_name": reporter_name,
        "type_id": incident.type_id,
        "type_name": type_name,
        "location_id": incident.location_id,
        "location_name": location_name,
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "people_affected": incident.people_affected,
        "learning_impact": incident.learning_impact,
        "priority_score": incident.priority_score,
        "priority_level": incident.priority_level,
        "status": incident.status,
        "assigned_to": incident.assigned_to,
        "assignee_name": assignee_name,
        "reported_at": incident.reported_at.isoformat() if incident.reported_at else None,
        "received_at": incident.received_at.isoformat() if incident.received_at else None,
        "assigned_at": incident.assigned_at.isoformat() if incident.assigned_at else None,
        "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
        "confirmed_at": incident.confirmed_at.isoformat() if incident.confirmed_at else None,
        "resolution_notes": incident.resolution_notes,
        "image_paths": image_paths,
    }


def _get_status_history(db: Session, incident_id: int) -> list:
    """Lấy danh sách lịch sử thay đổi trạng thái."""
    histories = db.query(StatusHistory).filter(
        StatusHistory.incident_id == incident_id
    ).order_by(StatusHistory.changed_at).all()

    result = []
    for h in histories:
        user = db.query(User).filter(User.id == h.changed_by).first()
        result.append({
            "id": h.id,
            "incident_id": h.incident_id,
            "changed_by": h.changed_by,
            "changed_by_name": user.full_name if user else None,
            "old_status": h.old_status,
            "new_status": h.new_status,
            "notes": h.notes,
            "changed_at": h.changed_at.isoformat() if h.changed_at else None,
        })
    return result


def update_incident_info(db: Session, incident_id: int, data: dict, user_id: int) -> Incident:
    """
    Cập nhật nội dung sự cố (tiêu đề, mô tả, mức nghiêm trọng, phòng học...)
    và tự động tính lại điểm ưu tiên P.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự cố"
        )

    if data.get("title"):
        incident.title = data["title"]
    if "description" in data:
        incident.description = data["description"]
    if data.get("type_id"):
        incident.type_id = data["type_id"]
    if data.get("location_id"):
        incident.location_id = data["location_id"]
    if data.get("severity"):
        incident.severity = max(1, min(5, data["severity"]))
    if data.get("people_affected"):
        incident.people_affected = max(1, data["people_affected"])
    if data.get("learning_impact"):
        incident.learning_impact = max(1, min(5, data["learning_impact"]))

    # Tự động tính lại điểm ưu tiên
    recalculate_incident_priority(db, incident)

    # Ghi log lịch sử
    history = StatusHistory(
        incident_id=incident.id,
        changed_by=user_id,
        old_status=incident.status,
        new_status=incident.status,
        notes="Cập nhật thông tin chi tiết sự cố",
        changed_at=datetime.utcnow()
    )
    db.add(history)
    db.commit()
    db.refresh(incident)
    return incident


def delete_incident(db: Session, incident_id: int) -> dict:
    """
    Xóa sự cố khỏi hệ thống cùng toàn bộ lịch sử liên quan (Admin).
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự cố"
        )

    # Xóa lịch sử trạng thái trước
    db.query(StatusHistory).filter(StatusHistory.incident_id == incident_id).delete()
    # Xóa sự cố
    db.delete(incident)
    db.commit()
    return {"id": incident_id, "deleted": True}

