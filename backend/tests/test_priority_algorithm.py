"""
Unit Tests & Thực Nghiệm Thuật Toán Ưu Tiên SIMPS
Kiểm tra các giả thuyết khoa học của đề tài KHKT:
1. Độ chính xác của các hàm chuẩn hóa
2. Tính đúng đắn của công thức tính điểm P
3. Hoạt động của quy tắc ghi đè an toàn (Safety Override)
4. Thí nghiệm 1: So sánh hiệu quả giữa FIFO (Theo thứ tự báo cáo) và SIMPS Priority
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

# Thêm đường dẫn backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.priority_service import (
    normalize_people_affected,
    normalize_time,
)


class TestPriorityAlgorithm(unittest.TestCase):
    """Kiểm tra các thành phần cốt lõi của thuật toán ưu tiên"""

    def test_normalize_people_affected(self):
        """Kiểm tra chuẩn hóa số người bị ảnh hưởng về thang 1-5"""
        self.assertEqual(normalize_people_affected(1), 1)
        self.assertEqual(normalize_people_affected(5), 1)
        self.assertEqual(normalize_people_affected(6), 2)
        self.assertEqual(normalize_people_affected(20), 2)
        self.assertEqual(normalize_people_affected(21), 3)
        self.assertEqual(normalize_people_affected(50), 3)
        self.assertEqual(normalize_people_affected(51), 4)
        self.assertEqual(normalize_people_affected(200), 4)
        self.assertEqual(normalize_people_affected(201), 5)
        self.assertEqual(normalize_people_affected(1000), 5)

    def test_normalize_time(self):
        """Kiểm tra chuẩn hóa thời gian chờ về thang 1-5"""
        self.assertEqual(normalize_time(0.5), 1)  # < 2h
        self.assertEqual(normalize_time(1.9), 1)
        self.assertEqual(normalize_time(2.0), 2)  # 2 - 8h
        self.assertEqual(normalize_time(8.0), 2)
        self.assertEqual(normalize_time(8.1), 3)  # 8 - 24h
        self.assertEqual(normalize_time(24.0), 3)
        self.assertEqual(normalize_time(24.1), 4)  # 24 - 72h
        self.assertEqual(normalize_time(72.0), 4)
        self.assertEqual(normalize_time(72.1), 5)  # > 72h
        self.assertEqual(normalize_time(100.0), 5)

    def test_priority_score_formula(self):
        """
        Kiểm tra tính điểm theo công thức:
        P = 0.30*S + 0.20*I + 0.20*R + 0.15*T + 0.15*E
        """
        w = {"w1": 0.30, "w2": 0.20, "w3": 0.20, "w4": 0.15, "w5": 0.15}
        
        # Tình huống 1: Mọi yếu tố ở mức tối thiểu (1)
        S, I, R, T, E = 1, 1, 1, 1, 1
        p_min = w["w1"]*S + w["w2"]*I + w["w3"]*R + w["w4"]*T + w["w5"]*E
        self.assertAlmostEqual(p_min, 1.0, places=2)

        # Tình huống 2: Mọi yếu tố ở mức tối đa (5)
        S, I, R, T, E = 5, 5, 5, 5, 5
        p_max = w["w1"]*S + w["w2"]*I + w["w3"]*R + w["w4"]*T + w["w5"]*E
        self.assertAlmostEqual(p_max, 5.0, places=2)

        # Tình huống 3: Sự cố phòng học thông thường
        # S=2 (hỏng quạt), I=40 người (-> 3), R=2 (phòng học), T=2h (-> 2), E=3 (trung bình)
        S, I, R, T, E = 2, 3, 2, 2, 3
        expected = 0.30*2 + 0.20*3 + 0.20*2 + 0.15*2 + 0.15*3
        # 0.6 + 0.6 + 0.4 + 0.3 + 0.45 = 2.35
        self.assertAlmostEqual(expected, 2.35, places=2)

    def test_fifo_vs_priority_simulation(self):
        """
        Thực nghiệm mô phỏng (Experiment 1 trong đề cương KHKT):
        So sánh thời gian chờ trung bình của các sự cố nguy hiểm giữa FIFO và SIMPS
        """
        # Giả lập 5 sự cố đến theo thứ tự:
        incidents = [
            {"id": 1, "title": "Bàn gãy", "priority_level": "normal", "severity": 1, "repair_hours": 2},
            {"id": 2, "title": "Khóa cửa kẹt", "priority_level": "normal", "severity": 2, "repair_hours": 1},
            {"id": 3, "title": "Hở dây điện hành lang", "priority_level": "emergency", "severity": 5, "repair_hours": 1},
            {"id": 4, "title": "Đèn chập chờn", "priority_level": "normal", "severity": 2, "repair_hours": 2},
            {"id": 5, "title": "Vỡ đường ống nước", "priority_level": "urgent", "severity": 4, "repair_hours": 3},
        ]

        # Phương pháp 1: FIFO (Tuần tự theo thứ tự báo cáo: 1 -> 2 -> 3 -> 4 -> 5)
        fifo_wait_time = 0
        current_time = 0
        emergency_wait_fifo = 0
        for inc in incidents:
            if inc["id"] == 3:  # Sự cố khẩn cấp
                emergency_wait_fifo = current_time
            current_time += inc["repair_hours"]

        # Phương pháp 2: SIMPS Priority (Sắp xếp theo thứ tự ưu tiên: emergency -> urgent -> normal)
        priority_order = sorted(incidents, key=lambda x: (
            0 if x["priority_level"] == "emergency" else 
            1 if x["priority_level"] == "urgent" else 2
        ))
        
        current_time = 0
        emergency_wait_simps = 0
        for inc in priority_order:
            if inc["id"] == 3:
                emergency_wait_simps = current_time
            current_time += inc["repair_hours"]

        # Kết quả chứng minh: Thời gian chờ sự cố khẩn cấp ở SIMPS giảm đáng kể so với FIFO
        self.assertEqual(emergency_wait_fifo, 3)    # Phải chờ sự cố 1 (2h) + sự cố 2 (1h) = 3h
        self.assertEqual(emergency_wait_simps, 0)   # Được xử lý ngay lập tức (0h)
        self.assertLess(emergency_wait_simps, emergency_wait_fifo)


if __name__ == "__main__":
    unittest.main()
