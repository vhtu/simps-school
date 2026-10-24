"""
Service Thông báo Đẩy Ngoại vi - Gửi cảnh báo tức thì qua Zalo Webhook và Telegram Bot
Dành cho các sự cố Khẩn cấp (Safety Override P=999) hoặc Cấp bách (P >= 3.5).
"""

import json
import logging
import urllib.request
import urllib.error
from sqlalchemy.orm import Session
from app.models.survey import SystemConfig

logger = logging.getLogger("simps.alert")


def get_alert_configs(db: Session) -> dict:
    """Lấy cấu hình webhook Zalo & Telegram từ SystemConfig"""
    configs = {
        "zalo_webhook_url": "",
        "telegram_bot_token": "",
        "telegram_chat_id": "",
        "alert_enabled": "true",
        "alert_min_priority": "urgent"  # "emergency" hoặc "urgent"
    }
    rows = db.query(SystemConfig).filter(SystemConfig.key.in_(configs.keys())).all()
    for r in rows:
        configs[r.key] = r.value
    return configs


def save_alert_configs(db: Session, data: dict):
    """Lưu cấu hình alert webhook vào SystemConfig"""
    for key, value in data.items():
        if value is None:
            value = ""
        cfg = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if cfg:
            cfg.value = str(value)
        else:
            cfg = SystemConfig(key=key, value=str(value))
            db.add(cfg)
    db.commit()


def send_external_alert(db: Session, incident, location_name: str, type_name: str, reporter_name: str = "Học sinh"):
    """
    Gửi tin nhắn cảnh báo ra ngoài (Zalo Webhook / Telegram Bot)
    khi có sự cố đáp ứng ngưỡng ưu tiên (P >= 3.5 hoặc P = 999).
    """
    configs = get_alert_configs(db)
    if configs.get("alert_enabled") != "true":
        return {"sent": False, "reason": "Cảnh báo ngoại vi đang tắt"}

    min_p = configs.get("alert_min_priority", "urgent")
    # Kiểm tra mức ưu tiên
    if min_p == "emergency" and incident.priority_level != "emergency":
        return {"sent": False, "reason": "Chưa đạt ngưỡng Khẩn cấp"}

    # Tạo nội dung tin nhắn
    p_badge = "🚨 [KHẨN CẤP - P=999]" if incident.priority_level == "emergency" else "⚠️ [CẤP BÁCH]"
    message_text = (
        f"{p_badge} CẢNH BÁO SỰ CỐ CƠ SỞ VẬT CHẤT\n"
        f"🏛️ Trường THPT Ô Môn - Hệ thống SIMPS\n"
        f"-----------------------------------------\n"
        f"📌 Sự cố: {incident.title}\n"
        f"📍 Khu vực: {location_name}\n"
        f"🏷️ Danh mục: {type_name}\n"
        f"⭐ Điểm ưu tiên P: {incident.priority_score}\n"
        f"👤 Người báo: {reporter_name}\n"
        f"📝 Mô tả: {incident.description or 'Không có ghi chú'}\n"
        f"-----------------------------------------\n"
        f"👉 Tổ Kỹ thuật CSVC vui lòng tiếp nhận xử lý ngay!"
    )

    results = {}

    # 1. Gửi qua Telegram Bot (nếu cấu hình)
    bot_token = configs.get("telegram_bot_token", "").strip()
    chat_id = configs.get("telegram_chat_id", "").strip()
    if bot_token and chat_id:
        try:
            tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = json.dumps({
                "chat_id": chat_id,
                "text": message_text,
                "parse_mode": "HTML"
            }).encode("utf-8")
            req = urllib.request.Request(tg_url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                results["telegram"] = "success"
        except Exception as e:
            logger.error(f"Lỗi gửi Telegram: {e}")
            results["telegram"] = f"error: {str(e)}"

    # 2. Gửi qua Zalo Webhook / Generic Webhook (nếu cấu hình)
    zalo_url = configs.get("zalo_webhook_url", "").strip()
    if zalo_url:
        try:
            payload = json.dumps({
                "event_name": "incident_alert",
                "incident_id": incident.id,
                "priority": incident.priority_level,
                "priority_score": incident.priority_score,
                "title": incident.title,
                "location": location_name,
                "message": message_text
            }).encode("utf-8")
            req = urllib.request.Request(zalo_url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                results["zalo"] = "success"
        except Exception as e:
            logger.error(f"Lỗi gửi Zalo Webhook: {e}")
            results["zalo"] = f"error: {str(e)}"

    return results


def test_alert_channel(channel: str, target: str, token: str = "") -> dict:
    """Gửi tin nhắn test kiểm tra kênh liên lạc"""
    test_msg = (
        "🔔 [TEST SIMPS] Kiểm tra kết nối Thông Báo Tức Thì thành công!\n"
        "🏛️ Hệ thống Quản lý và Ưu tiên Sự cố - Trường THPT Ô Môn\n"
        "Đề tài KHKT 2026 • Kênh thông báo hoạt động sẵn sàng tiếp nhận sự cố khẩn cấp."
    )
    if channel == "telegram":
        if not token or not target:
            raise ValueError("Cần cung cấp Bot Token và Chat ID")
        tg_url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = json.dumps({
            "chat_id": target,
            "text": test_msg
        }).encode("utf-8")
        req = urllib.request.Request(tg_url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            return {"status": "success", "response": resp.read().decode("utf-8")}
    elif channel == "zalo":
        if not target:
            raise ValueError("Cần cung cấp URL Webhook Zalo")
        payload = json.dumps({
            "event_name": "test_alert",
            "message": test_msg
        }).encode("utf-8")
        req = urllib.request.Request(target, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            return {"status": "success", "response": resp.read().decode("utf-8")}
    else:
        raise ValueError("Kênh không hợp lệ")
