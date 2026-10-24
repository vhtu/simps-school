"""
Script xuất toàn bộ danh sách tài khoản người dùng và mật khẩu từ SQLite sang file Word (.docx).
"""

import sys
import os
from datetime import datetime

# Import backend modules
sys.path.insert(0, r'D:\KHKT\backend')
from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import verify_password

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls


def export_users_to_word():
    db = SessionLocal()
    users = db.query(User).order_by(User.id).all()

    doc = docx.Document()

    # Thiết lập lề trang
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    # Tiêu đề trên cùng
    p_top = doc.add_paragraph()
    r_top1 = p_top.add_run('CUỘC THI KHOA HỌC KỸ THUẬT DÀNH CHO HỌC SINH TRUNG HỌC NĂM 2026\nĐƠN VỊ: TRƯỜNG THPT Ô MÔN, TP CẦN THƠ\n')
    r_top1.font.size = Pt(10)
    r_top1.font.bold = True
    r_top1.font.color.rgb = RGBColor(100, 116, 139)

    r_top2 = p_top.add_run('HỆ THỐNG QUẢN LÝ VÀ ƯU TIÊN SỰ CỐ TRƯỜNG HỌC (SIMPS)\n')
    r_top2.font.size = Pt(11)
    r_top2.font.bold = True
    r_top2.font.color.rgb = RGBColor(79, 70, 229)

    r_top3 = p_top.add_run('Học sinh thực hiện: Lê Quốc Khánh và Hồ Anh Khoa | GVHD: Phan Thuý Quỳnh')
    r_top3.font.size = Pt(10)
    r_top3.font.italic = True
    r_top3.font.color.rgb = RGBColor(71, 85, 105)

    # Tiêu đề chính
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(14)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run('DANH SÁCH TÀI KHOẢN NGƯỜI DÙNG & MẬT KHẨU HỆ THỐNG')
    r_title.font.size = Pt(15)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run('(Dữ liệu thực nghiệm phục vụ kiểm thử, giám sát và chấm thi)')
    r_sub.font.size = Pt(10)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    # Thông tin đăng nhập
    p_info = doc.add_paragraph()
    p_info.paragraph_format.space_after = Pt(10)
    
    r_url_lbl = p_info.add_run('• Địa chỉ truy cập hệ thống (Web App): ')
    r_url_lbl.font.bold = True
    r_url = p_info.add_run('https://simps-school.vercel.app (Online) | http://localhost:8000 (Local)\n')
    r_url.font.bold = True
    r_url.font.color.rgb = RGBColor(79, 70, 229)

    r_rules = p_info.add_run(
        '• Quy ước mật khẩu mặc định:\n'
        '   + Tài khoản Quản trị viên (admin): mật khẩu là "admin123"\n'
        '   + Tất cả các tài khoản còn lại (Nhân viên CSVC, Hiệu trưởng, Học sinh): mật khẩu là "123456"\n'
        '• An toàn bảo mật: Trong cơ sở dữ liệu (SQLite), toàn bộ mật khẩu đều được mã hóa một chiều bằng giải thuật Bcrypt ($2b$12$).'
    )
    r_rules.font.size = Pt(9.5)
    r_rules.font.color.rgb = RGBColor(51, 65, 85)

    # Bảng dữ liệu
    headers = ['STT', 'Tên Đăng Nhập', 'Mật Khẩu', 'Họ và Tên', 'Vai Trò', 'Lớp / Bộ Phận', 'Email']
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Format Header
    header_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        header_cells[i].text = h
        shading = parse_xml(r'<w:shd {} w:fill="4F46E5"/>'.format(nsdecls('w')))
        header_cells[i]._tc.get_or_add_tcPr().append(shading)
        header_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = header_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(255, 255, 255)

    # Thêm từng user vào bảng
    for i, u in enumerate(users, start=1):
        row = table.add_row()
        cells = row.cells

        pw = 'admin123' if verify_password('admin123', u.password_hash) else '123456'

        # STT
        cells[0].text = str(u.id)
        cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Username
        cells[1].text = u.username
        cells[1].paragraphs[0].runs[0].font.bold = True

        # Password
        cells[2].text = pw
        cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cells[2].paragraphs[0].runs[0].font.bold = True
        if pw == 'admin123':
            cells[2].paragraphs[0].runs[0].font.color.rgb = RGBColor(220, 38, 38)
        else:
            cells[2].paragraphs[0].runs[0].font.color.rgb = RGBColor(5, 150, 105)

        # Full Name
        cells[3].text = u.full_name or ''

        # Role
        role_vn = 'Quản trị' if u.role == 'admin' else ('Nhân viên' if u.role == 'staff' else 'Học sinh')
        cells[4].text = role_vn
        cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Class / Dept
        cells[5].text = u.class_name or ('Tổ Kỹ thuật' if u.role == 'staff' else 'Ban Giám Hiệu')

        # Email
        cells[6].text = u.email or '--'

        # Màu dòng so le (Zebra striping)
        bg = 'F8FAFC' if i % 2 == 1 else 'FFFFFF'
        for c in cells:
            shading = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), bg))
            c._tc.get_or_add_tcPr().append(shading)
            c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = c.paragraphs[0]
            if len(p.runs) > 0:
                p.runs[0].font.size = Pt(9)

    # Căn chỉnh độ rộng cột
    col_widths = [Inches(0.45), Inches(1.2), Inches(0.9), Inches(1.8), Inches(0.8), Inches(0.95), Inches(1.6)]
    for row in table.rows:
        for j, w in enumerate(col_widths):
            row.cells[j].width = w

    # Ghi chú chân trang
    p_foot = doc.add_paragraph()
    p_foot.paragraph_format.space_before = Pt(14)
    r_foot = p_foot.add_run(f'Xuất tự động ngày {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} từ cơ sở dữ liệu: D:\\KHKT\\backend\\simps.db')
    r_foot.font.size = Pt(8.5)
    r_foot.font.italic = True
    r_foot.font.color.rgb = RGBColor(148, 163, 184)

    output_path = r'D:\KHKT\Danh_sach_tai_khoan_nguoi_dung_SIMPS.docx'
    doc.save(output_path)
    print(f'Successfully exported {len(users)} accounts to: {output_path}')
    db.close()


if __name__ == '__main__':
    export_users_to_word()
