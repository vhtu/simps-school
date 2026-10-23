"""
⭐ Service Thuật toán Ưu tiên - PHẦN CỐT LÕI CỦA HỆ THỐNG ⭐

Công thức tính điểm ưu tiên:
    P = w1*S + w2*I + w3*R + w4*T + w5*E

Trong đó:
    S = severity (mức nghiêm trọng, 1-5)
    I = normalize(people_affected) → chuyển về thang 1-5
    R = location.risk_level (mức rủi ro khu vực, 1-5)
    T = normalize_time(hours_waiting) → chuyển về thang 1-5
    E = learning_impact (ảnh hưởng học tập, 1-5)

Quy tắc ghi đè an toàn (Safety Override):
    Nếu location.risk_level >= 5 HOẶC incident_type.is_safety_critical = True:
    → priority_level = "emergency", score = 999

Trọng số mặc định (từ khảo sát):
    w1=0.30, w2=0.20, w3=0.20, w4=0.15, w5=0.15

Ngưỡng phân loại:
    emergency = override (ghi đè)
    urgent >= 3.5
    high >= 2.5
    normal < 2.5
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.location import Location
from app.models.incident_type import IncidentType
from app.models.survey import SystemConfig
from app.config import DEFAULT_WEIGHTS, PRIORITY_THRESHOLDS


def get_weights(db: Session) -> dict:
    """
    Lấy trọng số hiện tại từ cơ sở dữ liệu.
    Nếu chưa có trong DB, trả về trọng số mặc định.
    
    Returns:
        Dict chứa w1, w2, w3, w4, w5
    """
    weights = {}
    for key in ["w1", "w2", "w3", "w4", "w5"]:
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if config:
            weights[key] = float(config.value)
        else:
            weights[key] = DEFAULT_WEIGHTS[key]
    return weights


def get_thresholds(db: Session) -> dict:
    """
    Lấy ngưỡng phân loại từ cơ sở dữ liệu.
    Nếu chưa có trong DB, trả về ngưỡng mặc định.
    """
    thresholds = {}
    for key in ["urgent", "high"]:
        config_key = f"threshold_{key}"
        config = db.query(SystemConfig).filter(SystemConfig.key == config_key).first()
        if config:
            thresholds[key] = float(config.value)
        else:
            thresholds[key] = PRIORITY_THRESHOLDS[key]
    return thresholds


def normalize_people_affected(count: int) -> int:
    """
    Chuẩn hóa số người bị ảnh hưởng về thang 1-5.
    
    Quy tắc chuyển đổi:
        1-5 người   → 1 (ít ảnh hưởng)
        6-20 người  → 2
        21-50 người → 3
        51-200 người → 4
        >200 người  → 5 (ảnh hưởng rất rộng)
    
    Args:
        count: Số người bị ảnh hưởng
    
    Returns:
        Giá trị chuẩn hóa (1-5)
    """
    if count <= 5:
        return 1
    elif count <= 20:
        return 2
    elif count <= 50:
        return 3
    elif count <= 200:
        return 4
    else:
        return 5


def normalize_time(hours_waiting: float) -> int:
    """
    Chuẩn hóa thời gian chờ về thang 1-5.
    Sự cố chờ càng lâu → điểm thời gian càng cao → ưu tiên càng cao.
    
    Quy tắc chuyển đổi:
        < 2 giờ     → 1 (mới báo cáo)
        2-8 giờ     → 2
        8-24 giờ    → 3
        24-72 giờ   → 4
        > 72 giờ    → 5 (đã chờ quá lâu)
    
    Args:
        hours_waiting: Số giờ đã chờ
    
    Returns:
        Giá trị chuẩn hóa (1-5)
    """
    if hours_waiting < 2:
        return 1
    elif hours_waiting <= 8:
        return 2
    elif hours_waiting <= 24:
        return 3
    elif hours_waiting <= 72:
        return 4
    else:
        return 5


def check_safety_override(db: Session, incident: Incident) -> bool:
    """
    Kiểm tra điều kiện ghi đè an toàn (Safety Override).
    
    Nếu một trong hai điều kiện sau đúng, sự cố tự động được nâng
    lên mức "emergency" (khẩn cấp nhất):
    
    1. Khu vực có mức rủi ro >= 5 (khu vực nguy hiểm)
    2. Loại sự cố được đánh dấu is_safety_critical (liên quan an toàn)
    
    Args:
        db: Database session
        incident: Đối tượng sự cố cần kiểm tra
    
    Returns:
        True nếu cần ghi đè an toàn
    """
    # Kiểm tra mức rủi ro khu vực
    location = db.query(Location).filter(Location.id == incident.location_id).first()
    if location and location.risk_level >= 5:
        return True

    # Kiểm tra loại sự cố liên quan an toàn
    incident_type = db.query(IncidentType).filter(
        IncidentType.id == incident.type_id
    ).first()
    if incident_type and incident_type.is_safety_critical:
        return True

    return False


def calculate_priority(db: Session, incident: Incident) -> tuple:
    """
    ⭐ HÀM CHÍNH: Tính điểm ưu tiên cho một sự cố.
    
    Công thức: P = w1*S + w2*I + w3*R + w4*T + w5*E
    
    Bước 1: Kiểm tra Safety Override
    Bước 2: Lấy trọng số từ cấu hình
    Bước 3: Tính các thành phần (S, I, R, T, E)
    Bước 4: Tính điểm tổng hợp
    Bước 5: Phân loại mức ưu tiên dựa trên ngưỡng
    
    Args:
        db: Database session
        incident: Đối tượng sự cố cần tính điểm
    
    Returns:
        Tuple (priority_score, priority_level)
        - priority_score: Điểm ưu tiên (float)
        - priority_level: Mức ưu tiên ("normal"/"high"/"urgent"/"emergency")
    """
    # === Bước 1: Kiểm tra Safety Override ===
    if check_safety_override(db, incident):
        return (999.0, "emergency")

    # === Bước 2: Lấy trọng số từ cấu hình ===
    weights = get_weights(db)

    # === Bước 3: Tính các thành phần ===
    # S: Mức nghiêm trọng (đã có sẵn, 1-5)
    S = incident.severity

    # I: Chuẩn hóa số người bị ảnh hưởng → 1-5
    I = normalize_people_affected(incident.people_affected)

    # R: Mức rủi ro khu vực (lấy từ bảng locations)
    location = db.query(Location).filter(Location.id == incident.location_id).first()
    R = location.risk_level if location else 1

    # T: Chuẩn hóa thời gian chờ → 1-5
    if incident.reported_at:
        hours_waiting = (datetime.utcnow() - incident.reported_at).total_seconds() / 3600
    else:
        hours_waiting = 0
    T = normalize_time(hours_waiting)

    # E: Ảnh hưởng học tập (đã có sẵn, 1-5)
    E = incident.learning_impact

    # === Bước 4: Tính điểm tổng hợp ===
    priority_score = (
        weights["w1"] * S +
        weights["w2"] * I +
        weights["w3"] * R +
        weights["w4"] * T +
        weights["w5"] * E
    )

    # Làm tròn 2 chữ số thập phân
    priority_score = round(priority_score, 2)

    # === Bước 5: Phân loại mức ưu tiên ===
    thresholds = get_thresholds(db)
    if priority_score >= thresholds["urgent"]:
        priority_level = "urgent"
    elif priority_score >= thresholds["high"]:
        priority_level = "high"
    else:
        priority_level = "normal"

    return (priority_score, priority_level)


def recalculate_incident_priority(db: Session, incident: Incident):
    """
    Tính lại và cập nhật điểm ưu tiên cho một sự cố.
    
    Gọi hàm này khi:
    1. Sự cố mới được tạo
    2. Trọng số được cập nhật
    3. Cần cập nhật theo thời gian chờ
    
    Args:
        db: Database session
        incident: Đối tượng sự cố cần cập nhật
    """
    score, level = calculate_priority(db, incident)
    incident.priority_score = score
    incident.priority_level = level
    db.commit()


def recalculate_all_open_incidents(db: Session):
    """
    Tính lại điểm ưu tiên cho TẤT CẢ sự cố đang mở.
    
    Gọi hàm này khi trọng số được cập nhật bởi admin,
    để đảm bảo tất cả sự cố phản ánh đúng trọng số mới.
    
    Chỉ tính lại cho sự cố chưa đóng (không phải "closed" hay "confirmed").
    """
    # Lấy tất cả sự cố chưa đóng
    open_statuses = ["reported", "received", "assigned", "in_progress", "resolved"]
    open_incidents = db.query(Incident).filter(
        Incident.status.in_(open_statuses)
    ).all()

    updated_count = 0
    for incident in open_incidents:
        score, level = calculate_priority(db, incident)
        incident.priority_score = score
        incident.priority_level = level
        updated_count += 1

    db.commit()
    return updated_count
