"""
Script Khởi tạo Dữ liệu Mẫu (Seed Data) cho Hệ thống SIMPS.
Chạy: python -m seeds.seed_data (từ thư mục backend/)
"""

import sys
import os
import json
from datetime import datetime, timedelta
import random

# Thêm thư mục backend vào sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.location import Location
from app.models.incident_type import IncidentType
from app.models.incident import Incident
from app.models.status_history import StatusHistory
from app.models.survey import SystemConfig
from app.services.auth_service import hash_password
from app.services.priority_service import recalculate_incident_priority


def seed_database():
    print("=" * 60)
    print("Bắt đầu khởi tạo dữ liệu mẫu cho SIMPS...")
    print("=" * 60)

    # Đảm bảo bảng tồn tại
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Cấu hình hệ thống (Weights & Thresholds)
        print("1. Cấu hình trọng số thuật toán...")
        configs = [
            ("w1", "0.30"),
            ("w2", "0.20"),
            ("w3", "0.20"),
            ("w4", "0.15"),
            ("w5", "0.15"),
            ("threshold_urgent", "3.5"),
            ("threshold_high", "2.5"),
        ]
        for key, val in configs:
            existing = db.query(SystemConfig).filter(SystemConfig.key == key).first()
            if not existing:
                db.add(SystemConfig(key=key, value=val))
        db.commit()

        # 2. Người dùng (Users)
        print("2. Tạo người dùng mẫu...")
        # Admin
        admins = [
            {"username": "admin", "full_name": "Quản Trị Viên Hệ Thống", "role": "admin", "email": "admin@truong.edu.vn"},
            {"username": "hieutruong", "full_name": "Thầy Hiệu Trưởng", "role": "admin", "email": "hieutruong@truong.edu.vn"},
            {"username": "quanlycsvc", "full_name": "Trưởng Ban CSVC", "role": "admin", "email": "csvc@truong.edu.vn"},
        ]
        created_admins = []
        for u in admins:
            user = db.query(User).filter(User.username == u["username"]).first()
            if not user:
                user = User(
                    username=u["username"],
                    password_hash=hash_password("admin123" if u["username"] == "admin" else "123456"),
                    full_name=u["full_name"],
                    role=u["role"],
                    email=u["email"],
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            created_admins.append(user)

        # Nhân viên CSVC (Staff)
        staff_data = [
            {"username": "nhanvien_dien", "full_name": "Nguyễn Văn Tuấn (Kỹ thuật Điện)", "role": "staff"},
            {"username": "nhanvien_nuoc", "full_name": "Trần Văn Nam (Thợ Nước & Mộc)", "role": "staff"},
            {"username": "nhanvien_cntt", "full_name": "Lê Quang Minh (Kỹ thuật CNTT)", "role": "staff"},
            {"username": "nhanvien_vesinh", "full_name": "Phạm Thị Hương (Tổ Vệ Sinh)", "role": "staff"},
            {"username": "nhanvien_baotri", "full_name": "Hoàng Đức Thắng (Bảo trì chung)", "role": "staff"},
        ]
        created_staff = []
        for u in staff_data:
            user = db.query(User).filter(User.username == u["username"]).first()
            if not user:
                user = User(
                    username=u["username"],
                    password_hash=hash_password("123456"),
                    full_name=u["full_name"],
                    role=u["role"],
                    email=f"{u['username']}@truong.edu.vn",
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            created_staff.append(user)

        # Học sinh (Students)
        created_students = []
        for i in range(1, 21):
            uname = f"hs{i:02d}"
            user = db.query(User).filter(User.username == uname).first()
            if not user:
                user = User(
                    username=uname,
                    password_hash=hash_password("123456"),
                    full_name=f"Học Sinh Lớp 10A{(i % 4) + 1} - Số {i:02d}",
                    role="student",
                    class_name=f"10A{(i % 4) + 1}",
                    email=f"{uname}@hocsinh.truong.edu.vn",
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            created_students.append(user)

        # 3. Địa điểm (Locations)
        print("3. Tạo danh mục địa điểm...")
        locations_data = [
            {"name": "Phòng 101 (Lớp 10A1)", "building": "Tòa A", "floor": "Tầng 1", "risk_level": 2, "description": "Phòng học thông thường"},
            {"name": "Phòng 102 (Lớp 10A2)", "building": "Tòa A", "floor": "Tầng 1", "risk_level": 2, "description": "Phòng học thông thường"},
            {"name": "Phòng 201 (Lớp 11A1)", "building": "Tòa A", "floor": "Tầng 2", "risk_level": 2, "description": "Phòng học tầng 2"},
            {"name": "Phòng Tin học 1", "building": "Tòa B", "floor": "Tầng 2", "risk_level": 3, "description": "Nhiều máy móc, thiết bị điện"},
            {"name": "Phòng Tin học 2", "building": "Tòa B", "floor": "Tầng 2", "risk_level": 3, "description": "Nhiều máy móc, thiết bị điện"},
            {"name": "Phòng Thí nghiệm Hóa học", "building": "Tòa C", "floor": "Tầng 1", "risk_level": 5, "description": "Khu vực hóa chất, rủi ro an toàn rất cao"},
            {"name": "Phòng Thí nghiệm Vật lý", "building": "Tòa C", "floor": "Tầng 2", "risk_level": 4, "description": "Nguồn điện áp, dụng cụ thí nghiệm"},
            {"name": "Thư viện trường", "building": "Tòa B", "floor": "Tầng 1", "risk_level": 1, "description": "Khu vực tự học và đọc sách"},
            {"name": "Hội trường lớn", "building": "Tòa A", "floor": "Tầng 3", "risk_level": 3, "description": "Sức chứa 400 người"},
            {"name": "Nhà vệ sinh Nam Tòa A", "building": "Tòa A", "floor": "Tầng 1", "risk_level": 3, "description": "Khu vực ẩm ướt, dễ trơn trượt"},
            {"name": "Nhà vệ sinh Nữ Tòa A", "building": "Tòa A", "floor": "Tầng 1", "risk_level": 3, "description": "Khu vực ẩm ướt, dễ trơn trượt"},
            {"name": "Cầu thang Tòa B", "building": "Tòa B", "floor": "Tầng 1-3", "risk_level": 4, "description": "Khu vực lưu thông đông đúc, rủi ro ngã té cao"},
            {"name": "Căng tin trường", "building": "Khu Dịch vụ", "floor": "Tầng 1", "risk_level": 2, "description": "Khu vực ăn uống của học sinh"},
            {"name": "Sân vận động / Thể chất", "building": "Ngoài trời", "floor": "Mặt đất", "risk_level": 2, "description": "Khu tập thể dục thể thao"},
            {"name": "Trạm biến áp / Phòng điện", "building": "Tòa C", "floor": "Tầng trệt", "risk_level": 5, "description": "Khu vực điện cao thế đặc biệt nguy hiểm"}
        ]
        created_locations = []
        for loc in locations_data:
            existing = db.query(Location).filter(Location.name == loc["name"]).first()
            if not existing:
                existing = Location(**loc)
                db.add(existing)
                db.commit()
                db.refresh(existing)
            created_locations.append(existing)

        # 4. Loại sự cố (Incident Types)
        print("4. Tạo danh mục loại sự cố...")
        types_data = [
            {"name": "Quạt trần / Quạt tường hỏng", "default_severity": 2, "description": "Quạt không quay, kêu to hoặc rung lắc", "is_safety_critical": False},
            {"name": "Đèn chiếu sáng chập chờn / hỏng", "default_severity": 2, "description": "Bóng đèn cháy, không đủ sáng cho phòng học", "is_safety_critical": False},
            {"name": "Máy chiếu / Màn hình tivi không lên", "default_severity": 3, "description": "Ảnh hưởng trực tiếp đến bài giảng giáo viên", "is_safety_critical": False},
            {"name": "Vòi nước rò rỉ / Ống nước vỡ", "default_severity": 3, "description": "Gây ngập úng, trơn trượt và lãng phí nước", "is_safety_critical": False},
            {"name": "Tắc bồn cầu / Vệ sinh ô nhiễm", "default_severity": 4, "description": "Ảnh hưởng sinh hoạt và vệ sinh dịch tễ", "is_safety_critical": False},
            {"name": "Bàn ghế gãy / Lỏng ốc vít", "default_severity": 2, "description": "Gây khó khăn hoặc mất an toàn khi ngồi", "is_safety_critical": False},
            {"name": "Cửa chính / Cửa sổ kẹt hoặc hỏng khóa", "default_severity": 2, "description": "Gây mất an toàn tài sản hoặc thoát hiểm", "is_safety_critical": False},
            {"name": "Mạng Wifi / Internet mất kết nối", "default_severity": 2, "description": "Phòng tin học hoặc giáo viên không truy cập được mạng", "is_safety_critical": False},
            {"name": "Rác thải ùn ứ / Mùi hôi", "default_severity": 2, "description": "Chưa dọn thùng rác tại khu vực chung", "is_safety_critical": False},
            {"name": "Rò điện / Dây điện hở nguy hiểm", "default_severity": 5, "description": "NGUY HIỂM TÍNH MẠNG - Có dấu hiệu rò điện, tia lửa, khói", "is_safety_critical": True},
        ]
        created_types = []
        for t in types_data:
            existing = db.query(IncidentType).filter(IncidentType.name == t["name"]).first()
            if not existing:
                existing = IncidentType(**t)
                db.add(existing)
                db.commit()
                db.refresh(existing)
            created_types.append(existing)

        # 5. Dữ liệu sự cố mẫu (Incidents)
        print("5. Tạo 30 sự cố thực tế với các trạng thái...")
        # Danh sách tình huống đa dạng
        scenarios = [
            # Tình huống khẩn cấp (Safety critical)
            {
                "title": "Dây điện trần bị hở tại hành lang Tòa C",
                "desc": "Có tia lửa điện nhỏ khi chạm vào tường, rất nguy hiểm cho học sinh đi ngang qua",
                "type_idx": 9, "loc_idx": 6, "sev": 5, "people": 150, "impact": 4,
                "status": "in_progress", "hours_ago": 2, "assigned_staff_idx": 0
            },
            {
                "title": "Lan can cầu thang Tòa B bị lung lay có nguy cơ rơi",
                "desc": "Ốc vít giữ lan can tầng 2 bị tuột, học sinh tì vào có thể ngã",
                "type_idx": 6, "loc_idx": 11, "sev": 5, "people": 300, "impact": 3,
                "status": "assigned", "hours_ago": 5, "assigned_staff_idx": 1
            },
            {
                "title": "Mùi khét và bốc khói từ tủ điện phòng Tin học 1",
                "desc": "Aptomat nhảy liên tục và có mùi khét lẹt quanh tủ điện góc lớp",
                "type_idx": 9, "loc_idx": 3, "sev": 5, "people": 45, "impact": 5,
                "status": "reported", "hours_ago": 1, "assigned_staff_idx": None
            },
            # Sự cố cấp bách (Urgent)
            {
                "title": "Vỡ đường ống nước tầng 1 Tòa A gây ngập sàn",
                "desc": "Nước tràn lênh láng khắp sảnh chính, nền gạch rất trơn dễ trượt ngã",
                "type_idx": 3, "loc_idx": 0, "sev": 4, "people": 250, "impact": 4,
                "status": "in_progress", "hours_ago": 8, "assigned_staff_idx": 1
            },
            {
                "title": "Hỏng máy chiếu phòng 101 trong giờ ôn thi tốt nghiệp",
                "desc": "Máy chiếu kêu tít tít rồi tắt ngúm, giáo viên không thể chiếu đề cương ôn tập",
                "type_idx": 2, "loc_idx": 0, "sev": 3, "people": 42, "impact": 5,
                "status": "in_progress", "hours_ago": 26, "assigned_staff_idx": 2
            },
            {
                "title": "Tắc 3 bồn cầu liên tiếp tại nhà vệ sinh Nam Tòa A",
                "desc": "Nước ứ đọng bốc mùi nồng nặc lan sang các phòng học lân cận",
                "type_idx": 4, "loc_idx": 9, "sev": 4, "people": 200, "impact": 3,
                "status": "assigned", "hours_ago": 15, "assigned_staff_idx": 3
            },
            # Sự cố ưu tiên cao (High)
            {
                "title": "Mất mạng Internet toàn bộ phòng Tin học 2",
                "desc": "Học sinh không thể thực hành bài kiểm tra 1 tiết môn Tin học",
                "type_idx": 7, "loc_idx": 4, "sev": 3, "people": 45, "impact": 4,
                "status": "received", "hours_ago": 12, "assigned_staff_idx": None
            },
            {
                "title": "Cháy toàn bộ bóng đèn phòng học 201",
                "desc": "Trời mưa âm u, phòng học rất tối học sinh không đọc được bài giảng",
                "type_idx": 1, "loc_idx": 2, "sev": 3, "people": 40, "impact": 4,
                "status": "reported", "hours_ago": 18, "assigned_staff_idx": None
            },
            {
                "title": "Quạt trần giữa lớp 10A2 rung lắc mạnh và phát tiếng kêu to",
                "desc": "Quạt có cảm giác lỏng ty treo, học sinh ngồi dưới rất sợ hãi",
                "type_idx": 0, "loc_idx": 1, "sev": 4, "people": 42, "impact": 3,
                "status": "received", "hours_ago": 30, "assigned_staff_idx": None
            },
            # Các sự cố bình thường (Normal)
            {
                "title": "Hỏng ổ khóa cửa sổ góc cuối lớp 10A1",
                "desc": "Khi có gió to cửa đập mạnh, cần siết lại bản lề hoặc thay chốt",
                "type_idx": 6, "loc_idx": 0, "sev": 2, "people": 10, "impact": 1,
                "status": "reported", "hours_ago": 48, "assigned_staff_idx": None
            },
            {
                "title": "Bàn ghế tổ 3 lớp 10A2 bị lung lay gãy mối hàn",
                "desc": "Mặt bàn bị cập kênh học sinh viết rất khó khăn",
                "type_idx": 5, "loc_idx": 1, "sev": 2, "people": 4, "impact": 2,
                "status": "assigned", "hours_ago": 60, "assigned_staff_idx": 1
            },
            {
                "title": "Thùng rác ngoài sân bóng bị đổ tràn rác",
                "desc": "Cần nhân viên vệ sinh quét dọn và dựng lại thùng rác",
                "type_idx": 8, "loc_idx": 13, "sev": 1, "people": 30, "impact": 1,
                "status": "reported", "hours_ago": 70, "assigned_staff_idx": None
            },
            # Các sự cố ĐÃ HOÀN THÀNH / ĐÃ XÁC NHẬN (Resolved / Confirmed / Closed)
            {
                "title": "Thay vòi nước rửa tay bị rỉ ở nhà vệ sinh Nữ",
                "desc": "Vòi rửa tay bồn số 2 bị khóa không chặt nhỏ giọt liên tục",
                "type_idx": 3, "loc_idx": 10, "sev": 2, "people": 100, "impact": 2,
                "status": "confirmed", "hours_ago": 96, "assigned_staff_idx": 1,
                "resolved_hours_ago": 24, "res_notes": "Đã thay van vòi nước mới loại Inox 304, kiểm tra không rỉ nước."
            },
            {
                "title": "Sửa máy chiếu hội trường chuẩn bị cho lễ sơ kết",
                "desc": "Máy chiếu mờ màu đỏ và sọc ngang màn hình",
                "type_idx": 2, "loc_idx": 8, "sev": 4, "people": 350, "impact": 4,
                "status": "resolved", "hours_ago": 80, "assigned_staff_idx": 2,
                "resolved_hours_ago": 6, "res_notes": "Đã vệ sinh ống kính và cắm lại cáp HDMI tín hiệu nét rõ."
            },
            {
                "title": "Thay thế bóng đèn tuýp LED tại Thư viện",
                "desc": "Khu vực dãy bàn đọc sách phía đông bị cháy 2 bóng đèn",
                "type_idx": 1, "loc_idx": 7, "sev": 2, "people": 50, "impact": 2,
                "status": "closed", "hours_ago": 120, "assigned_staff_idx": 0,
                "resolved_hours_ago": 48, "res_notes": "Đã lắp mới 2 bóng LED Rạng Đông 18W."
            },
        ]

        # Bổ sung thêm sự cố cho đủ 30 bản ghi
        additional_titles = [
            ("Quạt treo tường phòng Hội trường kêu rè rè", 0, 8, 2, 80, 2),
            ("Đèn exit cầu thang Tòa A không sáng", 1, 11, 3, 200, 2),
            ("Mạng Wifi Thư viện chập chờn hay mất kết nối", 7, 7, 2, 60, 3),
            ("Gãy then cài cửa chính lớp 11A1", 6, 2, 2, 40, 2),
            ("Vòi xịt vệ sinh phòng Nam bị đứt dây", 3, 9, 3, 150, 2),
            ("Bàn giáo viên phòng 102 bị bong tróc mặt gỗ", 5, 1, 2, 40, 1),
            ("Chuột cắn đứt dây loa thông báo ngoài sân", 9, 13, 3, 500, 3),
            ("Bình nước uống tầng 2 Tòa B bị rỉ vòi", 3, 11, 2, 100, 2),
            ("Màn hình máy tính số 15 phòng Tin 1 bị sọc xanh", 2, 3, 2, 45, 3),
            ("Ghế xoay thư viện bị gãy bánh xe", 5, 7, 1, 1, 1),
            ("Ổ cắm điện góc tường phòng Hóa học bị lỏng chân", 9, 5, 4, 30, 4),
            ("Cửa kính phòng thực hành Vật lý bị nứt", 6, 6, 3, 40, 3),
            ("Khu vực rửa tay căng tin bị đọng nước", 3, 12, 2, 120, 1),
            ("Bóng đèn cầu thang Tòa B bị cháy", 1, 11, 3, 250, 2),
            ("Chốt cửa phòng vệ sinh Nữ bị kẹt", 6, 10, 3, 180, 2),
        ]

        for title, t_idx, l_idx, sev, people, impact in additional_titles:
            scenarios.append({
                "title": title,
                "desc": f"Mô tả sự cố ghi nhận tại trường: {title}. Cần khắc phục để đảm bảo an toàn và nề nếp sinh hoạt.",
                "type_idx": t_idx,
                "loc_idx": l_idx,
                "sev": sev,
                "people": people,
                "impact": impact,
                "status": random.choice(["reported", "received", "assigned", "in_progress", "resolved"]),
                "hours_ago": random.randint(3, 90),
                "assigned_staff_idx": random.choice([0, 1, 2, 3, 4])
            })

        count_created = 0
        for s in scenarios:
            reporter = random.choice(created_students)
            rep_time = datetime.utcnow() - timedelta(hours=s["hours_ago"])
            
            assigned_staff = None
            if s.get("assigned_staff_idx") is not None:
                assigned_staff = created_staff[s["assigned_staff_idx"]]

            res_notes = s.get("res_notes")
            res_time = None
            if s.get("resolved_hours_ago"):
                res_time = datetime.utcnow() - timedelta(hours=s["resolved_hours_ago"])
            elif s["status"] in ["resolved", "confirmed", "closed"]:
                res_time = rep_time + timedelta(hours=min(s["hours_ago"] // 2, 24))
                res_notes = res_notes or "Đã sửa chữa và kiểm tra hoạt động ổn định."

            incident = Incident(
                reporter_id=reporter.id,
                type_id=created_types[s["type_idx"]].id,
                location_id=created_locations[s["loc_idx"]].id,
                title=s["title"],
                description=s["desc"],
                severity=s["sev"],
                people_affected=s["people"],
                learning_impact=s["impact"],
                status=s["status"],
                assigned_to=assigned_staff.id if assigned_staff else None,
                reported_at=rep_time,
                received_at=rep_time + timedelta(minutes=15) if s["status"] != "reported" else None,
                assigned_at=rep_time + timedelta(minutes=30) if s["status"] in ["assigned", "in_progress", "resolved", "confirmed", "closed"] else None,
                resolved_at=res_time,
                confirmed_at=res_time + timedelta(hours=2) if s["status"] in ["confirmed", "closed"] else None,
                resolution_notes=res_notes,
                image_paths=json.dumps([]),
            )
            db.add(incident)
            db.flush()

            # Tính điểm ưu tiên
            recalculate_incident_priority(db, incident)

            # Lịch sử
            h1 = StatusHistory(
                incident_id=incident.id,
                changed_by=reporter.id,
                old_status=None,
                new_status="reported",
                notes="Học sinh báo cáo sự cố qua hệ thống",
                changed_at=rep_time
            )
            db.add(h1)

            if s["status"] != "reported":
                h2 = StatusHistory(
                    incident_id=incident.id,
                    changed_by=created_admins[0].id,
                    old_status="reported",
                    new_status="received",
                    notes="Nhà trường tiếp nhận sự cố",
                    changed_at=rep_time + timedelta(minutes=15)
                )
                db.add(h2)

            if s["status"] in ["assigned", "in_progress", "resolved", "confirmed", "closed"] and assigned_staff:
                h3 = StatusHistory(
                    incident_id=incident.id,
                    changed_by=created_admins[0].id,
                    old_status="received",
                    new_status="assigned",
                    notes=f"Phân công xử lý cho: {assigned_staff.full_name}",
                    changed_at=rep_time + timedelta(minutes=30)
                )
                db.add(h3)

            if s["status"] in ["in_progress", "resolved", "confirmed", "closed"]:
                h4 = StatusHistory(
                    incident_id=incident.id,
                    changed_by=assigned_staff.id if assigned_staff else created_admins[0].id,
                    old_status="assigned",
                    new_status="in_progress",
                    notes="Bắt đầu tiến hành kiểm tra và khắc phục",
                    changed_at=rep_time + timedelta(hours=1)
                )
                db.add(h4)

            if s["status"] in ["resolved", "confirmed", "closed"]:
                h5 = StatusHistory(
                    incident_id=incident.id,
                    changed_by=assigned_staff.id if assigned_staff else created_admins[0].id,
                    old_status="in_progress",
                    new_status="resolved",
                    notes=res_notes or "Đã khắc phục xong sự cố",
                    changed_at=res_time
                )
                db.add(h5)

            if s["status"] in ["confirmed", "closed"]:
                h6 = StatusHistory(
                    incident_id=incident.id,
                    changed_by=reporter.id,
                    old_status="resolved",
                    new_status="confirmed",
                    notes="Học sinh xác nhận sự cố đã được sửa chữa tốt",
                    changed_at=res_time + timedelta(hours=2)
                )
                db.add(h6)

            count_created += 1

        db.commit()
        print(f"Đã tạo thành công {count_created} sự cố mẫu!")
        print("=" * 60)
        print("Khởi tạo hoàn tất! Tài khoản đăng nhập mẫu:")
        print("1. Admin:      admin / admin123")
        print("2. Nhân viên:  nhanvien_dien / 123456")
        print("3. Học sinh:   hs01 / 123456")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"Lỗi khi seed dữ liệu: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
