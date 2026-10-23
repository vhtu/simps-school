"""
Service Thống kê - Tính toán các chỉ số thống kê cho dashboard admin.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.models.incident import Incident
from app.models.location import Location
from app.models.incident_type import IncidentType
from app.models.user import User


def get_overview_stats(db: Session) -> dict:
    """
    Thống kê tổng quan hệ thống.
    
    Trả về:
    - Tổng số sự cố
    - Số lượng theo trạng thái
    - Số lượng theo mức ưu tiên
    - Số sự cố quá hạn (> 72h chưa giải quyết)
    """
    total = db.query(Incident).count()

    # Đếm theo trạng thái
    status_counts = {}
    statuses = ["reported", "received", "assigned", "in_progress",
                "resolved", "confirmed", "closed"]
    for s in statuses:
        count = db.query(Incident).filter(Incident.status == s).count()
        status_counts[s] = count

    # Đếm theo mức ưu tiên
    priority_counts = {}
    priorities = ["normal", "high", "urgent", "emergency"]
    for p in priorities:
        count = db.query(Incident).filter(Incident.priority_level == p).count()
        priority_counts[p] = count

    # Đếm sự cố quá hạn (> 72 giờ, chưa giải quyết)
    overdue_threshold = datetime.utcnow() - timedelta(hours=72)
    open_statuses = ["reported", "received", "assigned", "in_progress"]
    overdue_count = db.query(Incident).filter(
        Incident.status.in_(open_statuses),
        Incident.reported_at < overdue_threshold
    ).count()

    return {
        "total_incidents": total,
        "by_status": status_counts,
        "by_priority": priority_counts,
        "overdue_count": overdue_count,
    }


def get_stats_by_location(db: Session) -> list:
    """
    Thống kê theo địa điểm.
    Trả về số lượng sự cố và thời gian giải quyết trung bình cho mỗi địa điểm.
    """
    locations = db.query(Location).all()
    result = []

    for loc in locations:
        incidents = db.query(Incident).filter(
            Incident.location_id == loc.id
        ).all()

        incident_count = len(incidents)

        # Tính thời gian giải quyết trung bình (chỉ tính những sự cố đã giải quyết)
        resolution_times = []
        for inc in incidents:
            if inc.resolved_at and inc.reported_at:
                delta = (inc.resolved_at - inc.reported_at).total_seconds() / 3600
                resolution_times.append(delta)

        avg_resolution = None
        if resolution_times:
            avg_resolution = round(sum(resolution_times) / len(resolution_times), 2)

        result.append({
            "location_id": loc.id,
            "location_name": loc.name,
            "incident_count": incident_count,
            "avg_resolution_hours": avg_resolution,
        })

    # Sắp xếp theo số lượng giảm dần
    result.sort(key=lambda x: x["incident_count"], reverse=True)
    return result


def get_stats_by_type(db: Session) -> list:
    """
    Thống kê theo loại sự cố.
    Trả về số lượng sự cố cho mỗi loại.
    """
    incident_types = db.query(IncidentType).all()
    result = []

    for it in incident_types:
        count = db.query(Incident).filter(Incident.type_id == it.id).count()
        result.append({
            "type_id": it.id,
            "type_name": it.name,
            "incident_count": count,
        })

    result.sort(key=lambda x: x["incident_count"], reverse=True)
    return result


def get_stats_by_month(db: Session) -> list:
    """
    Thống kê theo tháng (12 tháng gần nhất).
    Trả về số lượng sự cố mỗi tháng.
    """
    result = []
    now = datetime.utcnow()

    for i in range(11, -1, -1):
        # Tính tháng cần thống kê
        month_date = now - timedelta(days=30 * i)
        year = month_date.year
        month = month_date.month

        # Đếm sự cố trong tháng đó
        count = db.query(Incident).filter(
            extract("year", Incident.reported_at) == year,
            extract("month", Incident.reported_at) == month,
        ).count()

        result.append({
            "month": f"{year}-{month:02d}",
            "incident_count": count,
        })

    return result


def get_avg_resolution_time(db: Session) -> dict:
    """
    Thống kê thời gian giải quyết trung bình.
    Tính tổng thể và theo từng mức ưu tiên.
    """
    # Lấy tất cả sự cố đã giải quyết
    resolved_incidents = db.query(Incident).filter(
        Incident.resolved_at.isnot(None),
        Incident.reported_at.isnot(None),
    ).all()

    # Tính tổng thể
    all_times = []
    by_priority = {}

    for inc in resolved_incidents:
        hours = (inc.resolved_at - inc.reported_at).total_seconds() / 3600
        all_times.append(hours)

        # Nhóm theo mức ưu tiên
        level = inc.priority_level
        if level not in by_priority:
            by_priority[level] = []
        by_priority[level].append(hours)

    overall_avg = None
    if all_times:
        overall_avg = round(sum(all_times) / len(all_times), 2)

    # Tính trung bình cho mỗi mức ưu tiên
    priority_avg = {}
    for level, times in by_priority.items():
        priority_avg[level] = round(sum(times) / len(times), 2)

    return {
        "overall_avg_hours": overall_avg,
        "by_priority": priority_avg,
    }


def get_stats_by_staff(db: Session) -> list:
    """
    Thống kê hiệu suất theo từng nhân viên kỹ thuật CSVC.
    Bao gồm số sự cố đang phụ trách và số sự cố đã hoàn thành.
    """
    staff_members = db.query(User).filter(User.role == "staff").all()
    result = []

    for staff in staff_members:
        in_progress = db.query(Incident).filter(
            Incident.assigned_to == staff.id,
            Incident.status.in_(["assigned", "in_progress"])
        ).count()

        resolved = db.query(Incident).filter(
            Incident.assigned_to == staff.id,
            Incident.status.in_(["resolved", "confirmed", "closed"])
        ).count()

        result.append({
            "staff_id": staff.id,
            "staff_name": staff.full_name,
            "in_progress_count": in_progress,
            "resolved_count": resolved,
            "total_assigned": in_progress + resolved
        })

    result.sort(key=lambda x: x["resolved_count"], reverse=True)
    return result

