"""
Statistics Engine - เครื่องมือคำนวณทางสถิติพื้นฐาน
รองรับ: ค่าเฉลี่ย, มัธยฐาน, ฐานนิยม, ส่วนเบี่ยงเบนมาตรฐาน, ความแปรปรวน
"""

import math
from typing import Dict, Any, List
import sys
import os

# เพิ่ม path สำหรับ import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engines.base_engine import BaseEngine


class StatisticsEngine(BaseEngine):
    """Engine สำหรับการคำนวณทางสถิติ"""
    
    def __init__(self):
        super().__init__(name="statistics", version="1.0")
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        ประมวลผลคำสั่งทางสถิติ
        
        Args:
            params: พารามิเตอร์รวมถึง 'action', 'data', 'formula'
            
        Returns:
            dict: ผลลัพธ์การคำนวณ
        """
        action = params.get("action", "").lower()
        data = params.get("data", [])
        formula = params.get("formula", "")
        
        # แปลงข้อมูลถ้าเป็น string
        if isinstance(data, str):
            data = self._parse_data_string(data)
        
        if action == "mean" or "ค่าเฉลี่ย" in action or "average" in action.lower():
            result = self._calculate_mean(data)
            return {"response": result, "statistic_type": "mean"}
        
        elif action == "median" or "มัธยฐาน" in action.lower():
            result = self._calculate_median(data)
            return {"response": result, "statistic_type": "median"}
        
        elif action == "mode" or "ฐานนิยม" in action.lower():
            result = self._calculate_mode(data)
            return {"response": result, "statistic_type": "mode"}
        
        elif action == "std" or "std_dev" in action or "ส่วนเบี่ยงเบน" in action.lower():
            result = self._calculate_std(data)
            return {"response": result, "statistic_type": "std_dev"}
        
        elif action == "variance" or "ความแปรปรวน" in action.lower():
            result = self._calculate_variance(data)
            return {"response": result, "statistic_type": "variance"}
        
        elif action == "min" or "ต่ำสุด" in action.lower():
            result = self._calculate_min(data)
            return {"response": result, "statistic_type": "min"}
        
        elif action == "max" or "สูงสุด" in action.lower():
            result = self._calculate_max(data)
            return {"response": result, "statistic_type": "max"}
        
        elif action == "range" or "พิสัย" in action.lower():
            result = self._calculate_range(data)
            return {"response": result, "statistic_type": "range"}
        
        elif action == "all" or "ทั้งหมด" in action.lower() or not action:
            # คำนวณทั้งหมด
            results = {
                "mean": self._calculate_mean(data),
                "median": self._calculate_median(data),
                "mode": self._calculate_mode(data),
                "std_dev": self._calculate_std(data),
                "variance": self._calculate_variance(data),
                "min": self._calculate_min(data),
                "max": self._calculate_max(data),
                "range": self._calculate_range(data),
            }
            return {"response": results, "statistic_type": "all"}
        
        else:
            return {"response": f"⚠️ Unknown statistics action: {action}", "error": True}
    
    def _parse_data_string(self, data_str: str) -> List[float]:
        """แปลง string ของตัวเลขเป็น list"""
        import re
        # แยกตัวเลขด้วย comma, space, หรือภาษาไทย
        numbers = re.findall(r'-?\d+(?:\.\d+)?', data_str)
        return [float(n) for n in numbers]
    
    def _calculate_mean(self, data: List[float]) -> str:
        """คำนวณค่าเฉลี่ย"""
        if not data:
            return "Error: No data provided"
        mean = sum(data) / len(data)
        return f"📊 ค่าเฉลี่ย (Mean): {mean:.4f}" if mean != int(mean) else f"📊 ค่าเฉลี่ย (Mean): {int(mean)}"
    
    def _calculate_median(self, data: List[float]) -> str:
        """คำนวณมัธยฐาน"""
        if not data:
            return "Error: No data provided"
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        
        if n % 2 == 0:
            median = (sorted_data[mid - 1] + sorted_data[mid]) / 2
        else:
            median = sorted_data[mid]
        
        return f"📊 มัธยฐาน (Median): {median:.4f}" if median != int(median) else f"📊 มัธยฐาน (Median): {int(median)}"
    
    def _calculate_mode(self, data: List[float]) -> str:
        """คำนวณฐานนิยม"""
        if not data:
            return "Error: No data provided"
        
        from collections import Counter
        count = Counter(data)
        max_count = max(count.values())
        modes = [k for k, v in count.items() if v == max_count]
        
        if len(modes) == len(data):
            return "📊 ฐานนิยม (Mode): ไม่มี (ทุกค่ามีความถี่เท่ากัน)"
        elif len(modes) == 1:
            mode = modes[0]
            return f"📊 ฐานนิยม (Mode): {mode:.4f}" if mode != int(mode) else f"📊 ฐานนิยม (Mode): {int(mode)}"
        else:
            modes_str = ", ".join([f"{m:.4f}" if m != int(m) else str(int(m)) for m in modes])
            return f"📊 ฐานนิยม (Mode): {modes_str} (มีหลายค่า)"
    
    def _calculate_variance(self, data: List[float]) -> str:
        """คำนวณความแปรปรวน"""
        if not data:
            return "Error: No data provided"
        if len(data) < 2:
            return "Error: Need at least 2 data points for variance"
        
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)  # Sample variance
        
        return f"📊 ความแปรปรวน (Variance): {variance:.4f}" if variance != int(variance) else f"📊 ความแปรปรวน (Variance): {int(variance)}"
    
    def _calculate_std(self, data: List[float]) -> str:
        """คำนวณส่วนเบี่ยงเบนมาตรฐาน"""
        if not data:
            return "Error: No data provided"
        if len(data) < 2:
            return "Error: Need at least 2 data points for std dev"
        
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
        std_dev = math.sqrt(variance)
        
        return f"📊 ส่วนเบี่ยงเบนมาตรฐาน (Std Dev): {std_dev:.4f}" if std_dev != int(std_dev) else f"📊 ส่วนเบี่ยงเบนมาตรฐาน (Std Dev): {int(std_dev)}"
    
    def _calculate_min(self, data: List[float]) -> str:
        """คำนวณค่าต่ำสุด"""
        if not data:
            return "Error: No data provided"
        min_val = min(data)
        return f"📊 ค่าต่ำสุด (Min): {min_val:.4f}" if min_val != int(min_val) else f"📊 ค่าต่ำสุด (Min): {int(min_val)}"
    
    def _calculate_max(self, data: List[float]) -> str:
        """คำนวณค่าสูงสุด"""
        if not data:
            return "Error: No data provided"
        max_val = max(data)
        return f"📊 ค่าสูงสุด (Max): {max_val:.4f}" if max_val != int(max_val) else f"📊 ค่าสูงสุด (Max): {int(max_val)}"
    
    def _calculate_range(self, data: List[float]) -> str:
        """คำนวณพิสัย"""
        if not data:
            return "Error: No data provided"
        range_val = max(data) - min(data)
        return f"📊 พิสัย (Range): {range_val:.4f}" if range_val != int(range_val) else f"📊 พิสัย (Range): {int(range_val)}"


# ทดสอบการทำงาน
if __name__ == "__main__":
    engine = StatisticsEngine()
    
    test_cases = [
        {"action": "all", "data": [1, 2, 3, 4, 5, 5, 6, 7, 8, 9]},
        {"action": "mean", "data": [10, 20, 30, 40, 50]},
        {"action": "median", "data": [1, 3, 3, 6, 7, 8, 9]},
        {"action": "mode", "data": [1, 2, 2, 3, 4, 4, 4, 5]},
        {"action": "std", "data": [2, 4, 4, 4, 5, 5, 7, 9]},
        {"action": "ค่าเฉลี่ย", "data": "15, 25, 35, 45, 55"},
    ]
    
    print("=" * 80)
    print("=== STATISTICS ENGINE TEST ===")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}] Action: {test['action']}, Data: {test['data']}")
        print("-" * 80)
        result = engine.execute(test)
        if result.get('statistic_type') == 'all':
            for stat_type, stat_result in result['response'].items():
                print(f"  {stat_result}")
        else:
            print(f"  {result['response']}")
        print()
