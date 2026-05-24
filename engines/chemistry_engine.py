"""
Chemistry Engine - WORZ SOVEREIGN CORE
รองรับ: สมการเคมี, การคำนวณโมล, ความเข้มข้น, มวลโมเลกุล
Symbolic-only mode (ไม่ใช้ LLM)
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from .base_engine import BaseEngine

class ChemistryEngine(BaseEngine):
    def __init__(self):
        super().__init__(name="chemistry", version="1.0")
        
        # Atomic masses (g/mol) - ข้อมูลพื้นฐาน
        self.atomic_masses = {
            'H': 1.008, 'He': 4.003,
            'Li': 6.941, 'Be': 9.012, 'B': 10.81, 'C': 12.01, 'N': 14.01, 'O': 16.00,
            'F': 19.00, 'Ne': 20.18,
            'Na': 22.99, 'Mg': 24.31, 'Al': 26.98, 'Si': 28.09, 'P': 30.97, 'S': 32.07,
            'Cl': 35.45, 'Ar': 39.95,
            'K': 39.10, 'Ca': 40.08, 'Fe': 55.85, 'Cu': 63.55, 'Zn': 65.38,
            'Br': 79.90, 'Ag': 107.87, 'I': 126.90, 'Au': 196.97, 'Hg': 200.59,
            'Pb': 207.2, 'U': 238.03
        }
        
        # Common compounds pre-calculated
        self.compound_masses = {
            'H2O': 18.015,
            'CO2': 44.01,
            'NaCl': 58.44,
            'H2SO4': 98.08,
            'HCl': 36.46,
            'NaOH': 40.00,
            'CH4': 16.04,
            'C6H12O6': 180.16,
            'NH3': 17.03,
            'O2': 32.00,
            'N2': 28.02,
            'H2': 2.016
        }
    
    def execute(self, params: Dict[str, Any]) -> str:
        """ประมวลผลคำสั่งทางเคมี"""
        action = params.get("action", "").lower()
        expression = params.get("expression", "")
        values = params.get("values", [])
        
        # ตรวจสอบประเภทคำสั่ง
        if "มวลโมเลกุล" in action or "molecular" in action or "mass" in action:
            return self._calculate_molecular_mass(expression)
        elif "โมล" in action or "mole" in action:
            return self._calculate_moles(params)
        elif "ความเข้มข้น" in action or "concentration" in action or "molarity" in action:
            return self._calculate_concentration(params)
        elif "สมดุล" in action or "balance" in action or "สมการ" in action:
            return self._balance_equation(expression)
        elif "stoich" in action or "ปริมาณสาร" in action:
            return self._stoichiometry(params)
        else:
            # พยายามวิเคราะห์จาก expression
            return self._auto_detect(expression, params)
    
    def _parse_formula(self, formula: str) -> Dict[str, int]:
        """แยกสูตรเคมีเป็นธาตุและจำนวนอะตอม"""
        formula = formula.strip()
        elements = {}
        
        # Pattern สำหรับจับธาตุและจำนวน (เช่น H2, O, C6)
        pattern = r'([A-Z][a-z]?)(\d*)'
        matches = re.findall(pattern, formula)
        
        for element, count in matches:
            if element:
                count = int(count) if count else 1
                elements[element] = elements.get(element, 0) + count
        
        return elements
    
    def _calculate_molecular_mass(self, formula: str) -> str:
        """คำนวณมวลโมเลกุลจากสูตรเคมี"""
        formula = formula.strip()
        
        # ตรวจสอบว่ามีใน cache หรือไม่
        if formula in self.compound_masses:
            return f"🧪 มวลโมเลกุลของ {formula} = {self.compound_masses[formula]:.3f} g/mol (pre-calculated)"
        
        # คำนวณจาก atomic masses
        try:
            elements = self._parse_formula(formula)
            total_mass = 0.0
            
            for element, count in elements.items():
                if element in self.atomic_masses:
                    total_mass += self.atomic_masses[element] * count
                else:
                    return f"⚠️ ไม่พบข้อมูลมวลอะตอมของธาตุ '{element}'"
            
            # Save to cache
            self.compound_masses[formula] = total_mass
            
            detail = " + ".join([f"{elem}×{count}({self.atomic_masses.get(elem, 0):.3f})" 
                               for elem, count in elements.items()])
            return f"🧪 มวลโมเลกุลของ {formula} = {total_mass:.3f} g/mol\n   รายละเอียด: {detail}"
        except Exception as e:
            return f"❌ เกิดข้อผิดพลาดในการคำนวณมวลโมเลกุล: {e}"
    
    def _calculate_moles(self, params: Dict[str, Any]) -> str:
        """คำนวณจำนวนโมล"""
        mass = params.get("mass", params.get("grams", None))
        molar_mass = params.get("molar_mass", None)
        formula = params.get("formula", None)
        volume = params.get("volume", None)
        molarity = params.get("molarity", None)
        
        try:
            # กรณีที่ 1: รู้มวลและมวลโมเลกุล
            if mass is not None and molar_mass is not None:
                moles = float(mass) / float(molar_mass)
                return f"🧪 จำนวนโมล = {moles:.4f} mol\n   สูตร: n = m/M = {mass}g / {molar_mass}g/mol"
            
            # กรณีที่ 2: รู้มวลและสูตรเคมี (คำนวณมวลโมเลกุลเอง)
            if mass is not None and formula is not None:
                result = self._calculate_molecular_mass(formula)
                if "=" in result:
                    molar_mass = float(result.split("=")[1].split()[0])
                    moles = float(mass) / molar_mass
                    return f"🧪 จำนวนโมล = {moles:.4f} mol\n   จากมวล {mass}g ของ {formula} (M={molar_mass:.3f} g/mol)"
                return result
            
            # กรณีที่ 3: รู้ปริมาตรและความเข้มข้น (สำหรับสารละลาย)
            if volume is not None and molarity is not None:
                volume_l = float(volume) / 1000 if float(volume) > 1 else float(volume)  # แปลง mL → L ถ้าจำเป็น
                moles = float(molarity) * volume_l
                return f"🧪 จำนวนโมล = {moles:.4f} mol\n   สูตร: n = M×V = {molarity} mol/L × {volume_l} L"
            
            return "⚠️ กรุณาระบุข้อมูลให้ครบถ้วน (มวล+มวลโมเลกุล, หรือ มวล+สูตรเคมี, หรือ ปริมาตร+ความเข้มข้น)"
        except Exception as e:
            return f"❌ เกิดข้อผิดพลาดในการคำนวณโมล: {e}"
    
    def _calculate_concentration(self, params: Dict[str, Any]) -> str:
        """คำนวณความเข้มข้นโมลาร์ (Molarity)"""
        moles = params.get("moles", None)
        volume = params.get("volume", None)
        mass = params.get("mass", None)
        formula = params.get("formula", None)
        
        try:
            # คำนวณโมลก่อนถ้ามีมวล
            if moles is None and mass is not None and formula is not None:
                mole_result = self._calculate_moles({"mass": mass, "formula": formula})
                if "=" in mole_result:
                    moles = float(mole_result.split("=")[1].split()[0])
                else:
                    return mole_result
            
            if moles is None or volume is None:
                return "⚠️ กรุณาระบุจำนวนโมลและปริมาตร (หรือ มวล+สูตรเคมี และปริมาตร)"
            
            # แปลงปริมาตรเป็นลิตร
            volume_l = float(volume) / 1000 if float(volume) > 1 else float(volume)
            molarity = float(moles) / volume_l
            
            return f"🧪 ความเข้มข้นโมลาร์ = {molarity:.4f} M\n   สูตร: M = n/V = {moles} mol / {volume_l} L"
        except Exception as e:
            return f"❌ เกิดข้อผิดพลาดในการคำนวณความเข้มข้น: {e}"
    
    def _balance_equation(self, equation: str) -> str:
        """ดุลสมการเคมี (แบบง่าย)"""
        equation = equation.strip().replace("→", "->").replace("=", "->")
        
        # แยก reactants และ products
        if "->" not in equation:
            return "⚠️ รูปแบบสมการไม่ถูกต้อง ใช้ -> หรือ → คั่นระหว่างสารตั้งต้นและผลิตภัณฑ์"
        
        parts = equation.split("->")
        if len(parts) != 2:
            return "⚠️ สมการควรมีด้านซ้ายและขวาเท่านั้น"
        
        reactants = [r.strip() for r in parts[0].split("+")]
        products = [p.strip() for p in parts[1].split("+")]
        
        # วิเคราะห์ธาตุในแต่ละด้าน (แบบง่าย - นับจำนวนอะตอม)
        def count_elements(compounds: List[str]) -> Dict[str, int]:
            total = {}
            for compound in compounds:
                # ละเว้น coefficient ชั่วคราว
                formula = re.sub(r'^\d+', '', compound)
                elements = self._parse_formula(formula)
                for elem, count in elements.items():
                    total[elem] = total.get(elem, 0) + count
            return total
        
        left_elements = count_elements(reactants)
        right_elements = count_elements(products)
        
        # ตรวจสอบว่าดุลแล้วหรือไม่
        is_balanced = left_elements == right_elements
        
        result = []
        result.append(f"📝 สมการ: {equation}")
        result.append(f"\nด้านซ้าย (Reactants): {' + '.join(reactants)}")
        result.append(f"   ธาตุ: {left_elements}")
        result.append(f"\nด้านขวา (Products): {' + '.join(products)}")
        result.append(f"   ธาตุ: {right_elements}")
        
        if is_balanced:
            result.append("\n✅ สมการดุลแล้ว!")
        else:
            result.append("\n⚠️ สมการยังไม่ได้ดุล")
            result.append("   หมายเหตุ: การดุลสมการที่ซับซ้อนต้องการอัลกอริทึมขั้นสูง")
        
        return "\n".join(result)
    
    def _stoichiometry(self, params: Dict[str, Any]) -> str:
        """คำนวณปริมาณสารสัมพันธ์ (Stoichiometry)"""
        # ตัวอย่าง: จากสมการ 2H2 + O2 -> 2H2O
        # ถ้ามี H2 10 กรัม จะได้ H2O กี่กรัม?
        
        given_mass = params.get("given_mass", None)
        given_formula = params.get("given_formula", None)
        target_formula = params.get("target_formula", None)
        equation = params.get("equation", None)
        
        if not all([given_mass, given_formula, target_formula]):
            return "⚠️ กรุณาระบุ: given_mass, given_formula, target_formula และ equation (ถ้ามี)"
        
        # คำนวณมวลโมเลกุลของสารที่กำหนด
        given_molar_mass_result = self._calculate_molecular_mass(given_formula)
        if "=" not in given_molar_mass_result:
            return given_molar_mass_result
        given_molar_mass = float(given_molar_mass_result.split("=")[1].split()[0])
        
        # คำนวณมวลโมเลกุลของสารเป้าหมาย
        target_molar_mass_result = self._calculate_molecular_mass(target_formula)
        if "=" not in target_molar_mass_result:
            return target_molar_mass_result
        target_molar_mass = float(target_molar_mass_result.split("=")[1].split()[0])
        
        # คำนวณโมลของสารที่กำหนด
        given_moles = float(given_mass) / given_molar_mass
        
        # อัตราส่วนโมล (สมมติ 1:1 ถ้าไม่มีสมการ)
        # ในอนาคตสามารถ parse สมการเพื่อหาอัตราส่วนที่แท้จริง
        mole_ratio = 1.0  # Default
        
        target_moles = given_moles * mole_ratio
        target_mass = target_moles * target_molar_mass
        
        result = []
        result.append(f"📊 การคำนวณปริมาณสารสัมพันธ์:")
        result.append(f"   สารตั้งต้น: {given_mass}g ของ {given_formula} ({given_molar_mass:.3f} g/mol)")
        result.append(f"   = {given_moles:.4f} mol")
        result.append(f"\n   สารเป้าหมาย: {target_formula} ({target_molar_mass:.3f} g/mol)")
        result.append(f"   อัตราส่วนโมล: {mole_ratio}")
        result.append(f"   = {target_moles:.4f} mol")
        result.append(f"\n   ✅ มวลของ {target_formula} ที่ได้ = {target_mass:.3f} g")
        
        return "\n".join(result)
    
    def _auto_detect(self, expression: str, params: Dict[str, Any]) -> str:
        """พยายามตรวจจับประเภทคำสั่งอัตโนมัติ"""
        expression_lower = expression.lower()
        
        # ตรวจสอบ keywords
        if any(kw in expression_lower for kw in ['h2o', 'co2', 'nacl', 'h2so4']):
            # น่าจะถามถึงมวลโมเลกุล
            # แยกสูตรเคมีออกมา
            formulas = re.findall(r'[A-Z][a-z]?\d*', expression)
            if formulas:
                results = []
                for f in formulas:
                    results.append(self._calculate_molecular_mass(f))
                return "\n\n".join(results)
        
        # Default
        return "🧪 Chemistry Engine พร้อมใช้งาน\nคำสั่งที่รองรับ:\n- คำนวณมวลโมเลกุล: 'มวลโมเลกุลของ H2O'\n- คำนวณโมล: 'โมลของ 10g NaCl'\n- ความเข้มข้น: 'ความเข้มข้นของ 0.5 mol ใน 500 mL'\n- ดุลสมการ: 'ดุล H2 + O2 -> H2O'"
