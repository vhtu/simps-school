"""
Điểm khởi động chính của ứng dụng SIMPS (FastAPI).
School Incident Management and Prioritization System.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
import app.models  # Đảm bảo tất cả models được import để tạo bảng
from app.config import CORS_ORIGINS, UPLOAD_DIR
from app.routes import (
    auth_router,
    incidents_router,
    stats_router,
    config_router,
    users_router,
    notifications_router,
)
from app.utils.helpers import api_response

# Tạo toàn bộ các bảng trong CSDL nếu chưa tồn tại (chỉ cần chạy trên Local SQLite)
if not os.getenv("VERCEL") and "sqlite" in str(engine.url):
    Base.metadata.create_all(bind=engine)

# Khởi tạo thư mục upload nếu chưa có
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Khởi tạo FastAPI app
app = FastAPI(
    title="SIMPS - Hệ thống Quản lý và Ưu tiên Xử lý Sự cố Trường học",
    description="Đề tài Nghiên cứu Khoa học Kỹ thuật (KHKT 2026) - Trường THPT Ô Môn, TP Cần Thơ. Học sinh thực hiện: Nguyễn Quốc Khánh | Giáo viên hướng dẫn (GVHD): Phan Thuý Quỳnh.",
    version="1.0.0",
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phục vụ thư mục hình ảnh tĩnh
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Gắn các router API với tiền tố /api
app.include_router(auth_router, prefix="/api")
app.include_router(incidents_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")


@app.get("/api/health", summary="Kiểm tra trạng thái hệ thống")
def health_check():
    return api_response(
        success=True,
        data={"status": "healthy"},
        message="Hệ thống SIMPS đang hoạt động bình thường"
    )


@app.get("/api/debug-db", summary="Kiểm tra kết nối CSDL và chẩn đoán lỗi")
def debug_db():
    import traceback
    try:
        from app.config import DATABASE_URL, IS_VERCEL
        from app.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
        return {
            "success": True,
            "is_vercel": IS_VERCEL,
            "db_type": str(engine.url).split(":")[0],
            "db_host": engine.url.host,
            "select_1": result[0] if result else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


# Phục vụ toàn bộ giao diện Frontend (Single Unified Port 8000)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend"))
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

