# SIMPS - School Incident Management and Prioritization System (Backend)

Hệ thống phần mềm quản lý và ưu tiên xử lý sự cố trong trường học dựa trên mức độ ảnh hưởng và mức độ khẩn cấp.

## Công nghệ sử dụng
- **Ngôn ngữ**: Python 3.11+
- **Framework**: FastAPI
- **Cơ sở dữ liệu**: SQLite (có thể chuyển sang MySQL cấu hình trong `app/config.py`)
- **ORM**: SQLAlchemy 2.0
- **Xác thực**: JWT (JSON Web Token) + bcrypt
- **Thuật toán ưu tiên**: Weighted Rule-Based Multi-Factor Scoring with Safety Override

## Hướng dẫn cài đặt & Khởi chạy

### 1. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 2. Khởi tạo dữ liệu mẫu
```bash
python seeds/seed_data.py
```

### 3. Chạy Server
```bash
uvicorn app.main:app --reload --port 8000
```
- API Docs (Swagger UI): http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

## Tài khoản mẫu
| Vai trò | Tên đăng nhập | Mật khẩu | Chức vụ |
|---|---|---|---|
| Admin | `admin` | `admin123` | Quản trị viên hệ thống |
| Nhân viên | `nhanvien_dien` | `123456` | Kỹ thuật điện |
| Học sinh | `hs01` | `123456` | Học sinh lớp 10A2 |
