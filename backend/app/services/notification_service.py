"""
Service Thông báo (Notification Service) - Xử lý thông báo đến Admin & Kỹ thuật CSVC.
"""

from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.models.notification import Notification


def get_user_notifications(
    db: Session,
    user_role: str,
    user_id: int,
    unread_only: bool = False,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Lấy danh sách thông báo dành cho vai trò người dùng (staff/admin) hoặc cá nhân.
    """
    query = db.query(Notification).filter(
        or_(
            Notification.target_role == user_role,
            Notification.target_role == "all",
            Notification.user_id == user_id
        )
    )

    # Đếm số lượng chưa đọc
    unread_count = query.filter(Notification.is_read == False).count()

    if unread_only:
        query = query.filter(Notification.is_read == False)

    notifications = query.order_by(desc(Notification.created_at)).limit(limit).all()

    items = []
    for n in notifications:
        items.append({
            "id": n.id,
            "incident_id": n.incident_id,
            "title": n.title,
            "message": n.message,
            "priority_level": n.priority_level,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None
        })

    return {
        "items": items,
        "unread_count": unread_count
    }


def mark_notification_read(db: Session, notification_id: int) -> bool:
    """Đánh dấu một thông báo là đã đọc"""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if notif:
        notif.is_read = True
        db.commit()
        return True
    return False


def mark_all_notifications_read(db: Session, user_role: str, user_id: int) -> int:
    """Đánh dấu toàn bộ thông báo của vai trò là đã đọc"""
    notifs = db.query(Notification).filter(
        or_(
            Notification.target_role == user_role,
            Notification.target_role == "all",
            Notification.user_id == user_id
        ),
        Notification.is_read == False
    ).all()

    count = len(notifs)
    for n in notifs:
        n.is_read = True
    db.commit()
    return count
