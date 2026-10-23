"""
Điểm khởi động Serverless Function cho Vercel.
Tự động nạp ứng dụng FastAPI từ thư mục backend.
"""

import sys
import os

# Nạp đường dẫn backend vào sys.path để import các module app.*
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(root_dir, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
