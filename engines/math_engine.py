import sympy
from typing import Any, Dict, List
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
from .base_engine import BaseEngine

class MathEngine(BaseEngine):
    def __init__(self):
        super().__init__(name="math", version="2.1")
    
    def execute(self, params: Dict[str, Any]) -> str:
        expr = params.get("expression") or next(iter(params.values()), None)
        steps = params.get("steps", [])
        sequences = params.get("sequences", [])
        priority = params.get("priority", "medium")
        
        # กรณีมีหลายขั้นตอน (Multi-step Math)
        if steps:
            return self._execute_multi_step(steps, sequences, priority)
        
        if not expr: 
            return "Error: No valid expression."
        
        try:
            trans = (standard_transformations + (implicit_multiplication_application, convert_xor))
            expr_str = str(expr)
            
            # ลบคำเชื่อมที่ไม่ใช่คณิตศาสตร์ออก (เช่น &&, and, but)
            import re
            expr_str = re.sub(r'\s+and\s+', ',', expr_str, flags=re.IGNORECASE)
            expr_str = re.sub(r'\s+but\s+', ',', expr_str, flags=re.IGNORECASE)
            expr_str = re.sub(r'\s+then\s+', ',', expr_str, flags=re.IGNORECASE)
            expr_str = re.sub(r'\s+next\s+', ',', expr_str, flags=re.IGNORECASE)
            expr_str = expr_str.replace('&&', ',').replace('||', ',')
            
            # ถ้ามีหลายนิพจน์ คำนวณทีละตัว
            if ',' in expr_str:
                parts = [p.strip() for p in expr_str.split(',') if p.strip()]
                results = []
                for i, part in enumerate(parts, 1):
                    try:
                        res = parse_expr(part, transformations=trans).evalf()
                        final = round(float(res), 10)
                        results.append(int(final) if final % 1 == 0 else final)
                    except Exception as e:
                        results.append(f"Error: {part}")
                
                if sequences:
                    # แสดงผลตามลำดับขั้น
                    output = []
                    for seq in sorted(sequences, key=lambda x: x.get('step_number', 0)):
                        step_num = seq.get('step_number', 0)
                        if step_num <= len(results):
                            output.append(f"Step {step_num}: {results[step_num-1]}")
                    return f"📊 Sequential Results (Priority: {priority}):\n" + "\n".join(output)
                
                return f"📊 Results: {results}"
            
            if "=" in expr_str:
                parts = expr_str.split("=")
                eqs = [sympy.Eq(parse_expr(parts[i], transformations=trans), parse_expr(parts[i+1], transformations=trans)) for i in range(len(parts)-1)]
                sol = sympy.solve(eqs)
                return f"🌟 Solution: {sol}"
            
            res = parse_expr(expr_str, transformations=trans).evalf()
            final = round(float(res), 10)
            return f"Result: {int(final) if final % 1 == 0 else final} (Priority: {priority})"
        except Exception as e:
            return f"Math Error: {e}"
    
    def _execute_multi_step(self, steps: List[str], sequences: List[Dict], priority: str) -> str:
        """ประมวลผลคณิตศาสตร์หลายขั้นตอนตามลำดับ"""
        results = []
        
        # เรียงลำดับขั้นตอนตาม sequences
        if sequences:
            ordered_steps = []
            for seq in sorted(sequences, key=lambda x: x.get('step_number', 0)):
                step_name = seq.get('step')
                if step_name and step_name in steps:
                    ordered_steps.append(step_name)
            for step in steps:
                if step not in ordered_steps:
                    ordered_steps.append(step)
            steps = ordered_steps
        
        trans = (standard_transformations + (implicit_multiplication_application, convert_xor))
        
        # ประเมินแต่ละขั้นตอน
        for i, step in enumerate(steps, 1):
            try:
                expr_str = str(step)
                # ทำความสะอาดนิพจน์
                import re
                expr_str = re.sub(r'\s+', '', expr_str)
                res = parse_expr(expr_str, transformations=trans).evalf()
                final = round(float(res), 10)
                result_val = int(final) if final % 1 == 0 else final
                results.append(f"Step {i}: {step} = {result_val}")
            except Exception as e:
                results.append(f"Step {i}: {step} → Error: {e}")
        
        return f"📊 Multi-step Math (Priority: {priority}):\n" + "\n".join(results)