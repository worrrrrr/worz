import sympy
from typing import Any, Dict
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

class MathEngine:
    def execute(self, params: Dict[str, Any]) -> str:
        expr = params.get("expression") or next(iter(params.values()), None)
        if not expr: return "Error: No valid expression."
        
        try:
            trans = (standard_transformations + (implicit_multiplication_application, convert_xor))
            if "=" in str(expr):
                parts = str(expr).split("=")
                eqs = [sympy.Eq(parse_expr(parts[i], transformations=trans), parse_expr(parts[i+1], transformations=trans)) for i in range(len(parts)-1)]
                sol = sympy.solve(eqs)
                return f"🌟 Solution: {sol}"
            
            res = parse_expr(str(expr), transformations=trans).evalf()
            final = round(float(res), 10)
            return f"Result: {int(final) if final % 1 == 0 else final}"
        except Exception as e:
            return f"Math Error: {e}"