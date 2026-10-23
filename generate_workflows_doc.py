"""
Script tự động tạo tài liệu Word (.docx) mô tả chi tiết các luồng chính
của Hệ thống Quản lý và Ưu tiên Xử lý Sự cố Cơ sở vật chất Trường học (SIMPS).
Phục vụ thuyết minh và báo cáo đề tài Khoa học Kỹ thuật (KHKT).
"""

import os
from datetime import datetime
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Đặt màu nền cho ô trong bảng"""
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Đặt lề trong cho ô (padding)"""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_document():
    doc = Document()

    # Thiết lập lề trang chuẩn (A4, lề 2cm mỗi bên)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    # Đặt style mặc định
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Arial'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = RGBColor(30, 41, 59) # Slate 800
    style_normal.paragraph_format.line_spacing = 1.2
    style_normal.paragraph_format.space_after = Pt(4)

    # --- TIÊU ĐỀ BÌA TÀI LIỆU ---
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_header.add_run("CUỘC THI KHOA HỌC KỸ THUẬT DÀNH CHO HỌC SINH TRUNG HỌC NĂM 2026\nLĨNH VỰC: HỆ THỐNG NHÚNG & PHẦN MỀM HỆ THỐNG\n")
    r_sub.font.size = Pt(10)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("TÀI LIỆU MÔ TẢ KIẾN TRÚC & CÁC LUỒNG HOẠT ĐỘNG CHÍNH\nHỆ THỐNG QUẢN LÝ VÀ ƯU TIÊN XỬ LÝ SỰ CỐ\nCƠ SỞ VẬT CHẤT TRƯỜNG HỌC (SIMPS)")
    r_title.font.size = Pt(17)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(30, 58, 138) # Navy Blue
    p_title.paragraph_format.space_after = Pt(6)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_desc = p_sub.add_run("School Incident Management and Prioritization System (SIMPS)\nThuật toán xếp hạng đa tiêu chí tuyến tính kết hợp cơ chế ghi đè an toàn (Safety Override)")
    r_desc.font.size = Pt(11)
    r_desc.font.italic = True
    r_desc.font.color.rgb = RGBColor(71, 85, 105)
    p_sub.paragraph_format.space_after = Pt(20)

    # Đường kẻ phân cách
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_line = p_line.add_run("—" * 38)
    r_line.font.color.rgb = RGBColor(203, 213, 225)
    p_line.paragraph_format.space_after = Pt(16)

    # Helper function cho heading
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(37, 99, 235)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 23, 42)
        return p

    def add_callout(text, title="LƯU Ý QUAN TRỌNG:"):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.rows[0].cells[0]
        set_cell_background(cell, "EFF6FF") # Blue 50
        set_cell_margins(cell, 120, 120, 180, 180)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r_t = p.add_run(f"📌 {title} ")
        r_t.font.bold = True
        r_t.font.size = Pt(10.5)
        r_t.font.color.rgb = RGBColor(30, 58, 138)
        r_c = p.add_run(text)
        r_c.font.size = Pt(10.5)
        r_c.font.color.rgb = RGBColor(30, 41, 59)
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ================= CHƯƠNG 1 =================
    add_h1("CHƯƠNG 1: TỔNG QUAN HỆ THỐNG SIMPS")
    doc.add_paragraph(
        "Hệ thống SIMPS (School Incident Management and Prioritization System) là giải pháp công nghệ thông tin "
        "toàn diện nhằm giải quyết bài toán tiếp nhận, xếp thứ tự ưu tiên và theo dõi xử lý các sự cố cơ sở vật chất "
        "(điện, quạt, máy chiếu, thiết bị thí nghiệm, hệ thống cấp thoát nước, bàn ghế...) trong môi trường giáo dục phổ thông."
    )
    doc.add_paragraph(
        "Khác với phương pháp truyền thống (ghi sổ trực tuần, báo miệng hoặc phản ánh qua mạng xã hội phân tán), SIMPS "
        "ứng dụng công nghệ web hiện đại (FastAPI + Vanilla Modern JS + SQLite) và đặc biệt sở hữu Thuật toán xếp hạng ưu tiên "
        "đa tiêu chí tuyến tính khách quan (Multi-Criteria Scoring). Hệ thống hoàn toàn không phụ thuộc vào trí tuệ nhân tạo (AI) "
        "phức tạp, mà dựa trên logic toán học minh bạch, giúp đảm bảo tính tức thời, tính chính xác và giải thích rõ ràng được từng quyết định phân loại."
    )

    # ================= CHƯƠNG 2 =================
    add_h1("CHƯƠNG 2: CÁC TÁC NHÂN THAM GIA HỆ THỐNG (ACTORS & ROLES)")
    doc.add_paragraph(
        "Hệ thống phân quyền nghiêm ngặt theo mô hình RBAC (Role-Based Access Control) thông qua mã định danh JWT (JSON Web Token), "
        "chia người dùng thành 3 nhóm tác nhân chính:"
    )

    t_actor = doc.add_table(rows=4, cols=3)
    t_actor.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t_actor.rows[0].cells
    hdr[0].text = "Vai trò (Role)"
    hdr[1].text = "Đối tượng thực tế"
    hdr[2].text = "Nhiệm vụ & Quyền hạn cốt lõi"
    for c in hdr:
        set_cell_background(c, "1E3A8A")
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(c, 100, 100, 120, 120)

    actors_data = [
        ("Học sinh (Student)", "Học sinh các khối lớp trong nhà trường", 
         "• Phát hiện và gửi phiếu báo cáo sự cố kèm hình ảnh hiện trường.\n• Theo dõi tiến trình khắc phục sự cố theo thời gian thực (Timeline Stepper).\n• Nghiệm thu và bấm 'Xác nhận' khi thợ đã sửa chữa đạt yêu cầu."),
        ("Kỹ thuật viên CSVC (Staff)", "Tổ bảo trì điện, nước, máy tính, thợ mộc", 
         "• Tiếp nhận sự cố từ Hàng đợi ưu tiên (Priority Queue) sắp xếp theo Điểm P.\n• Lọc sự cố theo chuyên môn (Điện/Nước/Mạng), theo Tòa nhà, hoặc sự cố Quá hạn (>72h).\n• Cập nhật trạng thái (Tiếp nhận -> Phân công -> Đang sửa -> Hoàn tất kèm ghi chú giải pháp)."),
        ("Quản trị viên (Admin)", "Ban Giám Hiệu, Thầy Cô quản lý Cơ sở vật chất", 
         "• Giám sát toàn cảnh qua 5 biểu đồ thống kê Hi-DPI chuyên nghiệp.\n• Điều chỉnh bộ trọng số (w1 - w5) và mô phỏng tức thì qua Bộ giả lập Sandbox.\n• Quản trị danh mục địa điểm, loại sự cố, cơ chế An toàn đặc biệt và cấp tài khoản người dùng.\n• Xuất dữ liệu báo cáo ra file Excel / CSV (UTF-8 BOM).")
    ]

    for idx, (role, obj, duty) in enumerate(actors_data):
        row = t_actor.rows[idx + 1].cells
        row[0].text = role
        row[1].text = obj
        row[2].text = duty
        bg = "FFFFFF" if idx % 2 == 0 else "F8FAFC"
        for c in row:
            set_cell_background(c, bg)
            set_cell_margins(c, 80, 80, 100, 100)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # ================= CHƯƠNG 3 =================
    add_h1("CHƯƠNG 3: CHI TIẾT CÁC LUỒNG HOẠT ĐỘNG CHÍNH (CORE WORKFLOWS)")

    # LUỒNG 1
    add_h2("3.1. Luồng 1: Xác Thực & Điều Hướng Người Dùng (Authentication & Navigation Flow)")
    doc.add_paragraph(
        "Mục tiêu: Đảm bảo an toàn bảo mật, định danh chính xác người thực hiện hành động và tự động chuyển hướng "
        "đến không gian làm việc chuyên biệt tương ứng với vai trò."
    )
    doc.add_paragraph(
        "1. Người dùng truy cập trang đăng nhập (index.html), cung cấp Tên đăng nhập (Username) và Mật khẩu (Password).\n"
        "2. Client gửi POST request đến `/api/auth/login`.\n"
        "3. Backend kiểm tra tài khoản, xác thực mật khẩu qua thuật toán mã hóa một chiều Bcrypt.\n"
        "4. Nếu hợp lệ, Backend sinh chuỗi mã hóa JWT Token (chứa user_id, username, role và thời hạn hiệu lực) trả về Client.\n"
        "5. Client lưu trữ Token vào LocalStorage, giải mã thông tin vai trò và tự động chuyển hướng:\n"
        "   • Role = 'student' -> Chuyển đến `pages/student.html`\n"
        "   • Role = 'staff' -> Chuyển đến `pages/staff.html`\n"
        "   • Role = 'admin' -> Chuyển đến `pages/admin.html`\n"
        "6. Khi người dùng thực hiện bất kỳ thao tác nào, Token được tự động gắn vào Header `Authorization: Bearer <token>` để kiểm tra quyền truy cập."
    )

    # LUỒNG 2
    add_h2("3.2. Luồng 2: Tiếp Nhận Báo Cáo Sự Cố Từ Học Sinh (Incident Reporting Flow)")
    doc.add_paragraph(
        "Mục tiêu: Cho phép học sinh gửi báo cáo hư hỏng nhanh chóng, chính xác với đầy đủ các tham số định lượng "
        "phục vụ thuật toán tính điểm ưu tiên."
    )
    doc.add_paragraph(
        "Các bước thực hiện:\n"
        "1. Học sinh đăng nhập cổng `student.html` và nhấn nút '➕ Báo Cáo Sự Cố Mới'.\n"
        "2. Điền thông tin vào Phiếu Tiếp Nhận Báo Cáo:\n"
        "   • Tiêu đề ngắn gọn & Mô tả chi tiết hiện trường.\n"
        "   • Danh mục loại sự cố (Quạt, Đèn, Nước, Máy chiếu, Bàn ghế...).\n"
        "   • Địa điểm phát hiện (chọn phòng học/khu vực; hệ thống tự động gắn Mức rủi ro khu vực R từ 1-5).\n"
        "   • Mức độ hư hỏng nghiêm trọng (S - Severity): Thang trực quan 1 (Rất nhẹ) đến 5 (Rất nguy hiểm).\n"
        "   • Ước tính số người bị ảnh hưởng trực tiếp (I - People Affected): Điền số người (VD: 40 học sinh/lớp).\n"
        "   • Mức độ ảnh hưởng đến giờ học (E - Learning Impact): Thang 1 (Không ảnh hưởng) đến 5 (Buộc phải dừng tiết học).\n"
        "   • Đính kèm hình ảnh minh chứng hiện trường (Tùy chọn).\n"
        "3. Học sinh bấm '🚀 Gửi Báo Cáo Đến Ban CSVC'. Hệ thống tải ảnh (nếu có) lên máy chủ, kiểm chứng dữ liệu và gửi POST `/api/incidents`.\n"
        "4. Kích hoạt tự động Luồng 3 (Thuật toán tính điểm ưu tiên P) và Luồng 4 (Hệ thống thông báo thời gian thực)."
    )

    # LUỒNG 3 - CORE
    add_h2("3.3. Luồng 3: Thuật Toán Xếp Hạng & Ưu Tiên Đa Tiêu Chí (Priority Algorithm & Safety Override)")
    doc.add_paragraph(
        "Đây là TRÁI TIM KHOA HỌC CỐT LÕI của đề tài. Thuật toán hoạt động theo nguyên lý đánh giá đa tiêu chí "
        "kết hợp cơ chế phản xạ an toàn khẩn cấp, giải quyết triệt để tình trạng cảm tính trong điều phối CSVC."
    )
    
    add_callout(
        "P = w1 × S + w2 × I + w3 × R + w4 × T + w5 × E\n"
        "Trong đó: w1 + w2 + w3 + w4 + w5 = 1.00\n"
        "Bộ trọng số mặc định (xác lập từ khảo sát thực tế): w1=0.30, w2=0.20, w3=0.20, w4=0.15, w5=0.15.",
        "CÔNG THỨC TÍNH ĐIỂM ƯU TIÊN TUYẾN TÍNH:"
    )

    doc.add_paragraph("Chi tiết các biến số thành phần chuẩn hóa (Scale 1 đến 5):")
    doc.add_paragraph(
        "• S (Severity - Mức độ nghiêm trọng vật lý): Đánh giá trực quan từ 1 đến 5.\n"
        "• I (Impact - Quy mô người bị ảnh hưởng): Chuẩn hóa phi tuyến số người thực tế:\n"
        "   - 1 - 5 người (cá nhân) -> Điểm I = 1\n"
        "   - 6 - 20 người (nhóm học sinh) -> Điểm I = 2\n"
        "   - 21 - 50 người (quy mô 1 lớp học) -> Điểm I = 3\n"
        "   - 51 - 200 người (quy mô khối lớp) -> Điểm I = 4\n"
        "   - Trên 200 người (toàn trường/sân trường/khu công cộng) -> Điểm I = 5\n"
        "• R (Risk Level - Mức độ rủi ro địa điểm): Gắn liền với vị trí xảy ra (Phòng học bình thường R=2, Cầu thang/sân trường R=4, Phòng thí nghiệm Hóa/Trạm điện R=5).\n"
        "• T (Time Waiting - Thời gian chờ chưa được giải quyết): Tính năng 'Tự động tăng điểm ưu tiên theo thời gian' (Aging effect):\n"
        "   - Dưới 2 giờ -> Điểm T = 1\n"
        "   - Từ 2 đến 8 giờ -> Điểm T = 2\n"
        "   - Từ 8 đến 24 giờ (1 ngày) -> Điểm T = 3\n"
        "   - Từ 24 đến 72 giờ (3 ngày) -> Điểm T = 4\n"
        "   - Trên 72 giờ (Quá hạn) -> Điểm T = 5 (Được gắn cờ đỏ cảnh báo trễ hạn)\n"
        "• E (Educational Impact - Ảnh hưởng giảng dạy): Đánh giá từ 1 đến 5."
    )

    add_callout(
        "Nếu Địa điểm có mức rủi ro R = 5 (Phòng thí nghiệm Hóa học, Trạm biến áp...) "
        "HOẶC Sự cố thuộc danh mục 'An toàn đặc biệt' (Dây điện hở, cháy nổ, bình chữa cháy hỏng, sập lan can...):\n"
        "-> HỆ THỐNG TỰ ĐỘNG GHI ĐÈ BỎ QUA CÔNG THỨC: Thiết lập Điểm P = 999 và Mức ưu tiên là KHẨN CẤP (EMERGENCY).\n"
        "Phát tín hiệu còi hú và banner cảnh báo đỏ toàn màn hình đến Kỹ thuật viên.",
        "CƠ CHẾ PHẢN XẠ AN TOÀN ĐẶC BIỆT (SAFETY OVERRIDE):"
    )

    doc.add_paragraph("Phân cấp mức ưu tiên (Priority Levels):")
    doc.add_paragraph(
        "1. KHẨN CẤP (Emergency - Màu Đỏ nhấp nháy): Điểm P = 999 (Kích hoạt do Safety Override).\n"
        "2. CẤP BÁCH (Urgent - Màu Cam): Điểm P ≥ 3.5 (Cần xử lý trong vòng 4 giờ).\n"
        "3. ƯU TIÊN CAO (High - Màu Vàng): Điểm 2.5 ≤ P < 3.5 (Cần xử lý trong ngày).\n"
        "4. BÌNH THƯỜNG (Normal - Màu Xanh): Điểm P < 2.5 (Bảo dưỡng theo lịch tuần)."
    )

    # LUỒNG 4
    add_h2("3.4. Luồng 4: Thông Báo Thời Gian Thực (Real-Time Notification Flow)")
    doc.add_paragraph(
        "Mục tiêu: Đảm bảo thông tin hai chiều thông suốt, không để sót bất kỳ sự cố hay tiến độ xử lý nào."
    )
    doc.add_paragraph(
        "1. Kích hoạt thông báo:\n"
        "   • Khi học sinh gửi báo cáo mới -> Tự động sinh bản ghi thông báo loại `incident_reported` cho Ban Quản trị và toàn bộ Kỹ thuật viên CSVC.\n"
        "   • Khi sự cố được xếp mức 'Khẩn cấp' -> Tạo cảnh báo nguy hiểm ưu tiên cao nhất (`type: emergency`).\n"
        "   • Khi kỹ thuật viên sửa chữa xong (`status: resolved`) -> Tự động sinh thông báo loại `incident_resolved` gửi riêng cho học sinh đã báo cáo.\n"
        "2. Cơ chế phân phối & Giao diện:\n"
        "   • Cổng Frontend duy trì cơ chế Polling thông minh (chu kỳ 6 giây) kiểm tra thông báo mới qua `/api/notifications`.\n"
        "   • Chuông thông báo hiển thị huy hiệu đếm số lượng tin chưa đọc (Unread Badge).\n"
        "   • Khi có tin mới, hệ thống tự động phát âm thanh chuông hai âm sắc (Web Audio API Chime 587Hz -> 880Hz) mà không cần thư viện ngoài.\n"
        "   • Người dùng bấm vào chuông để xem danh sách, bấm vào từng tin để mở trực tiếp chi tiết sự cố và đánh dấu đã đọc."
    )

    # LUỒNG 5
    add_h2("3.5. Luồng 5: Điều Phối, Phân Công & Khắc Phục Sự Cố Kỹ Thuật (Staff Handling Flow)")
    doc.add_paragraph(
        "Mục tiêu: Cung cấp cho đội ngũ kỹ thuật giao diện 'Trung tâm chỉ huy' (Command Center) trực quan, "
        "giúp xử lý đúng việc, đúng người, đúng mức độ cấp bách."
    )
    doc.add_paragraph(
        "1. Xem Hàng đợi ưu tiên (Priority Queue):\n"
        "   • Kỹ thuật viên truy cập `pages/staff.html`.\n"
        "   • Hàng đợi hiển thị toàn bộ sự cố được tự động sắp xếp giảm dần theo Điểm ưu tiên P. Các sự cố Khẩn cấp luôn ở đầu danh sách.\n"
        "   • Biểu đồ phân bổ công việc theo Chuyên môn (Điện, Nước, Máy tính, Bàn ghế...) hiển thị khối lượng công việc đang tồn đọng.\n"
        "2. Ứng dụng bộ lọc linh hoạt:\n"
        "   • Lọc theo Chuyên môn (thợ điện chỉ xem thiết bị điện, thợ sửa ống nước chỉ xem sự cố nước).\n"
        "   • Lọc theo Khu vực / Tòa nhà (Tòa A, Tòa B, Tòa C) để xử lý cuốn chiếu theo vị trí địa lý.\n"
        "   • Lọc phân công: 'Việc chưa ai nhận' (để nhận việc mới), 'Việc được giao cho tôi' (quản lý công việc cá nhân).\n"
        "   • Bật chế độ '⚠️ Chỉ hiển thị sự cố trễ hạn (> 72h)' để ưu tiên giải quyết dứt điểm các ca tồn đọng.\n"
        "3. Thực hiện chu trình xử lý:\n"
        "   • Nhấn 'Xử lý' trên dòng sự cố -> Mở Modal cập nhật tiến độ.\n"
        "   • Đổi trạng thái: `reported` (Mới) -> `received` (Tiếp nhận) -> `assigned` (Phân công người phụ trách) -> `in_progress` (Bắt đầu sửa chữa) -> `resolved` (Đã hoàn tất sửa chữa).\n"
        "   • Nhập ghi chú giải pháp kỹ thuật và vật tư thay thế (ví dụ: 'Đã thay mới bóng đèn LED 1.2m, kiểm tra lại dây nối an toàn').\n"
        "   • Hệ thống tự động ghi nhật ký vào bảng `status_history` để phục vụ thanh tra và truy vết sau này."
    )

    # LUỒNG 6
    add_h2("3.6. Luồng 6: Học Sinh Nghiệm Thu & Đóng Sự Cố (Verification & Closure Flow)")
    doc.add_paragraph(
        "Mục tiêu: Đóng kín quy trình quản lý chất lượng (Closed-Loop Quality Control), trao quyền cho học sinh "
        "nghiệm thu thực tế tại hiện trường trước khi sự cố được coi là hoàn tất."
    )
    doc.add_paragraph(
        "1. Khi kỹ thuật viên đánh dấu sự cố là `resolved` (Đã khắc phục), học sinh nhận được thông báo chuông và thấy thẻ sự cố chuyển sang màu vàng hổ phách nổi bật với nút '🔔 Cần xác nhận'.\n"
        "2. Học sinh đến lớp học / khu vực phát hiện sự cố để kiểm tra thực tế xem thiết bị đã hoạt động ổn định và an toàn hay chưa.\n"
        "3. Nếu đã khắc phục tốt: Học sinh bấm nút '✅ Xác nhận'.\n"
        "4. Hệ thống chuyển trạng thái sang `confirmed` (Đã nghiệm thu), lưu thời gian hoàn tất thực tế (`confirmed_at`), gửi lời cảm ơn đến học sinh và đóng sự cố (`closed`).\n"
        "5. Nếu thiết bị vẫn chưa hoạt động tốt: Học sinh có thể phản hồi lại để kỹ thuật viên tiếp tục kiểm tra xử lý."
    )

    # LUỒNG 7
    add_h2("3.7. Luồng 7: Giám Sát, Thống Kê & Hiệu Chỉnh Của Quản Trị Viên (Admin Analytics & Simulator Flow)")
    doc.add_paragraph(
        "Mục tiêu: Giúp Ban Giám Hiệu và Ban CSVC nắm bắt bức tranh toàn cảnh về độ bền, độ ổn định của thiết bị học đường, "
        "đồng thời có công cụ nghiên cứu khoa học để tinh chỉnh thuật toán."
    )
    doc.add_paragraph(
        "1. Theo dõi 5 Biểu đồ Thống kê Trực quan (Canvas API chuẩn Hi-DPI):\n"
        "   • Biểu đồ 1 (Donut Chart): Phân bổ tỷ lệ phần trăm các loại sự cố phổ biến nhất.\n"
        "   • Biểu đồ 2 (Bar Chart): Điểm nóng cơ sở vật chất (Top các phòng học, khu vực phát sinh nhiều hư hỏng nhất).\n"
        "   • Biểu đồ 3 (Timeline Bar Chart): Tần suất phát sinh sự cố theo chuỗi 12 tháng (phục vụ dự báo bảo dưỡng định kỳ).\n"
        "   • Biểu đồ 4 (Horizontal Bar Chart): Thời gian giải quyết trung bình theo từng Mức Ưu Tiên (chứng minh sự cố Khẩn cấp có thời gian xử lý ngắn nhất).\n"
        "   • Biểu đồ 5 (Grouped Bar Chart): Đánh giá hiệu suất làm việc của từng Kỹ thuật viên CSVC (số sự cố đang xử lý vs đã hoàn thành).\n"
        "2. Thử nghiệm với Bộ Giả Lập Trọng Số (Formula Sandbox Simulator):\n"
        "   • Kéo thanh trượt điều chỉnh từng trọng số w1, w2, w3, w4, w5 trong công thức P.\n"
        "   • Theo dõi mẫu tính toán điểm giả lập trực tiếp ngay trên màn hình.\n"
        "   • Khi bấm 'Lưu Trọng Số Mới', hệ thống gửi yêu cầu cập nhật và tự động tính toán lại Điểm P cho toàn bộ các sự cố đang mở trong trường.\n"
        "3. Quản lý toàn diện Cơ sở dữ liệu sự cố & Xuất báo cáo:\n"
        "   • Tìm kiếm, lọc theo tòa nhà, mức ưu tiên, trạng thái, người phụ trách.\n"
        "   • Bấm '📥 Xuất File Excel / CSV': Hệ thống tự động tạo tệp tin `.csv` chuẩn UTF-8 BOM tiếng Việt, mở trực tiếp bằng Microsoft Excel không lỗi font chữ."
    )

    # ================= CHƯƠNG 4 =================
    add_h1("CHƯƠNG 4: VÒNG ĐỜI TRẠNG THÁI SỰ CỐ (INCIDENT STATE LIFECYCLE)")
    doc.add_paragraph(
        "Mỗi sự cố trong hệ thống SIMPS tuân theo máy trạng thái hữu hạn (Finite State Machine) nghiêm ngặt gồm 7 trạng thái liên tiếp:"
    )

    t_states = doc.add_table(rows=8, cols=3)
    t_states.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_hdr = t_states.rows[0].cells
    s_hdr[0].text = "Trạng thái (Status Code)"
    s_hdr[1].text = "Tên hiển thị tiếng Việt"
    s_hdr[2].text = "Ý nghĩa & Tác nhân chuyển trạng thái"
    for c in s_hdr:
        set_cell_background(c, "1E3A8A")
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(c, 100, 100, 120, 120)

    states_data = [
        ("reported", "Mới báo cáo", "Sự cố vừa được học sinh gửi lên hệ thống, điểm P đã được tính toán, đang chờ tổ kỹ thuật tiếp nhận."),
        ("received", "Đã tiếp nhận", "Tổ kỹ thuật CSVC đã xem xét phiếu báo cáo và chấp thuận đưa vào kế hoạch sửa chữa."),
        ("assigned", "Đã phân công", "Trưởng bộ phận hoặc Admin chỉ định cụ thể kỹ thuật viên chuyên trách (thợ điện, thợ nước...)."),
        ("in_progress", "Đang xử lý", "Kỹ thuật viên đã có mặt tại hiện trường phòng học và bắt đầu quá trình tháo lắp, khắc phục."),
        ("resolved", "Đã sửa xong", "Kỹ thuật viên hoàn tất công việc, ghi chú giải pháp và gửi yêu cầu nghiệm thu đến học sinh."),
        ("confirmed", "Đã xác nhận", "Học sinh kiểm tra thực tế, xác nhận thiết bị đã hoạt động tốt và an toàn."),
        ("closed", "Đóng sự cố", "Lưu trữ sự cố vào kho dữ liệu lịch sử phục vụ thống kê và đánh giá khấu hao tài sản nhà trường.")
    ]

    for idx, (code, name, meaning) in enumerate(states_data):
        row = t_states.rows[idx + 1].cells
        row[0].text = code
        row[1].text = name
        row[2].text = meaning
        bg = "FFFFFF" if idx % 2 == 0 else "F8FAFC"
        for c in row:
            set_cell_background(c, bg)
            set_cell_margins(c, 80, 80, 100, 100)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ================= CHƯƠNG 5 =================
    add_h1("CHƯƠNG 5: ĐÁNH GIÁ TÍNH MỚI, TÍNH THỰC TIỄN & HIỆU QUẢ CỦA ĐỀ TÀI")
    
    add_h2("5.1. Tính mới và sáng tạo")
    doc.add_paragraph(
        "1. Ứng dụng Thuật toán Đa tiêu chí Tuyến tính kết hợp Ghi đè An toàn (Safety Override): Thay vì sắp xếp sự cố theo thứ tự thời gian nộp đơn (FIFO) hoặc hoàn toàn theo cảm tính, SIMPS là hệ thống đầu tiên trong nhà trường lượng hóa chính xác mức độ khẩn cấp dựa trên 5 yếu tố cốt lõi (S, I, R, T, E).\n"
        "2. Cơ chế Tự động tăng điểm theo thời gian chờ (Aging Mechanism): Đảm bảo các sự cố nhỏ (mức P thấp) không bao giờ bị bỏ quên vĩnh viễn, khi quá 72 giờ sẽ tự động được đẩy lên thang điểm cao nhất.\n"
        "3. Đóng kín vòng lặp chất lượng (Closed-Loop Quality Control): Buộc quy trình sửa chữa phải có sự nghiệm thu của chính học sinh bị ảnh hưởng trước khi đóng hồ sơ."
    )

    add_h2("5.2. Tính khả thi và khả năng áp dụng thực tế")
    doc.add_paragraph(
        "• Công nghệ gọn nhẹ, độc lập: Hệ thống sử dụng FastAPI (Python) và Vanilla HTML/CSS/JS, không cần cài đặt các thư viện front-end nặng nề, có thể chạy trơn tru trên một máy tính văn phòng thông thường đóng vai trò máy chủ cục bộ (Local Server) của nhà trường.\n"
        "• Tiết kiệm ngân sách tối đa: Không tốn chi phí thuê API AI thương mại, chi phí duy trì phần mềm bằng 0 đồng.\n"
        "• Dễ dàng nhân rộng: Có thể triển khai cho bất kỳ trường Tiểu học, THCS, THPT nào trên toàn quốc chỉ trong vòng 15 phút cài đặt."
    )

    # Footer note
    doc.add_paragraph().paragraph_format.space_after = Pt(20)
    p_end = doc.add_paragraph()
    p_end.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_time = p_end.add_run(f"Tài liệu xuất bản tự động từ Hệ thống SIMPS • Ngày {datetime.now().strftime('%d/%m/%Y')}")
    r_time.font.italic = True
    r_time.font.size = Pt(9.5)
    r_time.font.color.rgb = RGBColor(148, 163, 184)

    # Lưu tài liệu
    output_path = r"D:\KHKT\Mo_ta_cac_luong_chinh_he_thong_SIMPS.docx"
    doc.save(output_path)
    print(f"Generated docx successfully: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    create_document()
