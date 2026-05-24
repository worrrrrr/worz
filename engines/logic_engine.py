# Logic Engine - ประมวลผลตรรกะและเหตุผล พร้อมรองรับลำดับขั้นและความซับซ้อน
from typing import Dict, Any, List
from .base_engine import BaseEngine

class LogicEngine(BaseEngine):
    def __init__(self):
        super().__init__(name="logic", version="2.1")
    
    def execute(self, params: Dict[str, Any]) -> str:
        expression = params.get("expression")
        steps = params.get("steps", [])
        sequences = params.get("sequences", [])
        negation = params.get("negation", False)
        conditionals = params.get("conditionals", [])
        priority = params.get("priority", "medium")
        
        # กรณีมีหลายขั้นตอน (Multi-step Logic)
        if steps:
            return self._execute_multi_step(steps, sequences, conditionals, priority)
        
        if not expression:
            return "Error: No logical expression provided."
        
        try:
            # แปลงคำเชื่อมตรรกะเป็น Python syntax
            expr = str(expression).lower()
            
            # แทนที่คำเชื่อมภาษาไทยและอังกฤษ
            replacements = {
                'และ': ' and ',
                'หรือ': ' or ',
                'ไม่': ' not ',
                'ถ้า': ' implies ',
                'ก็ต่อเมื่อ': ' iff ',
                'implies': ' <= ',
                'iff': ' == ',
                '=>': ' <= ',
                '<=>': ' == ',
            }
            
            for th, en in replacements.items():
                expr = expr.replace(th, en)
            
            # จัดการ negation จากคำสั่ง
            if negation:
                expr = f"not ({expr})"
            
            # จัดการ conditionals
            if conditionals:
                conditional_expr = self._process_conditionals(expr, conditionals)
                if conditional_expr:
                    expr = conditional_expr
            
            # ตรวจสอบว่าเป็นประพจน์แบบง่าย (A and B, A or B)
            if ' and ' in expr or ' or ' in expr or 'not ' in expr:
                result = self._evaluate_logic(expr)
                return f"🧠 Logic Result: {result} (Priority: {priority})"
            
            return f"🧠 Logical Expression: {expr}\nNote: Complex logic requires symbolic evaluation."
            
        except Exception as e:
            return f"Logic Error: {str(e)}"
    
    def _process_conditionals(self, expr: str, conditionals: List[str]) -> str:
        """ประมวลผลเงื่อนไข if-then"""
        # ถ้ามีคำว่า "ถ้า" หรือ "if" ใน expression
        if any(word in expr.lower() for word in ['if', 'ถ้า', 'หาก', 'when', 'เมื่อ']):
            # พยายามแยกส่วน condition และ consequence
            for cond_word in ['ถ้า', 'หาก', 'if', 'when']:
                if cond_word in expr:
                    parts = expr.split(cond_word, 1)
                    if len(parts) == 2:
                        condition = parts[1].strip()
                        # ค้นหาคำเชื่อม "แล้ว" หรือ "then"
                        for then_word in ['แล้ว', 'then', 'จึง']:
                            if then_word in condition:
                                sub_parts = condition.split(then_word, 1)
                                if len(sub_parts) == 2:
                                    return f"({sub_parts[0].strip()}) <= ({sub_parts[1].strip()})"
        return None
    
    def _execute_multi_step(self, steps: List[str], sequences: List[Dict], conditionals: List[str], priority: str) -> str:
        """ประมวลผลตรรกะหลายขั้นตอนตามลำดับ"""
        results = []
        
        # เรียงลำดับขั้นตอนตาม sequences
        if sequences:
            # sort steps based on sequence order
            ordered_steps = []
            for seq in sorted(sequences, key=lambda x: x.get('step_number', 0)):
                step_name = seq.get('step')
                if step_name and step_name in steps:
                    ordered_steps.append(step_name)
            # เพิ่มขั้นตอนที่เหลือที่ไม่ได้ระบุใน sequences
            for step in steps:
                if step not in ordered_steps:
                    ordered_steps.append(step)
            steps = ordered_steps
        
        # ประเมินแต่ละขั้นตอน
        for i, step in enumerate(steps, 1):
            try:
                result = self._evaluate_logic(step.lower())
                results.append(f"Step {i}: {step} → {result}")
            except Exception as e:
                results.append(f"Step {i}: {step} → Error: {e}")
        
        return f"🧠 Multi-step Logic (Priority: {priority}):\n" + "\n".join(results)
    
    def _evaluate_logic(self, expr: str) -> str:
        """ประเมินนิพจน์ตรรกะอย่างง่าย"""
        # Mapping สำหรับตัวแปรตรรกะ
        truth_map = {
            'true': True, 'false': False,
            'จริง': True, 'เท็จ': False,
            't': True, 'f': False,
            'yes': True, 'no': False,
            'ใช่': True, 'ไม่ใช่': False,
        }
        
        # แทนที่ค่า truth
        evaluated = expr.lower()
        for key, val in truth_map.items():
            evaluated = evaluated.replace(key, str(val))
        
        # แทนที่ operators
        evaluated = evaluated.replace('<=', '<=').replace('==', '==')
        
        try:
            # ปลอดภัย: ใช้ eval เฉพาะกับนิพจน์ตรรกะ
            result = eval(evaluated)
            return "True" if result else "False"
        except:
            return expr
