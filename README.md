# Hệ Thống Quản Lý Và Ưu Tiên Xử Lý Sự Cố Trong Trường Học (SIMPS)
> **School Incident Management and Prioritization System Based on Impact and Urgency**

### 🎓 THÔNG TIN ĐỀ TÀI KHOA HỌC KỸ THUẬT (KHKT 2026)
* **Học sinh thực hiện**: **Lê Quốc Khánh** và **Hồ Anh Khoa**
* **Giáo viên hướng dẫn (GVHD)**: **Phan Thuý Quỳnh**
* **Đơn vị dự thi**: **Trường THPT Ô Môn, TP Cần Thơ**
* **Lĩnh vực nghiên cứu**: Hệ thống nhúng & Phần mềm hệ thống (System Software)

---

## 📌 Điểm Cốt Lõi Của Đề Tài (Tính Mới & Khoa Học)

1. **Không sử dụng AI/Học máy theo trào lưu**: Thay vào đó, đề tài xây dựng một **thuật toán xếp hạng ưu tiên đa tiêu chí dựa trên luật và trọng số (Weighted Rule-Based Scoring)** minh bạch, có thể giải thích và kiểm chứng:
   $$\mathbf{P = w_1 \times S + w_2 \times I + w_3 \times R + w_4 \times T + w_5 \times E}$$
   - $S$ (*Severity*): Mức độ nghiêm trọng của hư hỏng (1–5)
   - $I$ (*Impact*): Số lượng học sinh/giáo viên bị ảnh hưởng (Chuẩn hóa 1–5)
   - $R$ (*Risk*): Mức độ rủi ro an toàn của khu vực phát sinh (1–5)
   - $T$ (*Time*): Thời gian sự cố đã tồn tại chờ xử lý (Chuẩn hóa 1–5)
   - $E$ (*Education*): Mức độ gián đoạn đến hoạt động dạy và học (1–5)

2. **Quy tắc An Toàn Đặc Biệt (Safety Override)**:
   Nếu sự cố xảy ra tại khu vực nguy hiểm ($R \ge 5$) hoặc thuộc danh mục rủi ro tai nạn (rò điện, lan can lung lay, hóa chất...), hệ thống tự động đưa lên mức **Khẩn Cấp (Emergency)** với điểm tối đa ($P = 999$), không để điểm tổng quyết định sự an toàn.

3. **Xác định trọng số bằng khảo sát thực nghiệm**: Bộ trọng số $\{w_1, w_2, w_3, w_4, w_5\}$ được khảo sát thực tế từ giáo viên, nhân viên cơ sở vật chất và học sinh thay vì lựa chọn cảm tính.

4. **Thực nghiệm đối chứng**: Chứng minh định lượng sự vượt trội của phương pháp SIMPS Priority so với phương pháp FIFO (xử lý tuần tự theo thời gian báo cáo) trong việc giảm thời gian chờ của các sự cố nguy cấp.

---

## 🏛️ Cấu Trúc Dự Án

```
D:\KHKT\
├── De_xuat_de_tai_He_thong_quan_ly_va_uu_tien_xu_ly_su_co_truong_hoc.pdf # Đề cương đề tài
├── backend/                              # Máy chủ API (Python + FastAPI)
│   ├── app/
│   │   ├── config.py                     # Cấu hình JWT, CSDL, Trọng số mặc định
│   │   ├── database.py                   # Kết nối SQLAlchemy ORM
│   │   ├── models/                       # Entity: User, Incident, Location, Type...
│   │   ├── schemas/                      # Pydantic Schemas xác thực dữ liệu vào/ra
│   │   ├── services/
│   │   │   ├── priority_service.py       # ⭐ THUẬT TOÁN TÍNH ĐIỂM ƯU TIÊN
│   │   │   ├── incident_service.py       # Nghiệp vụ quản lý sự cố
│   │   │   ├── stats_service.py          # Thống kê, tổng hợp số liệu
│   │   │   └── auth_service.py           # Xác thực người dùng & mã hóa bcrypt
│   │   ├── routes/                       # RESTful API Endpoints
│   │   └── middleware/                   # JWT Auth & Phân quyền Role-Based
│   ├── seeds/
│   │   └── seed_data.py                  # Khởi tạo 30 sự cố thực tế và dữ liệu mẫu
│   ├── tests/
│   │   └── test_priority_algorithm.py    # Unit tests & Thí nghiệm mô phỏng thuật toán
│   ├── requirements.txt                  # Danh mục thư viện Python
│   └── README.md
│
├── frontend/                             # Giao diện người dùng (Vanilla HTML/CSS/JS)
│   ├── index.html                        # Trang Đăng nhập hệ thống
│   ├── pages/
│   │   ├── student.html                  # Cổng Học Sinh (Báo cáo & Theo dõi & Xác nhận)
│   │   ├── staff.html                    # Cổng Kỹ Thuật / CSVC (Hàng đợi ưu tiên & Xử lý)
│   │   └── admin.html                    # Cổng Quản Trị (Biểu đồ thống kê & Chỉnh trọng số)
│   ├── css/                              # Theme màu, components, responsive layout
│   └── js/                               # API Client, Auth, Canvas Charts, Toasts, Modals
│
└── README.md                             # Tài liệu tổng quan dự án
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Thử Hệ Thống

### 1. Khởi động Backend Server
Mở terminal tại thư mục dự án và chạy:
```powershell
cd D:\KHKT\backend
gõ lệnh
python -m uvicorn app.main:app --reload --port 8000
```
- API Docs tự động (Swagger UI): **http://localhost:8000/docs**
- Health Check: **http://localhost:8000/api/health**

### 2. Mở Giao Diện Người Dùng (Frontend)
Chỉ cần mở trực tiếp file `D:\KHKT\frontend\index.html` bằng trình duyệt web (Chrome, Edge, Firefox) hoặc dùng Live Server:
- `http://localhost:5500/frontend/index.html` hoặc mở trực tiếp `file:///D:/KHKT/frontend/index.html`.

### 3. Danh Sách Tài Khoản Thử Nghiệm

| Phân hệ | Tài khoản | Mật khẩu | Chức năng chính |
|---|---|---|---|
| **Ban Quản Lý (Admin)** | `admin` | `admin123` | Xem biểu đồ thống kê, điều chỉnh trọng số thuật toán $w_1 \dots w_5$, quản lý địa điểm, loại sự cố, người dùng |
| **Nhân Viên CSVC (Staff)** | `nhanvien_dien` | `123456` | Tiếp nhận và xử lý sự cố sắp xếp theo thứ tự ưu tiên $P$, nhận cảnh báo đỏ cho sự cố an toàn |
| **Học Sinh (Student)** | `hs01` | `123456` | Báo cáo sự cố mới kèm ảnh, theo dõi tiến trình xử lý, bấm nút Xác nhận khi sự cố đã được sửa tốt |

---

## 🧪 Chạy Kiểm Thử Thuật Toán (Unit Tests)
```powershell
python D:\KHKT\backend\tests\test_priority_algorithm.py
```
Kết quả kiểm tra tự động độ chính xác của chuẩn hóa thời gian, chuẩn hóa số người ảnh hưởng và thí nghiệm đối chứng FIFO vs SIMPS.


## 🧪 Truy cập database
cd D:\KHKT\
gõ lệnh
python -c "import sys; from sqlite_web.sqlite_web import main; sys.argv=['sqlite_web', r'D:\KHKT\backend\simps.db', '--port', '8080', '-H', '0.0.0.0', '-x']; main()"