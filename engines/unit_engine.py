# Unit Engine - แปลงหน่วยวัด พร้อมรองรับหลายขั้นตอนและลำดับความสำคัญ
from typing import Dict, Any, List
from .base_engine import BaseEngine

class UnitEngine(BaseEngine):
    def __init__(self):
        super().__init__(name="unit", version="2.1")
    
    def execute(self, params: Dict[str, Any]) -> str:
        value = params.get("value")
        from_unit = params.get("from", "").lower()
        to_unit = params.get("to", "").lower()
        conversions = params.get("conversions", [])
        sequences = params.get("sequences", [])
        priority = params.get("priority", "medium")
        
        # กรณีมีหลายการแปลง (Multi-step Conversions)
        if conversions:
            return self._execute_multi_conversions(conversions, sequences, priority)
        
        if value is None or not from_unit or not to_unit:
            return "Error: Please provide 'value', 'from', and 'to' units."
        
        try:
            result = self._convert_single(value, from_unit, to_unit)
            return f"{result} (Priority: {priority})"
            
        except Exception as e:
            return f"Unit Conversion Error: {str(e)}"
    
    def _convert_single(self, value, from_unit, to_unit) -> str:
        """แปลงหน่วยเดี่ยว"""
        # แปลงชื่อหน่วยภาษาไทยและอังกฤษแบบเต็มเป็นตัวย่อ
        th_to_en_units = {
            'เมตร': 'm', 'กิโลเมตร': 'km', 'เซนติเมตร': 'cm', 'มิลลิเมตร': 'mm',
            'ฟุต': 'ft', 'นิ้ว': 'in',
            'กิโลกรัม': 'kg', 'กรัม': 'g', 'ปอนด์': 'lb', 'ออนซ์': 'oz',
            'เซลเซียส': 'c', 'ฟาเรนไฮต์': 'f', 'เคลวิน': 'k',
            'ลิตร': 'l', 'มิลลิลิตร': 'ml', 'แกลลอน': 'gal',
            'วินาที': 's', 'นาที': 'min', 'ชั่วโมง': 'h',
            'องศาเซลเซียส': 'c', 'องศาฟาเรนไฮต์': 'f',
            # อังกฤษแบบเต็ม
            'celsius': 'c', 'fahrenheit': 'f', 'kelvin': 'k',
            'meter': 'm', 'kilometer': 'km', 'centimeter': 'cm', 'millimeter': 'mm',
            'foot': 'ft', 'feet': 'ft', 'inch': 'in', 'inches': 'in',
            'kilogram': 'kg', 'gram': 'g', 'pound': 'lb', 'ounce': 'oz',
            'liter': 'l', 'milliliter': 'ml', 'gallon': 'gal',
            'second': 's', 'minute': 'min', 'hour': 'h',
            # หน่วยวิศวกรรม - ไทย
            'นิวตัน': 'N', 'กิโลนิวตัน': 'kN', 'ปอนด์แรง': 'lbf', 'ไดน์': 'dyne',
            'ปาสคาล': 'Pa', 'กิโลปาสคาล': 'kPa', 'บาร์': 'bar', 'บรรยากาศ': 'atm',
            'เมตรต่อวินาที': 'm/s', 'กิโลเมตรต่อชั่วโมง': 'km/h', 'ฟุตต่อวินาที': 'ft/s',
            'ไมล์ต่อชั่วโมง': 'mph', 'นอต': 'knot',
            # หน่วยวิศวกรรม - อังกฤษ
            'newton': 'N', 'kilonewton': 'kN', 'pound-force': 'lbf', 'dyne': 'dyne',
            'pascal': 'Pa', 'kilopascal': 'kPa', 'bar': 'bar', 'atmosphere': 'atm',
            'meter per second': 'm/s', 'kilometer per hour': 'km/h', 'foot per second': 'ft/s',
            'mile per hour': 'mph', 'knot': 'knot',
        }
        
        # แปลงหน่วยถ้าเป็นภาษาไทยหรืออังกฤษแบบเต็ม (ทำให้เป็นตัวพิมพ์เล็กก่อน)
        from_unit_lower = from_unit.lower()
        to_unit_lower = to_unit.lower()
        from_unit = th_to_en_units.get(from_unit_lower, from_unit)
        to_unit = th_to_en_units.get(to_unit_lower, to_unit)
        
        # กรณีพิเศษ: ถ้ายังไม่ได้แปลง ให้ลองเช็ค case-sensitive (สำหรับ N, Pa, etc.)
        if from_unit.lower() == 'n' and from_unit != 'N':
            from_unit = 'N'
        if to_unit.lower() == 'n' and to_unit != 'N':
            to_unit = 'N'
        if from_unit.lower() == 'kn' and from_unit != 'kN':
            from_unit = 'kN'
        if to_unit.lower() == 'kn' and to_unit != 'kN':
            to_unit = 'kN'
        if from_unit.lower() == 'pa' and from_unit != 'Pa':
            from_unit = 'Pa'
        if to_unit.lower() == 'pa' and to_unit != 'Pa':
            to_unit = 'Pa'
        if from_unit.lower() == 'kpa' and from_unit != 'kPa':
            from_unit = 'kPa'
        if to_unit.lower() == 'kpa' and to_unit != 'kPa':
            to_unit = 'kPa'
        
        # ตารางแปลงหน่วยพื้นฐาน
        conversions = {
            # ความยาว (เมตร เป็น ฐาน)
            ('m', 'km'): lambda x: x / 1000,
            ('km', 'm'): lambda x: x * 1000,
            ('m', 'cm'): lambda x: x * 100,
            ('cm', 'm'): lambda x: x / 100,
            ('m', 'mm'): lambda x: x * 1000,
            ('mm', 'm'): lambda x: x / 1000,
            ('m', 'ft'): lambda x: x * 3.28084,
            ('ft', 'm'): lambda x: x / 3.28084,
            ('m', 'in'): lambda x: x * 39.3701,
            ('in', 'm'): lambda x: x / 39.3701,
            
            # น้ำหนัก (กิโลกรัม เป็น ฐาน)
            ('kg', 'g'): lambda x: x * 1000,
            ('g', 'kg'): lambda x: x / 1000,
            ('kg', 'lb'): lambda x: x * 2.20462,
            ('lb', 'kg'): lambda x: x / 2.20462,
            ('kg', 'oz'): lambda x: x * 35.274,
            ('oz', 'kg'): lambda x: x / 35.274,
            
            # อุณหภูมิ (เซลเซียส เป็น ฐาน)
            ('c', 'f'): lambda x: (x * 9/5) + 32,
            ('f', 'c'): lambda x: (x - 32) * 5/9,
            ('c', 'k'): lambda x: x + 273.15,
            ('k', 'c'): lambda x: x - 273.15,
            
            # ปริมาตร (ลิตร เป็น ฐาน)
            ('l', 'ml'): lambda x: x * 1000,
            ('ml', 'l'): lambda x: x / 1000,
            ('l', 'gal'): lambda x: x * 0.264172,
            ('gal', 'l'): lambda x: x / 0.264172,
            
            # เวลา (วินาที เป็น ฐาน)
            ('s', 'min'): lambda x: x / 60,
            ('min', 's'): lambda x: x * 60,
            ('min', 'h'): lambda x: x / 60,
            ('h', 'min'): lambda x: x * 60,
            ('h', 's'): lambda x: x * 3600,
            ('s', 'h'): lambda x: x / 3600,
            
            # แรง (นิวตัน เป็น ฐาน)
            ('N', 'kN'): lambda x: x / 1000,
            ('kN', 'N'): lambda x: x * 1000,
            ('N', 'lbf'): lambda x: x * 0.224809,
            ('lbf', 'N'): lambda x: x / 0.224809,
            ('N', 'dyne'): lambda x: x * 100000,
            ('dyne', 'N'): lambda x: x / 100000,
            
            # ความดัน (ปาสคาล เป็น ฐาน)
            ('Pa', 'kPa'): lambda x: x / 1000,
            ('kPa', 'Pa'): lambda x: x * 1000,
            ('Pa', 'bar'): lambda x: x / 100000,
            ('bar', 'Pa'): lambda x: x * 100000,
            ('Pa', 'psi'): lambda x: x * 0.000145038,
            ('psi', 'Pa'): lambda x: x / 0.000145038,
            ('Pa', 'atm'): lambda x: x / 101325,
            ('atm', 'Pa'): lambda x: x * 101325,
            ('bar', 'psi'): lambda x: x * 14.5038,
            ('psi', 'bar'): lambda x: x / 14.5038,
            ('kPa', 'bar'): lambda x: x / 100,
            ('bar', 'kPa'): lambda x: x * 100,
            
            # ความเร็ว (เมตร/วินาที เป็น ฐาน)
            ('m/s', 'km/h'): lambda x: x * 3.6,
            ('km/h', 'm/s'): lambda x: x / 3.6,
            ('m/s', 'ft/s'): lambda x: x * 3.28084,
            ('ft/s', 'm/s'): lambda x: x / 3.28084,
            ('m/s', 'mph'): lambda x: x * 2.23694,
            ('mph', 'm/s'): lambda x: x / 2.23694,
            ('km/h', 'mph'): lambda x: x * 0.621371,
            ('mph', 'km/h'): lambda x: x / 0.621371,
            ('knot', 'm/s'): lambda x: x * 0.514444,
            ('m/s', 'knot'): lambda x: x / 0.514444,
        }
        
        # ตารางหน่วยวิศวกรรมเพิ่มเติม (aliases)
        engineering_aliases = {
            # แรง
            'newton': 'N', 'นิวตัน': 'N',
            'kilonewton': 'kN', 'กิโลนิวตัน': 'kN',
            'pound-force': 'lbf', 'ปอนด์แรง': 'lbf',
            'dyne': 'dyne', 'ไดน์': 'dyne',
            
            # ความดัน
            'pascal': 'Pa', 'ปาสคาล': 'Pa',
            'kilopascal': 'kPa', 'กิโลปาสคาล': 'kPa',
            'bar': 'bar', 'บาร์': 'bar',
            'psi': 'psi',
            'atmosphere': 'atm', 'บรรยากาศ': 'atm',
            
            # ความเร็ว
            'meter per second': 'm/s', 'เมตรต่อวินาที': 'm/s',
            'kilometer per hour': 'km/h', 'กิโลเมตรต่อชั่วโมง': 'km/h',
            'foot per second': 'ft/s', 'ฟุตต่อวินาที': 'ft/s',
            'mile per hour': 'mph', 'ไมล์ต่อชั่วโมง': 'mph',
            'knot': 'knot', 'นอต': 'knot',
        }
        
        # แปลง aliases
        from_unit = engineering_aliases.get(from_unit, from_unit)
        to_unit = engineering_aliases.get(to_unit, to_unit)
        
        # หาฟังก์ชันแปลงหน่วย
        key = (from_unit, to_unit)
        if key in conversions:
            result = conversions[key](float(value))
            # ปัดเศษถ้าเป็นจำนวนเต็ม
            if result == int(result):
                result = int(result)
            else:
                result = round(result, 6)
            return f"📏 {value} {from_unit} = {result} {to_unit}"
        
        # กรณีหน่วยเดียวกัน
        if from_unit == to_unit:
            return f"📏 {value} {from_unit} = {value} {to_unit} (same unit)"
        
        return f"⚠️ Conversion from '{from_unit}' to '{to_unit}' is not supported yet.\nSupported: m, km, cm, mm, ft, in, kg, g, lb, oz, c, f, k, l, ml, gal, s, min, h, N, kN, lbf, Pa, kPa, bar, psi, atm, m/s, km/h, mph, knot"
    
    def _execute_multi_conversions(self, conversions: List[Dict], sequences: List[Dict], priority: str) -> str:
        """ประมวลผลหลายการแปลงตามลำดับ"""
        results = []
        
        # เรียงลำดับตาม sequences ถ้ามี
        if sequences:
            ordered_conversions = []
            for seq in sorted(sequences, key=lambda x: x.get('step_number', 0)):
                step_idx = seq.get('step_number', 0) - 1
                if 0 <= step_idx < len(conversions):
                    ordered_conversions.append(conversions[step_idx])
            # เพิ่มที่เหลือ
            for conv in conversions:
                if conv not in ordered_conversions:
                    ordered_conversions.append(conv)
            conversions = ordered_conversions
        
        # ทำการแปลงแต่ละตัว
        for i, conv in enumerate(conversions, 1):
            value = conv.get('value')
            from_unit = conv.get('from', '')
            to_unit = conv.get('to', '')
            
            if value is None or not from_unit or not to_unit:
                results.append(f"Step {i}: Error - Missing parameters")
                continue
            
            try:
                result = self._convert_single(value, from_unit, to_unit)
                # เอาเฉพาะผลลัพธ์ ไม่เอา priority
                result_text = result.split('(Priority')[0].strip()
                results.append(f"Step {i}: {result_text}")
            except Exception as e:
                results.append(f"Step {i}: Error - {str(e)}")
        
        return f"📏 Multi-step Unit Conversion (Priority: {priority}):\n" + "\n".join(results)
