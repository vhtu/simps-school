"""
Cấu hình ứng dụng - Quản lý các biến môi trường và thiết lập hệ thống.
"""

import os

# === Cấu hình cơ sở dữ liệu ===
# Sử dụng đường dẫn tuyệt đối cho SQLite để không phụ thuộc vào thư mục thực thi
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "simps.db").replace("\\", "/")

IS_VERCEL = bool(os.getenv("VERCEL"))

if IS_VERCEL and not os.getenv("DATABASE_URL"):
    # Trên Vercel serverless, thư mục duy nhất có quyền ghi là /tmp
    tmp_db = "/tmp/simps.db"
    if not os.path.exists(tmp_db) and os.path.exists(DB_PATH):
        import shutil
        try:
            shutil.copy2(DB_PATH, tmp_db)
        except Exception:
            pass
    DATABASE_URL = f"sqlite:///{tmp_db}"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# Tương thích với chuỗi kết nối của Supabase/Heroku (postgres:// -> postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# === Cấu hình JWT (JSON Web Token) ===
SECRET_KEY = os.getenv("SECRET_KEY", "simps-khkt-2024-secret-key-school-project")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Token hết hạn sau 24 giờ

# === Cấu hình upload file ===
if IS_VERCEL:
    UPLOAD_DIR = "/tmp/uploads"
else:
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# === Cấu hình trọng số mặc định cho thuật toán ưu tiên ===
DEFAULT_WEIGHTS = {
    "w1": 0.30,  # Trọng số mức độ nghiêm trọng (Severity)
    "w2": 0.20,  # Trọng số số người bị ảnh hưởng (Impact)
    "w3": 0.20,  # Trọng số mức độ rủi ro khu vực (Risk)
    "w4": 0.15,  # Trọng số thời gian chờ (Time)
    "w5": 0.15,  # Trọng số ảnh hưởng học tập (Education)
}

# === Ngưỡng phân loại mức ưu tiên ===
PRIORITY_THRESHOLDS = {
    "urgent": 3.5,   # Điểm >= 3.5 → Khẩn cấp
    "high": 2.5,     # Điểm >= 2.5 → Cao
    # Điểm < 2.5 → Bình thường
}

# === Cấu hình CORS ===
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "*",  # Cho phép tất cả trong môi trường phát triển
]
