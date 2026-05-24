"""
Pipeline Connector - เชื่อมต่อ Intent Parser กับ Router
รองรับ Multi-step Commands, Negation Handling, และ Sequential Execution
Version 1.0: Symbolic-only (No LLM)
"""

import json
from typing import Dict, Any, List, Optional
from core.intent_parser import RuleBasedIntentParser
from core.router import Router


class PipelineConnector:
    """เชื่อมต่อ Intent Parser กับ Router สำหรับประมวลผลคำสั่งหลายขั้นตอน"""
    
    def __init__(self):
        self.parser = RuleBasedIntentParser()
        self.router = Router()
        
        # Mapping จาก action types ไปยัง engine tools
        self.action_to_tool_map = {
            'calculate': 'math_engine',
            'convert': 'unit_engine',
            'check': 'logic_engine',
            'compare': 'logic_engine',
            'list': 'general_engine',
            'define': 'general_engine',
            'explain': 'general_engine',
            'statistics': 'statistics_engine',
            'stat': 'statistics_engine',
            'ค่าเฉลี่ย': 'statistics_engine',
            'มัธยฐาน': 'statistics_engine',
            'ฐานนิยม': 'statistics_engine',
            'มวลโมเลกุล': 'chemistry_engine',
            'โมล': 'chemistry_engine',
            'ความเข้มข้น': 'chemistry_engine',
            'ดุลสมการ': 'chemistry_engine',
            'ดอกเบี้ย': 'finance_engine',
            'ผ่อน': 'finance_engine',
            'roi': 'finance_engine',
            'npv': 'finance_engine',
            'จุดคุ้มทุน': 'finance_engine',
        }
    
    def _map_action_to_tool(self, actions: List[str]) -> str:
        """แปลง action types เป็น tool ที่เหมาะสม"""
        for action in actions:
            if action in self.action_to_tool_map:
                return self.action_to_tool_map[action]
        return 'general_engine'
    
    def _extract_numeric_values(self, text: str) -> List[float]:
        """สกัดค่าตัวเลขจากข้อความ"""
        import re
        pattern = r'(\d+(?:\.\d+)?)'
        matches = re.findall(pattern, text)
        return [float(m) for m in matches]
    
    def _build_math_expression(self, text: str) -> Optional[str]:
        """สร้างนิพจน์คณิตศาสตร์จากข้อความ"""
        import re
        
        # Pattern: ตัวเลข การดำเนินการ ตัวเลข
        math_pattern = r'(\d+(?:\.\d+)?)\s*(บวก|ลบ|คูณ|หาร|plus|minus|times|divide|\+|-|\*|/)\s*(\d+(?:\.\d+)?)'
        matches = re.findall(math_pattern, text, re.IGNORECASE)
        
        if not matches:
            return None
        
        op_map = {
            'บวก': '+', 'plus': '+', 'add': '+', '+': '+',
            'ลบ': '-', 'minus': '-', 'subtract': '-', '-': '-',
            'คูณ': '*', 'times': '*', 'multiply': '*', '*': '*',
            'หาร': '/', 'divide': '/', '/': '/',
        }
        
        expressions = []
        for num1, op, num2 in matches:
            op_symbol = op_map.get(op.lower(), op)
            expressions.append(f'{num1} {op_symbol} {num2}')
        
        return ' and '.join(expressions) if expressions else None
    
    def _build_convert_params(self, text: str, units: List[Dict]) -> Optional[Dict]:
        """สร้าง parameters สำหรับการแปลงหน่วย"""
        if not units:
            return None
        
        # ใช้ unit แรกที่พบ
        unit = units[0]
        value = float(unit['value'])
        from_unit = unit['unit']
        unit_type = unit['type']
        
        # หา target unit จากข้อความ (ถ้ามี)
        # ดูว่ามีหน่วยอื่นในประโยคที่ไม่ใช่ from_unit ไหม
        import re
        
        # สร้าง list ของหน่วยทั้งหมดที่อาจเป็น target
        all_units = {
            'เมตร': 'm', 'กิโลเมตร': 'km', 'เซนติเมตร': 'cm', 'มิลลิเมตร': 'mm', 
            'นิ้ว': 'in', 'ฟุต': 'ft', 'หลา': 'yd', 'ไมล์': 'mile',
            'กิโลกรัม': 'kg', 'กรัม': 'g', 'ปอนด์': 'lb', 'ออนซ์': 'oz', 'ตัน': 'ton',
            'เซลเซียส': 'c', 'ฟาเรนไฮต์': 'f', 'เคลวิน': 'k',
            'ลิตร': 'l', 'มิลลิลิตร': 'ml', 'แกลลอน': 'gal',
        }
        
        to_unit = None
        text_lower = text.lower()
        
        # ค้นหาหน่วยที่เป็นไปได้ในข้อความ - หาคำว่า "เป็น X" หรือ "to X"
        pattern = r'เป็น\s*(\S+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            potential_unit = match.group(1).strip()
            # ตรวจสอบว่าเป็นหน่วยที่รู้จักหรือไม่
            for th_unit, en_unit in all_units.items():
                if th_unit == potential_unit or potential_unit in th_unit or th_unit in potential_unit:
                    to_unit = th_unit
                    break
            # ถ้าไม่เจอในไทย ลองเช็คภาษาอังกฤษ
            if not to_unit:
                for en_unit in ['m', 'km', 'cm', 'mm', 'in', 'ft', 'kg', 'g', 'lb', 'oz', 'c', 'f', 'k', 'l', 'ml', 'gal']:
                    if en_unit == potential_unit.lower():
                        to_unit = en_unit
                        break
        
        # ถ้ายังไม่เจอ ให้ค้นหาหน่วยอื่นๆ ในประโยค
        if not to_unit:
            for th_unit, en_unit in all_units.items():
                if th_unit in text_lower and th_unit != from_unit and th_unit != unit.get('original_text', ''):
                    to_unit = th_unit
                    break
        
        # ถ้ายังไม่เจอ ให้ใช้หน่วยที่พบบ่อยตาม type
        if not to_unit:
            common_targets = {
                'length': 'เมตร',
                'weight': 'กิโลกรัม',
                'temperature': 'เซลเซียส',
            }
            to_unit = common_targets.get(unit_type, 'เมตร')
        
        return {
            'value': value,
            'from': from_unit,
            'to': to_unit,
            'unit_type': unit_type
        }
    
    def _process_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """ประมวลผลแต่ละขั้นตอน"""
        step_text = step['text']
        actions = step.get('actions', [])
        negation = step.get('negation', {})
        units = step.get('units', [])
        
        # ตรวจสอบ negation
        if negation.get('active', False):
            return {
                'status': 'skipped',
                'reason': f"Negation detected: {negation.get('words', [])}",
                'step_number': step.get('step_number', 0)
            }
        
        # กำหนด tool จาก actions และ context
        tool = self._map_action_to_tool(actions)
        
        # ถ้าไม่มี action ที่ชัดเจน ให้วิเคราะห์จากข้อความ
        if tool == 'general_engine':
            import re
            step_text_lower = step_text.lower()
            
            # ตรวจสอบว่าเป็นการคำนวณหรือไม่
            math_keywords = ['คำนวณ', 'หา', 'บวก', 'ลบ', 'คูณ', 'หาร', 'plus', 'minus', 'times', 'divide', 'force', 'แรง']
            if any(kw in step_text_lower for kw in math_keywords):
                tool = 'math_engine'
            
            # ตรวจสอบว่าเป็นการแปลงหน่วยหรือไม่
            convert_keywords = ['แปลง', 'convert', 'เป็น', 'to']
            if any(kw in step_text_lower for kw in convert_keywords) and units:
                tool = 'unit_engine'
            
            # ตรวจสอบว่าเป็นสถิติหรือไม่
            stat_keywords = ['ค่าเฉลี่ย', 'มัธยฐาน', 'ฐานนิยม', 'ส่วนเบี่ยงเบน', 'ความแปรปรวน', 'สถิติ', 'statistics', 'mean', 'median', 'mode', 'std', 'variance']
            if any(kw in step_text_lower for kw in stat_keywords):
                tool = 'statistics_engine'
            
            # ตรวจสอบว่าเป็นเคมีหรือไม่
            chem_keywords = ['มวลโมเลกุล', 'โมล', 'ความเข้มข้น', 'ดุลสมการ', 'เคมี', 'molecular', 'mole', 'concentration', 'balance']
            if any(kw in step_text_lower for kw in chem_keywords):
                tool = 'chemistry_engine'
            
            # ตรวจสอบว่าเป็นการเงินหรือไม่
            finance_keywords = ['ดอกเบี้ย', 'ผ่อน', 'roi', 'npv', 'จุดคุ้มทุน', 'finance', 'interest', 'loan', 'return']
            if any(kw in step_text_lower for kw in finance_keywords):
                tool = 'finance_engine'
        
        # สร้าง params ตาม type ของงาน
        params = {}
        
        if tool == 'math_engine':
            math_expr = self._build_math_expression(step_text)
            if math_expr:
                params = {'expression': math_expr}
            else:
                # พยายามสกัดตัวเลขและดำเนินการ
                numbers = self._extract_numeric_values(step_text)
                
                # ตรวจสอบว่าเป็นคำสั่งสถิติหรือไม่ (ถ้ามีคำว่า ค่าเฉลี่ย, สถิติ)
                step_text_lower = step_text.lower()
                stat_keywords = ['ค่าเฉลี่ย', 'มัธยฐาน', 'ฐานนิยม', 'สถิติ', 'mean', 'median', 'mode', 'average']
                if any(kw in step_text_lower for kw in stat_keywords):
                    tool = 'statistics_engine'
                    params = {'action': 'all', 'data': numbers}
                elif len(numbers) >= 2:
                    if 'บวก' in step_text or 'plus' in step_text.lower():
                        params = {'expression': f'{numbers[0]} + {numbers[1]}'}
                    elif 'ลบ' in step_text or 'minus' in step_text.lower():
                        params = {'expression': f'{numbers[0]} - {numbers[1]}'}
                    elif 'คูณ' in step_text or 'times' in step_text.lower():
                        params = {'expression': f'{numbers[0]} * {numbers[1]}'}
                    elif 'หาร' in step_text or 'divide' in step_text.lower():
                        params = {'expression': f'{numbers[0]} / {numbers[1]}'}
                    elif 'แรง' in step_text or 'force' in step_text.lower():
                        # F = m * a
                        params = {'expression': f'{numbers[0]} * {numbers[1]}'}
        
        elif tool == 'unit_engine':
            convert_params = self._build_convert_params(step_text, units)
            if convert_params:
                params = convert_params
        
        elif tool == 'logic_engine':
            params = {'statement': step_text}
        
        elif tool == 'statistics_engine':
            # สกัดตัวเลขจากข้อความสำหรับสถิติ
            numbers = self._extract_numeric_values(step_text)
            if numbers:
                params = {'action': 'all', 'data': numbers}
            else:
                params = {'action': 'all', 'data': []}
        
        elif tool == 'chemistry_engine':
            # สกัดข้อมูลสำหรับเคมี
            import re
            # พยายามสกัดสูตรเคมี (เช่น H2O, CO2, NaCl) - ปรับปรุง pattern
            # Pattern ใหม่: จับตัวพิมพ์ใหญ่ ตามด้วยตัวพิมพ์เล็ก (ถ้ามี) ตามด้วยตัวเลข (ถ้ามี) และทำซ้ำ
            formula_pattern = r'([A-Z][a-z]?\d*[A-Z]?[a-z]?\d*[A-Z]?[a-z]?\d*)'
            all_matches = re.findall(r'[A-Z][a-z]?\d*', step_text)
            
            # รวม matches ที่ติดกันเป็นสูตรเดียว
            formulas = []
            current_formula = ""
            last_end = 0
            
            for match in re.finditer(r'[A-Z][a-z]?\d*', step_text):
                if match.start() == last_end or current_formula == "":
                    # ต่อเนื่องกับอันก่อนหน้า
                    current_formula += match.group()
                else:
                    # ไม่ต่อเนื่อง เก็บอันเก่าเริ่มใหม่
                    if current_formula and len(current_formula) > 1:
                        formulas.append(current_formula)
                    current_formula = match.group()
                last_end = match.end()
            
            if current_formula and len(current_formula) > 1:
                formulas.append(current_formula)
            
            # ถ้าไม่เจอสูตรที่ซับซ้อน ใช้ list เดิม
            if not formulas and all_matches:
                formulas = all_matches
            
            numbers = self._extract_numeric_values(step_text)
            
            step_text_lower = step_text.lower()
            if 'มวลโมเลกุล' in step_text_lower or 'molecular' in step_text_lower or 'mass' in step_text_lower:
                if formulas:
                    params = {'action': 'molecular_mass', 'expression': formulas[0]}
                elif all_matches:
                    params = {'action': 'molecular_mass', 'expression': all_matches[0]}
            elif 'โมล' in step_text_lower or 'mole' in step_text_lower:
                if numbers and (formulas or all_matches):
                    formula_to_use = formulas[0] if formulas else (all_matches[0] if all_matches else None)
                    params = {'action': 'moles', 'mass': numbers[0], 'formula': formula_to_use}
            elif 'ความเข้มข้น' in step_text_lower or 'concentration' in step_text_lower:
                if len(numbers) >= 2:
                    params = {'action': 'concentration', 'moles': numbers[0], 'volume': numbers[1]}
            else:
                params = {'action': 'auto', 'expression': step_text}
        
        elif tool == 'finance_engine':
            # สกัดข้อมูลสำหรับการเงิน
            numbers = self._extract_numeric_values(step_text)
            step_text_lower = step_text.lower()
            
            if 'ดอกเบี้ย' in step_text_lower or 'interest' in step_text_lower:
                if len(numbers) >= 3:
                    params = {'action': 'interest', 'principal': numbers[0], 'rate': numbers[1], 'time': numbers[2]}
                elif len(numbers) >= 2:
                    params = {'action': 'interest', 'principal': numbers[0], 'rate': numbers[1]}
            elif 'ผ่อน' in step_text_lower or 'loan' in step_text_lower:
                if len(numbers) >= 3:
                    params = {'action': 'installment', 'loan': numbers[0], 'rate': numbers[1], 'years': numbers[2]}
            elif 'roi' in step_text_lower:
                if len(numbers) >= 2:
                    params = {'action': 'roi', 'initial': numbers[0], 'final': numbers[1]}
            elif 'npv' in step_text_lower:
                if numbers:
                    params = {'action': 'npv', 'initial': numbers[0], 'cash_flows': numbers[1:]}
            elif 'จุดคุ้มทุน' in step_text_lower or 'break-even' in step_text_lower:
                if len(numbers) >= 3:
                    params = {'action': 'break_even', 'fixed': numbers[0], 'price': numbers[1], 'variable': numbers[2]}
            else:
                params = {'action': 'auto', 'expression': step_text}
        
        elif tool == 'general_engine':
            params = {'action': 'respond', 'content': step_text}
        
        # ส่งไปยัง Router
        intent = {
            'tool': tool,
            'params': params,
            'step_info': {
                'step_number': step.get('step_number', 0),
                'order_hint': step.get('order_hint'),
                'original_text': step_text
            }
        }
        
        result = self.router.dispatch(intent)
        
        return {
            'status': 'completed',
            'step_number': step.get('step_number', 0),
            'tool_used': tool,
            'result': result
        }
    
    def execute(self, user_input: str) -> Dict[str, Any]:
        """
        ประมวลผลคำสั่งผู้ใช้ตั้งแต่ต้นจนจบ
        
        Args:
            user_input: ข้อความคำสั่งจากผู้ใช้
            
        Returns:
            Dictionary containing execution results
        """
        # Parse ด้วย Intent Parser
        parsed = self.parser.parse(user_input)
        
        # ตรวจสอบว่ามีหลายขั้นตอนหรือไม่
        steps = parsed.get('steps', [])
        
        if not steps:
            # คำสั่งเดี่ยว - ประมวลผลทันที
            single_step = {
                'step_number': 1,
                'text': user_input,
                'actions': parsed.get('actions', []),
                'negation': parsed.get('negation', {}),
                'units': parsed.get('units', []),
                'order_hint': None
            }
            steps = [single_step]
        
        # ประมวลผลแต่ละขั้นตอน
        results = []
        for step in steps:
            step_result = self._process_step(step)
            results.append(step_result)
        
        # รวมผลลัพธ์
        return {
            'original_input': user_input,
            'parsed_intent': parsed,
            'execution_results': results,
            'summary': {
                'total_steps': len(steps),
                'completed': sum(1 for r in results if r['status'] == 'completed'),
                'skipped': sum(1 for r in results if r['status'] == 'skipped')
            }
        }
    
    def execute_and_format(self, user_input: str) -> str:
        """
        ประมวลผลและจัดรูปแบบผลลัพธ์เป็นข้อความอ่านง่าย
        
        Args:
            user_input: ข้อความคำสั่งจากผู้ใช้
            
        Returns:
            Formatted string response
        """
        result = self.execute(user_input)
        
        output_lines = []
        output_lines.append(f"📝 **Input:** {result['original_input']}")
        output_lines.append("")
        
        summary = result['summary']
        output_lines.append(f"📊 **Summary:** {summary['completed']}/{summary['total_steps']} steps completed")
        output_lines.append("")
        
        for step_result in result['execution_results']:
            step_num = step_result.get('step_number', 0)
            status = step_result['status']
            
            if status == 'skipped':
                output_lines.append(f"⚠️  **Step {step_num}:** SKIPPED - {step_result['reason']}")
            elif status == 'completed':
                tool = step_result.get('tool_used', 'unknown')
                step_result_data = step_result.get('result', 'No result')
                output_lines.append(f"✅ **Step {step_num}** ({tool}):")
                output_lines.append(f"    Result: {step_result_data}")
            output_lines.append("")
        
        return '\n'.join(output_lines)


# ทดสอบการทำงาน
if __name__ == "__main__":
    connector = PipelineConnector()
    
    test_cases = [
        "คำนวณ 5 บวก 3",
        "ไม่ต้องคำนวณ 5 บวก 3 และ 10 คูณ 2",
        "แปลง 10 กิโลกรัมเป็นปอนด์",
        "ขั้นแรกคำนวณ 2 บวก 2 ถัดไปคูณด้วย 3",
        "หาแรงที่ใช้เคลื่อนมวล 50 กิโลกรัมด้วยความเร่ง 2 m/s²",
        "หาค่าเฉลี่ยของ 10, 20, 30, 40, 50",
        "สถิติ 5, 10, 15, 20, 25, 30",
        # Chemistry tests
        "มวลโมเลกุลของ H2O",
        "โมลของ 10g NaCl",
        # Finance tests
        "ดอกเบี้ย 10000 บาท ที่ 5% 3 ปี",
        "ROI ลงทุน 100000 ได้กลับมา 150000",
    ]
    
    print("=" * 80)
    print("=== PIPELINE CONNECTOR TEST ===")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test}")
        print("-" * 80)
        result = connector.execute_and_format(test)
        print(result)
        print()
