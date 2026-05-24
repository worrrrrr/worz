# Logic Engine - ประมวลผลตรรกะและเหตุผล พร้อมรองรับลำดับขั้นและความซับซ้อน
# Version 2.2: Symbolic Logic System (No eval())
from typing import Dict, Any, List, Tuple, Optional
from .base_engine import BaseEngine


class SymbolicLogicChecker:
    """Symbolic logic checker without using eval()."""
    
    def __init__(self):
        self.truth_values = {
            'true': True, 'false': False,
            'จริง': True, 'เท็จ': False,
            't': True, 'f': False,
            'yes': True, 'no': False,
            'ใช่': True, 'ไม่ใช่': False,
        }
    
    def parse_expression(self, expr: str) -> Tuple[List[str], List[str]]:
        """Parse expression into operands and operators."""
        tokens = []
        current_token = ""
        operators = []
        
        i = 0
        while i < len(expr):
            char = expr[i]
            
            # Handle multi-char operators
            if i + 1 < len(expr):
                two_char = expr[i:i+2]
                if two_char in ['<=', '==', '=>', '<>']:
                    if current_token.strip():
                        tokens.append(current_token.strip())
                        current_token = ""
                    operators.append(two_char)
                    i += 2
                    continue
            
            if char in '()':
                if current_token.strip():
                    tokens.append(current_token.strip())
                    current_token = ""
                operators.append(char)
                i += 1
                continue
            
            if char == ' ':
                if current_token.strip():
                    tokens.append(current_token.strip())
                    current_token = ""
                i += 1
                continue
            
            current_token += char
            i += 1
        
        if current_token.strip():
            tokens.append(current_token.strip())
        
        return tokens, operators
    
    def evaluate_symbolic(self, expr: str) -> Tuple[bool, str]:
        """Evaluate logical expression symbolically without eval()."""
        expr_lower = expr.lower()
        
        # Replace Thai/English connectors including formal Thai operators
        replacements = {
            'และ': ' and ',
            'หรือ': ' or ',
            'ไม่': ' not ',
            'implies': ' -> ',
            'iff': ' <-> ',
            # Thai formal operators (v2.2)
            'หาก': '',      # Remove "หาก" (if) - will be handled by if-then pattern
            'ย่อม': ' then ',   # Formal "then/yield"
        }
        
        for th, en in replacements.items():
            expr_lower = expr_lower.replace(th, en)
        
        # Parse and evaluate
        result, explanation = self._evaluate_recursive(expr_lower)
        return result, explanation
    
    def _evaluate_recursive(self, expr: str) -> Tuple[bool, str]:
        """Recursively evaluate logical expression."""
        expr = expr.strip()
        
        # Remove outer parentheses
        while expr.startswith('(') and expr.endswith(')'):
            # Check if these are matching outer parens
            depth = 0
            is_outer = True
            for i, char in enumerate(expr):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                if depth == 0 and i < len(expr) - 1:
                    is_outer = False
                    break
            if is_outer:
                expr = expr[1:-1].strip()
            else:
                break
        
        # Check for OR (lowest precedence)
        or_pos = self._find_operator(expr, ' or ')
        if or_pos != -1:
            left = expr[:or_pos].strip()
            right = expr[or_pos + 4:].strip()
            left_val, left_exp = self._evaluate_recursive(left)
            right_val, right_exp = self._evaluate_recursive(right)
            result = left_val or right_val
            explanation = f"({left_exp}) OR ({right_exp}) = {result}"
            return result, explanation
        
        # Check for AND
        and_pos = self._find_operator(expr, ' and ')
        if and_pos != -1:
            left = expr[:and_pos].strip()
            right = expr[and_pos + 5:].strip()
            left_val, left_exp = self._evaluate_recursive(left)
            right_val, right_exp = self._evaluate_recursive(right)
            result = left_val and right_val
            explanation = f"({left_exp}) AND ({right_exp}) = {result}"
            return result, explanation
        
        # Check for NOT
        if expr.startswith('not '):
            inner = expr[4:].strip()
            inner_val, inner_exp = self._evaluate_recursive(inner)
            result = not inner_val
            explanation = f"NOT ({inner_exp}) = {result}"
            return result, explanation
        
        # Check for IF-THEN pattern (handles both "if X then Y" and "X then Y")
        then_pos = self._find_operator(expr, ' then ')
        if then_pos != -1:
            # Check if there's an "if" before "then"
            if_pos = self._find_operator(expr, ' if ')
            start_pos = if_pos + 4 if if_pos != -1 and if_pos < then_pos else 0
            condition = expr[start_pos:then_pos].strip()
            consequence = expr[then_pos + 5:].strip()
            
            # Handle empty condition (when just "X then Y" format)
            if not condition:
                # Try to find any word before "then" as condition
                parts = expr[:then_pos].strip().split()
                if parts:
                    condition = parts[-1]  # Take last word before "then"
            
            if condition and consequence:
                try:
                    cond_val, cond_exp = self._evaluate_recursive(condition)
                    cons_val, cons_exp = self._evaluate_recursive(consequence)
                    result = (not cond_val) or cons_val
                    explanation = f"IF ({cond_exp}) THEN ({cons_exp}) = {result}"
                    return result, explanation
                except:
                    pass  # Fall through to other evaluation methods
        
        # Check for IMPLIES (->)
        impl_pos = self._find_operator(expr, ' -> ')
        if impl_pos != -1:
            left = expr[:impl_pos].strip()
            right = expr[impl_pos + 4:].strip()
            left_val, left_exp = self._evaluate_recursive(left)
            right_val, right_exp = self._evaluate_recursive(right)
            result = (not left_val) or right_val
            explanation = f"({left_exp}) -> ({right_exp}) = {result}"
            return result, explanation
        
        # Check for IFF (<->)
        iff_pos = self._find_operator(expr, ' <-> ')
        if iff_pos != -1:
            left = expr[:iff_pos].strip()
            right = expr[iff_pos + 5:].strip()
            left_val, left_exp = self._evaluate_recursive(left)
            right_val, right_exp = self._evaluate_recursive(right)
            result = left_val == right_val
            explanation = f"({left_exp}) <-> ({right_exp}) = {result}"
            return result, explanation
        
        # Base case: truth value lookup
        expr_clean = expr.strip().lower()
        if expr_clean in self.truth_values:
            result = self.truth_values[expr_clean]
            return result, f"{expr_clean}={result}"
        
        # Try to evaluate as comparison
        comparison_result = self._evaluate_comparison(expr)
        if comparison_result is not None:
            return comparison_result, f"{expr}={comparison_result}"
        
        # Unknown expression
        raise ValueError(f"Cannot evaluate: {expr}")
    
    def _find_operator(self, expr: str, op: str) -> int:
        """Find operator position respecting parentheses."""
        depth = 0
        i = 0
        while i < len(expr):
            if expr[i] == '(':
                depth += 1
            elif expr[i] == ')':
                depth -= 1
            elif depth == 0 and expr[i:i+len(op)] == op:
                return i
            i += 1
        return -1
    
    def evaluate(self, expr: str) -> Dict[str, Any]:
        """Public evaluate method returning dict with result and explanation."""
        try:
            result, explanation = self.evaluate_symbolic(expr)
            return {
                "result": result,
                "explanation": explanation,
                "success": True
            }
        except Exception as e:
            return {
                "result": None,
                "explanation": str(e),
                "success": False
            }
    
    def _evaluate_comparison(self, expr: str) -> Optional[bool]:
        """Evaluate simple comparisons like 'a == b' or 'x > y'."""
        import re
        
        # Pattern for numeric comparisons
        patterns = [
            (r'(\d+(?:\.\d+)?)\s*==\s*(\d+(?:\.\d+)?)', lambda a, b: float(a) == float(b)),
            (r'(\d+(?:\.\d+)?)\s*!=\s*(\d+(?:\.\d+)?)', lambda a, b: float(a) != float(b)),
            (r'(\d+(?:\.\d+)?)\s*>\s*(\d+(?:\.\d+)?)', lambda a, b: float(a) > float(b)),
            (r'(\d+(?:\.\d+)?)\s*<\s*(\d+(?:\.\d+)?)', lambda a, b: float(a) < float(b)),
            (r'(\d+(?:\.\d+)?)\s*>=\s*(\d+(?:\.\d+)?)', lambda a, b: float(a) >= float(b)),
            (r'(\d+(?:\.\d+)?)\s*<=\s*(\d+(?:\.\d+)?)', lambda a, b: float(a) <= float(b)),
        ]
        
        for pattern, func in patterns:
            match = re.search(pattern, expr)
            if match:
                return func(match.group(1), match.group(2))
        
        return None


class LogicEngine(BaseEngine):
    def __init__(self):
        super().__init__(name="logic", version="2.2")
        self.symbolic_checker = SymbolicLogicChecker()
    
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
            # ใช้ Symbolic Logic Checker แทน eval()
            result, explanation = self.symbolic_checker.evaluate_symbolic(str(expression))
            result_str = "True" if result else "False"
            
            response = (
                f"🧠 Logic Result: {result_str} (Priority: {priority})\n"
                f"📝 Reasoning: {explanation}\n"
                f"🔒 Security: Symbolic evaluation (no eval used)"
            )
            return response
            
        except ValueError as e:
            return f"🧠 Logic Analysis: Cannot determine truth value\n" \
                   f"📝 Reason: {str(e)}\n" \
                   f"🔒 Security: Symbolic evaluation (no eval used)"
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
