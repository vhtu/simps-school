# TÀI LIỆU HƯỚNG DẪN SỬ DỤNG HỆ THỐNG SIMPS
> **Đề tài: Nghiên cứu, phát triển hệ thống tiếp nhận và tự động xếp hạng ưu tiên xử lý sự cố cơ sở vật chất trường học dựa trên thuật toán đa tiêu chí (SIMPS)**  
> **School Incident Management and Prioritization System**  
> *Đề tài Nghiên cứu Khoa học Kỹ thuật (KHKT 2026)*

---

### 🎓 THÔNG TIN ĐỀ TÀI
* **Học sinh thực hiện**: **Lê Quốc Khánh** và **Hồ Anh Khoa**
* **Giáo viên hướng dẫn (GVHD)**: **Phan Thuý Quỳnh**
* **Đơn vị dự thi**: **Trường THPT Ô Môn, TP Cần Thơ**
* **Địa chỉ truy cập trực tuyến**: [https://simps-school.vercel.app](https://simps-school.vercel.app)

---

## MỤC LỤC
1. [GIỚI THIỆU TỔNG QUAN](#1-giới-thiệu-tổng-quan)
2. [HƯỚNG DẪN DÀNH CHO HỌC SINH (HỌC ĐƯỜNG)](#2-hướng-dẫn-dành-cho-học-sinh)
   - 2.1. Đăng nhập hệ thống
   - 2.2. Báo cáo sự cố tức thì qua Tem Mã QR (0-Touch)
   - 2.3. Tạo báo cáo thủ công qua phiếu tiếp nhận
   - 2.4. Theo dõi tiến trình & Nghiệm thu xác nhận
   - 2.5. Đổi mật khẩu cá nhân
3. [HƯỚNG DẪN DÀNH CHO TỔ KỸ THUẬT & CSVC (STAFF)](#3-hướng-dẫn-dành-cho-tổ-kỹ-thuật--csvc)
   - 3.1. Hàng đợi ưu tiên tự động (Priority Queue)
   - 3.2. Cảnh báo an toàn đặc biệt (Safety Override)
   - 3.3. Quy trình tiếp nhận, xử lý và hoàn tất sự cố
   - 3.4. Nhận thông báo tức thì qua Telegram / Zalo
4. [HƯỚNG DẪN DÀNH CHO QUẢN TRỊ VIÊN & BAN GIÁM HIỆU (ADMIN)](#4-hướng-dẫn-dành-cho-quản-trị-viên--ban-giám-hiệu)
   - 4.1. Bảng điều khiển KPI & Biểu đồ phân tích
   - 4.2. Khuyến nghị bảo trì phòng ngừa (Predictive Maintenance)
   - 4.3. Quản lý danh mục sự cố, xóa & điều phối
   - 4.4. Cấu hình trọng số AHP & Bộ giả lập P
   - 4.5. Quản lý Địa điểm, Mức rủi ro R & In hàng loạt tem QR
   - 4.6. Quản lý Loại sự cố & Quy tắc an toàn
   - 4.7. Quản lý Tài khoản người dùng (Sửa / Đổi mật khẩu / Xóa)
   - 4.8. Cấu hình Bắn thông báo Zalo & Telegram Webhook
5. [CÁC TÀI KHOẢN MẪU DÙNG THỬ (DEMO)](#5-các-tài-khoản-mẫu-dùng-thử)

---

## 1. GIỚI THIỆU TỔNG QUAN
SIMPS là hệ thống phần mềm thông minh ứng dụng giải thuật xếp hạng đa tiêu chí tuyến tính kết hợp quy tắc ghi đè an toàn (Safety Override):
$$\mathbf{P = w_1S + w_2I + w_3R + w_4T + w_5E}$$
- **$S$ (Nghiêm trọng)**: Trọng số $0.30$
- **$I$ (Số người ảnh hưởng)**: Trọng số $0.20$
- **$R$ (Rủi ro vị trí)**: Trọng số $0.20$
- **$T$ (Thời gian chờ)**: Trọng số $0.15$
- **$E$ (Tác động học tập)**: Trọng số $0.15$

Bộ trọng số được xác lập dựa trên phương pháp toán học **AHP (Thomas L. Saaty)** với tỉ số nhất quán $CR = 0.042 < 0.10$, đảm bảo tính logic khoa học tuyệt đối.

---

## 2. HƯỚNG DẪN DÀNH CHO HỌC SINH

### 2.1. Đăng nhập hệ thống
1. Truy cập [https://simps-school.vercel.app](https://simps-school.vercel.app).
2. Nhập **Tên đăng nhập** (ví dụ: `hs01`) và **Mật khẩu** (`123456`). *(Có thể bấm vào nút mẫu "🎓 Học Sinh" để tự động điền)*.
3. Bấm **Đăng Nhập Ngay**. Hệ thống sẽ tự động chuyển tới giao diện Cổng Học Sinh.

### 2.2. Báo cáo sự cố tức thì qua Tem Mã QR (0-Touch Quick Report)
Khi phát hiện hư hỏng ngay tại lớp học (quạt hỏng, đèn chớp, vòi nước rò rỉ, bóng đèn đứt...):
1. Mở ứng dụng **Zalo** hoặc **Camera điện thoại**, hướng ống kính vào **Tem QR dán tại cửa phòng học**.
2. Nhấp vào liên kết hiện lên trên màn hình.
3. Hệ thống sẽ **tự động định vị phòng học**, khóa hệ số rủi ro $R$, và chuyển ngay đến tab Báo cáo sự cố kèm thông báo xanh:  
   *`"QUÉT QR THÀNH CÔNG: ĐÃ TỰ ĐỘNG ĐỊNH VỊ PHÒNG HỌC!"`*
4. Học sinh chỉ cần:
   - Nhập tiêu đề sự cố (ví dụ: *"Quạt số 2 kêu rè rè"*).
   - Chọn loại thiết bị và mức độ nghiêm trọng (1 đến 5 sao).
   - Bấm **🚀 Gửi Báo Cáo Đến Ban CSVC** (thời gian thao tác chưa tới 20 giây).

### 2.3. Tạo báo cáo thủ công qua phiếu tiếp nhận
1. Trên thanh điều hướng, chọn tab **✏️ Tạo Báo Cáo Mới**.
2. Điền các trường thông tin:
   - **Tiêu đề**: Ngắn gọn, rõ ý.
   - **Loại hư hỏng**: Chọn trong danh mục (Điện, Nước, Quạt, Máy chiếu...).
   - **Vị trí phát hiện**: Chọn phòng học/khu vực tương ứng.
   - **Mức độ nghiêm trọng (S)**: Bấm chọn trực quan từ 1 (Rất nhẹ) đến 5 (Cực kỳ nghiêm trọng).
   - **Số người bị ảnh hưởng**: Ước lượng sĩ số lớp hoặc số người dùng.
   - **Ảnh hiện trường**: Kéo thả ảnh chụp minh chứng để kỹ thuật viên dễ dàng chuẩn bị đồ nghề thay thế.
3. Bấm **Gửi Báo Cáo**.

### 2.4. Theo dõi tiến trình & Nghiệm thu xác nhận
1. Chọn tab **📋 Báo Cáo Của Tôi**.
2. Danh sách hiển thị trực quan các sự cố bạn đã gửi kèm điểm ưu tiên $P$, màu sắc mức độ và thời gian báo cáo.
3. **Nghiệm thu đóng sự cố**: Khi kỹ thuật viên sửa xong, sự cố sẽ chuyển sang trạng thái *"Đã khắc phục"*. Lúc này, học sinh kiểm tra thực tế xem thiết bị đã dùng tốt chưa, sau đó bấm nút **`✅ Xác nhận`** để chính thức đóng hồ sơ sự cố.

### 2.5. Đổi mật khẩu cá nhân
1. Bấm vào nút **`🔑 Đổi MK`** trên góc phải thanh điều hướng.
2. Nhập mật khẩu hiện tại và mật khẩu mới (tối thiểu 4 ký tự).
3. Bấm **Xác Nhận Đổi**.

---

## 3. HƯỚNG DẪN DÀNH CHO TỔ KỸ THUẬT & CSVC (STAFF)

### 3.1. Hàng đợi ưu tiên tự động (Priority Queue)
- Truy cập bằng tài khoản Kỹ thuật (ví dụ: `nhanvien_dien` / `123456`).
- Màn hình chính là **Hàng đợi ưu tiên (Core Queue)**:
  - Các sự cố được thuật toán SIMPS tự động sắp xếp theo điểm $P$ giảm dần.
  - Sự cố có điểm $P$ cao hơn sẽ đứng ở trên đầu danh sách, giúp kỹ thuật viên biết chính xác sự cố nào cần xử lý trước, không phụ thuộc vào cảm tính.

### 3.2. Cảnh báo an toàn đặc biệt (Safety Override)
- Khi có sự cố chập điện, cháy nổ, bình chữa cháy hỏng, hoặc rủi ro tại trạm điện/phòng hóa nghiệm ($P = 999$):
  - Banner cảnh báo nhấp nháy màu đỏ **🚨 SAFETY OVERRIDE ACTIVE** sẽ xuất hiện ngay đầu trang kèm còi báo động.
  - Sự cố được ưu tiên tuyệt đối, yêu cầu kỹ thuật viên có mặt tại hiện trường trong vòng dưới 15 phút.

### 3.3. Quy trình tiếp nhận, xử lý và hoàn tất
1. Tại dòng sự cố, bấm nút **`⚙️ Thao tác`**.
2. Popup điều phối xuất hiện, kỹ thuật viên có thể:
   - Bấm **"Nhận xử lý sự cố này"** để ghi tên mình vào phiếu.
   - Chuyển trạng thái sang: **Đang xử lý** (khi bắt đầu sửa chữa) ➡️ **Đã khắc phục** (khi hoàn thành).
   - Nhập **Ghi chú giải pháp**: Ghi lại linh kiện đã thay (ví dụ: *"Đã thay tụ quạt 2.5uF mới"*).
3. Bấm **Lưu Thay Đổi**. Hệ thống tự động bắn thông báo chuông đến học sinh để kiểm tra nghiệm thu.

### 3.4. Nhận thông báo tức thì qua Telegram / Zalo
- Kỹ thuật viên tham gia vào nhóm Telegram CSVC của trường sẽ nhận được thông báo reo chuông ngay trên điện thoại khi có sự cố khẩn cấp mà không cần mở trình duyệt web.

---

## 4. HƯỚNG DẪN DÀNH CHO QUẢN TRỊ VIÊN & BAN GIÁM HIỆU (ADMIN)

### 4.1. Bảng điều khiển KPI & Biểu đồ phân tích
1. Đăng nhập bằng tài khoản Quản trị (`admin` / `admin123`).
2. Chọn mục **`📊 Bảng Điều Khiển & Biểu Đồ`**:
   - Theo dõi 4 chỉ số KPI: Tổng số sự cố, Sự cố khẩn cấp, Sự cố quá hạn (> 72h), Sự cố đã khắc phục.
   - **5 biểu đồ Canvas Retina tương tác**:
     1. Phân bổ theo danh mục hư hỏng.
     2. Điểm nóng thường xuyên phát sinh hỏng hóc.
     3. Tần suất phát sinh theo chuỗi thời gian (tháng).
     4. Thời gian giải quyết trung bình theo từng mức ưu tiên (Giờ).
     5. Hiệu suất xử lý công việc của từng kỹ thuật viên.

### 4.2. Khuyến nghị bảo trì phòng ngừa (Predictive Maintenance Insights)
- Thẻ thông minh tự động quét tần suất hỏng hóc lặp lại:
  - Kiến nghị **ĐẠI TU TOÀN DIỆN**: Khi một phòng học có từ 3 sự cố trở lên trước năm học mới.
  - Kiến nghị **THAY THẾ THIẾT BỊ MỚI**: Khi chi phí sửa chữa lũy kế vượt quá 50% nguyên giá thiết bị.

### 4.3. Quản lý danh mục sự cố, xóa & điều phối
1. Chọn mục **`📋 Toàn Bộ Sự Cố Học Đường`**.
2. Tìm kiếm theo từ khóa, lọc theo mức độ ưu tiên, trạng thái, tòa nhà hoặc kỹ thuật viên phụ trách.
3. Bấm nút **`📥 Xuất File Excel / CSV`** để tải toàn bộ dữ liệu sự cố phục vụ báo cáo.
4. Bấm **`Chi tiết`** để phân công nhân viên, đổi trạng thái hoặc **`🗑️ Xóa Sự Cố Này`** (khi gặp báo cáo rác hoặc sai sót).

### 4.4. Cấu hình trọng số AHP & Bộ giả lập P
1. Chọn mục **`⚙️ Trọng Số & Bộ Giả Lập P`**.
2. Có thể điều chỉnh thanh trượt của từng tiêu chí $w_1, w_2, w_3, w_4, w_5$.
3. Kéo thử các giá trị giả định trong **Bộ Giả Lập Kiểm Chứng** để xem trước kết quả điểm $P$.
4. Tham khảo bảng **Ma trận so sánh cặp AHP (Thomas L. Saaty)** chứng minh độ nhất quán toán học $CR = 0.042 < 0.10$.
5. Bấm **💾 Áp Dụng Trọng Số Mới & Tính Lại Toàn Bộ CSDL Trường Học**.

### 4.5. Quản lý Địa điểm, Mức rủi ro R & In hàng loạt tem QR
1. Chọn mục **`🏫 Địa Điểm & Mức Rủi Ro`**:
   - Bấm **`➕ Thêm Địa Điểm`**: Thêm phòng học, tòa nhà, tầng lầu và gán hệ số rủi ro an toàn $R \in [1, 5]$.
   - Bấm **`Sửa`**: Cập nhật thông tin phòng học và điều chỉnh mức rủi ro $R$.
   - Bấm **`Xóa`**: Xóa khu vực (có cơ chế bảo vệ nếu đang có sự cố ràng buộc).
   - Bấm **`📱 Mã QR Tem`**: Xem mã QR riêng của từng phòng học, tải ảnh PNG hoặc in tem đơn lẻ.
   - Bấm nút **`🖨️ In Hàng Loạt Tem QR Phòng Học`**: Tạo bản in khổ giấy A4 chứa toàn bộ tem dán cửa lớp cho cả trường chỉ trong 1 lần nhấn chuột.

### 4.6. Quản lý Loại sự cố & Quy tắc an toàn
1. Chọn mục **`🏷️ Loại Sự Cố & An Toàn`**:
   - Bấm **`➕ Thêm Loại Sự Cố`**: Nhập tên danh mục, mức nghiêm trọng mặc định $S$.
   - Tích chọn checkbox: **Kích hoạt quy tắc An Toàn Đặc Biệt (Safety Override)** đối với các loại sự cố nguy hiểm đến tính mạng (Điện, Cháy nổ...). Khi được kích hoạt, hệ thống sẽ tự động gán $P = 999$ cho mọi sự cố thuộc loại này.
   - Hỗ trợ đầy đủ chức năng **Sửa** và **Xóa** loại sự cố.

### 4.7. Quản lý Tài khoản người dùng
1. Chọn mục **`👥 Tài Khoản Người Dùng`**:
   - Bấm **`➕ Thêm Người Dùng`**: Cấp tài khoản mới cho học sinh, nhân viên hoặc quản trị viên.
   - Bấm **`Sửa`**: Thay đổi thông tin cá nhân, vai trò, lớp học hoặc email.
   - Bấm **`Đổi MK`**: Đặt lại mật khẩu mới cho bất kỳ người dùng nào khi học sinh quên mật khẩu.
   - Bấm **`Xóa`**: Vô hiệu hóa tài khoản khi học sinh đã ra trường.

### 4.8. Cấu hình Bắn thông báo Zalo & Telegram Webhook
1. Chọn mục **`📲 Bắn Thông Báo Zalo & Telegram`**:
   - Chọn trạng thái: **Bật** thông báo.
   - Chọn ngưỡng kích hoạt: Cấp bách ($P \ge 3.5$) hoặc chỉ gửi Khẩn cấp ($P = 999$).
   - Dán **Telegram Bot Token** và **Telegram Chat ID** (hoặc Zalo Webhook URL).
   - Bấm **`🔔 Gửi thử tin nhắn`** để kiểm tra kết nối tới điện thoại.
   - Bấm **`💾 Lưu Cấu Hình Bắn Thông Báo Ngoại Vi`**.

---

## 5. CÁC TÀI KHOẢN MẪU DÙNG THỬ (DEMO)

| Vai trò | Tên đăng nhập | Mật khẩu mặc định | Mục đích trải nghiệm |
| :--- | :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin` | `admin123` | Bảng điều khiển phân tích, cấu hình AHP, quản lý tài khoản, in mã QR, cấu hình webhook Zalo/Telegram |
| **Kỹ thuật Điện (Staff)** | `nhanvien_dien` | `123456` | Trải nghiệm Hàng đợi ưu tiên (Core Queue), cảnh báo Safety Override, cập nhật trạng thái sửa chữa |
| **Kỹ thuật CSVC (Staff)** | `nhanvien_nuoc` | `123456` | Xử lý các sự cố về đường ống nước, bồn rửa, vệ sinh trường học |
| **Học sinh (Student)** | `hs01` (đến `hs20`) | `123456` | Quét mã QR phòng học báo sự cố mới, theo dõi tiến trình, nghiệm thu xác nhận sự cố |

---
*Tài liệu hướng dẫn sử dụng Hệ thống SIMPS • Bản quyền đề tài KHKT 2026 - Trường THPT Ô Môn, TP Cần Thơ.*
