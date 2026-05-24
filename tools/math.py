# =============================================================================
# Symbolic AI Engine - ระบบ AI เชิงสัญลักษณ์แบบครบวงจร
# ผู้พัฒนา: วอ (สร้างเอง ไม่พึ่งพาโมเดลภายนอก)
# =============================================================================

from math import sin as _sin, cos as _cos, exp as _exp, log as _log, pi, e
import itertools

# =============================================================================
# ส่วนที่ 1: ระบบคณิตศาสตร์ (Mathematical Expression System)
# =============================================================================

class Expr:
    """คลาสพื้นฐาน - รองรับ Operator Overloading ให้เขียนสูตรได้เหมือนมนุษย์"""
    def __add__(self, o): return Add(self, _e(o))
    def __radd__(self, o): return Add(_e(o), self)
    def __sub__(self, o): return Sub(self, _e(o))
    def __rsub__(self, o): return Sub(_e(o), self)
    def __mul__(self, o): return Mul(self, _e(o))
    def __rmul__(self, o): return Mul(_e(o), self)
    def __truediv__(self, o): return Div(self, _e(o))
    def __rtruediv__(self, o): return Div(_e(o), self)
    def __pow__(self, o): return Pow(self, _e(o))
    def __neg__(self): return Neg(self)

def _e(x):
    """แปลงค่าทั่วไปเป็น Expr"""
    if isinstance(x, Expr): return x
    if isinstance(x, (int, float)): return Num(x)
    if isinstance(x, str): return Var(x)
    raise TypeError(f"แปลง {type(x)} ไม่ได้")


class Num(Expr):
    def __init__(self, v): self.v = v
    def __str__(self): return str(int(self.v)) if isinstance(self.v, float) and self.v.is_integer() else str(self.v)
    def evaluate(self, env=None): return self.v
    def diff(self, var): return Num(0)
    def simplify(self): return self
    def is_zero(self): return self.v == 0
    def is_one(self): return self.v == 1
    def is_const(self): return True


class Var(Expr):
    def __init__(self, name): self.name = name
    def __str__(self): return self.name
    def evaluate(self, env=None):
        if env and self.name in env: return env[self.name]
        raise ValueError(f"ตัวแปร '{self.name}' ไม่มีค่า")
    def diff(self, var): return Num(1) if self.name == var else Num(0)
    def simplify(self): return self
    def is_const(self): return False


class Neg(Expr):
    def __init__(self, x): self.x = _e(x)
    def __str__(self): return f"-{self.x}"
    def evaluate(self, env=None): return -self.x.evaluate(env)
    def diff(self, var): return Neg(self.x.diff(var))
    def simplify(self):
        x = self.x.simplify()
        if isinstance(x, Num): return Num(-x.v)
        if isinstance(x, Neg): return x.x
        return Neg(x)


class Add(Expr):
    def __init__(self, l, r): self.l, self.r = _e(l), _e(r)
    def __str__(self): return f"({self.l} + {self.r})"
    def evaluate(self, env=None): return self.l.evaluate(env) + self.r.evaluate(env)
    def diff(self, var):
        # กฎผลบวก: (u+v)' = u' + v'
        return Add(self.l.diff(var), self.r.diff(var))
    def simplify(self):
        l, r = self.l.simplify(), self.r.simplify()
        if isinstance(l, Num) and l.is_zero(): return r
        if isinstance(r, Num) and r.is_zero(): return l
        if isinstance(l, Num) and isinstance(r, Num): return Num(l.v + r.v)
        return Add(l, r)


class Sub(Expr):
    def __init__(self, l, r): self.l, self.r = _e(l), _e(r)
    def __str__(self): return f"({self.l} - {self.r})"
    def evaluate(self, env=None): return self.l.evaluate(env) - self.r.evaluate(env)
    def diff(self, var): return Sub(self.l.diff(var), self.r.diff(var))
    def simplify(self):
        l, r = self.l.simplify(), self.r.simplify()
        if isinstance(r, Num) and r.is_zero(): return l
        if isinstance(l, Num) and isinstance(r, Num): return Num(l.v - r.v)
        return Sub(l, r)


class Mul(Expr):
    def __init__(self, l, r): self.l, self.r = _e(l), _e(r)
    def __str__(self): return f"({self.l}*{self.r})"
    def evaluate(self, env=None): return self.l.evaluate(env) * self.r.evaluate(env)
    def diff(self, var):
        # กฎผลคูณ: (uv)' = u'v + uv'
        return Add(Mul(self.l.diff(var), self.r), Mul(self.l, self.r.diff(var)))
    def simplify(self):
        l, r = self.l.simplify(), self.r.simplify()
        if isinstance(l, Num) and l.is_zero(): return Num(0)
        if isinstance(r, Num) and r.is_zero(): return Num(0)
        if isinstance(l, Num) and l.is_one(): return r
        if isinstance(r, Num) and r.is_one(): return l
        if isinstance(l, Num) and isinstance(r, Num): return Num(l.v * r.v)
        return Mul(l, r)


class Div(Expr):
    def __init__(self, l, r): self.l, self.r = _e(l), _e(r)
    def __str__(self): return f"({self.l}/{self.r})"
    def evaluate(self, env=None): return self.l.evaluate(env) / self.r.evaluate(env)
    def diff(self, var):
        # กฎผลหาร: (u/v)' = (u'v - uv') / v^2
        u, v = self.l, self.r
        return Div(Sub(Mul(u.diff(var), v), Mul(u, v.diff(var))), Pow(v, Num(2)))
    def simplify(self):
        l, r = self.l.simplify(), self.r.simplify()
        if isinstance(l, Num) and l.is_zero(): return Num(0)
        if isinstance(r, Num) and r.is_one(): return l
        if isinstance(l, Num) and isinstance(r, Num): return Num(l.v / r.v)
        return Div(l, r)


class Pow(Expr):
    def __init__(self, b, e): self.b, self.e = _e(b), _e(e)
    def __str__(self): return f"({self.b}^{self.e})"
    def evaluate(self, env=None): return self.b.evaluate(env) ** self.e.evaluate(env)
    def diff(self, var):
        # กฎยกกำลัง + กฎลูกโซ่
        if self.e.is_const():
            return Mul(Mul(self.e, Pow(self.b, Sub(self.e, Num(1)))), self.b.diff(var))
        # d/dx(u^v) = u^v * (v'*ln(u) + v*u'/u)
        return Mul(self, Add(Mul(self.e.diff(var), Log(self.b)),
                              Mul(self.e, Div(self.b.diff(var), self.b))))
    def simplify(self):
        b, ex = self.b.simplify(), self.e.simplify()
        if isinstance(ex, Num) and ex.v == 0: return Num(1)
        if isinstance(ex, Num) and ex.is_one(): return b
        if isinstance(b, Num) and isinstance(ex, Num): return Num(b.v ** ex.v)
        return Pow(b, ex)


class Log(Expr):
    def __init__(self, x): self.x = _e(x)
    def __str__(self): return f"ln({self.x})"
    def evaluate(self, env=None): return _log(self.x.evaluate(env))
    def diff(self, var): return Div(self.x.diff(var), self.x)  # (ln u)' = u'/u
    def simplify(self):
        x = self.x.simplify()
        if isinstance(x, Num) and x.v == 1: return Num(0)
        return Log(x)


class Sin(Expr):
    def __init__(self, x): self.x = _e(x)
    def __str__(self): return f"sin({self.x})"
    def evaluate(self, env=None): return _sin(self.x.evaluate(env))
    def diff(self, var): return Mul(Cos(self.x), self.x.diff(var))  # (sin u)' = cos(u)*u'
    def simplify(self):
        x = self.x.simplify()
        if isinstance(x, Num) and x.v == 0: return Num(0)
        return Sin(x)


class Cos(Expr):
    def __init__(self, x): self.x = _e(x)
    def __str__(self): return f"cos({self.x})"
    def evaluate(self, env=None): return _cos(self.x.evaluate(env))
    def diff(self, var): return Neg(Mul(Sin(self.x), self.x.diff(var)))
    def simplify(self):
        x = self.x.simplify()
        if isinstance(x, Num) and x.v == 0: return Num(1)
        return Cos(x)


class Exp(Expr):
    def __init__(self, x): self.x = _e(x)
    def __str__(self): return f"e^({self.x})"
    def evaluate(self, env=None): return _exp(self.x.evaluate(env))
    def diff(self, var): return Mul(Exp(self.x), self.x.diff(var))
    def simplify(self):
        x = self.x.simplify()
        if isinstance(x, Num) and x.v == 0: return Num(1)
        return Exp(x)


# =============================================================================
# ส่วนที่ 2: ระบบตรรกศาสตร์ (Logic System)
# =============================================================================

class LogicExpr:
    def __and__(self, o): return And(self, o)
    def __or__(self, o): return Or(self, o)
    def __invert__(self): return Not(self)


class Prop(LogicExpr):
    def __init__(self, name): self.name = name
    def __str__(self): return self.name
    def evaluate(self, env=None):
        if env and self.name in env: return env[self.name]
        raise ValueError(f"ประพจน์ '{self.name}' ไม่มีค่า")
    def variables(self): return {self.name}


class Not(LogicExpr):
    def __init__(self, x): self.x = x
    def __str__(self): return f"¬{self.x}"
    def evaluate(self, env=None): return not self.x.evaluate(env)
    def variables(self): return self.x.variables()


class And(LogicExpr):
    def __init__(self, l, r): self.l, self.r = l, r
    def __str__(self): return f"({self.l} ∧ {self.r})"
    def evaluate(self, env=None): return self.l.evaluate(env) and self.r.evaluate(env)
    def variables(self): return self.l.variables() | self.r.variables()


class Or(LogicExpr):
    def __init__(self, l, r): self.l, self.r = l, r
    def __str__(self): return f"({self.l} ∨ {self.r})"
    def evaluate(self, env=None): return self.l.evaluate(env) or self.r.evaluate(env)
    def variables(self): return self.l.variables() | self.r.variables()


class Implies(LogicExpr):
    """ถ้า...แล้ว... (P → Q)"""
    def __init__(self, l, r): self.l, self.r = l, r
    def __str__(self): return f"({self.l} → {self.r})"
    def evaluate(self, env=None): return (not self.l.evaluate(env)) or self.r.evaluate(env)
    def variables(self): return self.l.variables() | self.r.variables()


class Iff(LogicExpr):
    """ก็ต่อเมื่อ (P ↔ Q)"""
    def __init__(self, l, r): self.l, self.r = l, r
    def __str__(self): return f"({self.l} ↔ {self.r})"
    def evaluate(self, env=None): return self.l.evaluate(env) == self.r.evaluate(env)
    def variables(self): return self.l.variables() | self.r.variables()


# =============================================================================
# ส่วนที่ 3: กลไกการให้เหตุผล (Reasoning Engine)
# =============================================================================

def truth_table(expr):
    vars_list = sorted(expr.variables())
    rows = []
    for vals in itertools.product([True, False], repeat=len(vars_list)):
        env = dict(zip(vars_list, vals))
        rows.append((env, expr.evaluate(env)))
    return vars_list, rows


def is_tautology(expr):
    return all(r for _, r in truth_table(expr)[1])


def is_contradiction(expr):
    return all(not r for _, r in truth_table(expr)[1])


def logical_equivalent(a, b):
    return is_tautology(Iff(a, b))


def extract_poly_coeffs(expr, var):
    """ดึงสัมประสิทธิ์พหุนาม ax² + bx + c โดยแทนค่า 3 จุด"""
    try:
        y0 = expr.evaluate({var: 0})
        y1 = expr.evaluate({var: 1})
        y_1 = expr.evaluate({var: -1})
        c = y0
        a = (y1 + y_1) / 2 - c
        b = (y1 - y_1) / 2
        return a, b, c
    except:
        return None


# =============================================================================
# ส่วนที่ 4: AI Reasoner (สมองหลัก)
# =============================================================================

class AIReasoner:
    def step(self, desc, expr=None):
        return f"  → {desc}" + (f"  :  {expr}" if expr else "")

    def differentiate(self, expr, var):
        print(f"\n[โจทย์] จงหา d/d{var} ของ {expr}")
        print(self.step("วิเคราะห์โครงสร้างสมการ"))
        self._explain(expr)
        raw = expr.diff(var)
        print(self.step("ผลลัพธ์ก่อนจัดรูป", raw))
        ans = raw.simplify()
        print(self.step("✨ คำตอบหลังจัดรูป", ans))
        return ans

    def _explain(self, expr):
        rules = {
            Add: "กฎผลบวก: (u+v)' = u' + v'",
            Sub: "กฎผลลบ: (u-v)' = u' - v'",
            Mul: "กฎผลคูณ: (u·v)' = u'·v + u·v'",
            Div: "กฎผลหาร: (u/v)' = (u'v - uv')/v²",
            Pow: "กฎยกกำลัง: d/dx(u^n) = n·u^(n-1)·u'",
            Sin: "กฎ sin: d/dx(sin u) = cos(u)·u'",
            Cos: "กฎ cos: d/dx(cos u) = -sin(u)·u'",
            Log: "กฎ ln: d/dx(ln u) = u'/u",
            Exp: "กฎ e^u: d/dx(e^u) = e^u·u'",
        }
        for cls, rule in rules.items():
            if isinstance(expr, cls):
                print(self.step(f"ใช้ {rule}"))
                return

    def solve(self, expr, var):
        print(f"\n[โจทย์] จงแก้สมการ {expr} = 0")
        coeffs = extract_poly_coeffs(expr, var)
        if not coeffs:
            print(self.step("❌ ไม่ใช่พหุนาม แก้ไม่ได้"))
            return
        a, b, c = coeffs
        print(self.step(f"ตรวจพบรูปทั่วไป: {a}·{var}² + {b}·{var} + {c} = 0"))
        if abs(a) < 1e-10:
            ans = -c / b if b != 0 else "ไม่มีคำตอบ"
            print(self.step(f"สมการเชิงเส้น: {var} = -c/b = {ans}"))
        else:
            d = b**2 - 4*a*c
            print(self.step(f"ดิสคริมิแนนท์ Δ = b²-4ac = {d}"))
            if d < 0:
                print(self.step("Δ < 0 → ไม่มีคำตอบเป็นจำนวนจริง"))
                ans = None
            elif d == 0:
                ans = [-b/(2*a)]
                print(self.step(f"Δ = 0 → รากซ้ำ: {var} = {ans[0]}"))
            else:
                sq = d**0.5
                ans = [(-b+sq)/(2*a), (-b-sq)/(2*a)]
                print(self.step(f"Δ > 0 → 2 คำตอบ: {var} = {ans[0]}, {ans[1]}"))
        return ans

    def check_argument(self, premises, conclusion, label=""):
        print(f"\n[โจทย์] ตรวจสอบความสมเหตุสมผล: {label}")
        print(self.step("สมมติฐาน"))
        for i, p in enumerate(premises, 1):
            print(f"    P{i}: {p}")
        print(self.step(f"ข้อสรุป: {conclusion}"))
        combined = premises[0]
        for p in premises[1:]:
            combined = And(combined, p)
        arg = Implies(combined, conclusion)
        if is_tautology(arg):
            print(self.step("✅ สมเหตุสมผล (Valid) - เป็นสัจนิรันดร์"))
            return True
        else:
            print(self.step("❌ ไม่สมเหตุสมผล (Fallacy)"))
            for env, r in truth_table(arg)[1]:
                if not r:
                    print(self.step(f"ตัวอย่างที่ล้มเหลว: {env}"))
                    break
            return False

    def prove_equivalence(self, a, b, label=""):
        print(f"\n[โจทย์] พิสูจน์: {label}")
        print(self.step(f"ฝั่งซ้าย: {a}"))
        print(self.step(f"ฝั่งขวา: {b}"))
        eq = logical_equivalent(a, b)
        if eq:
            print(self.step("✅ สมมูลกันทุกกรณี (Tautology ของ P ↔ Q)"))
        else:
            print(self.step("❌ ไม่สมมูล"))
        return eq


# =============================================================================
# ส่วนที่ 5: ทดสอบด้วยคำถามยาก 9 ข้อ
# =============================================================================

if __name__ == "__main__":
    ai = AIReasoner()
    x = Var('x')

    print("\n" + "="*70)
    print(" 🤖 Symbolic AI Engine - ทดสอบด้วยคำถามยาก 9 ข้อ")
    print("="*70)

    # --- คณิตศาสตร์ ---
    print("\n\n📐 หมวดคณิตศาสตร์")
    print("-"*70)
    ai.differentiate((x**2) * Sin(x), 'x')
    ai.differentiate(Exp(Num(2)*x) + Log(x**2 + 1), 'x')
    ai.differentiate(Sin(x**2), 'x')
    ai.solve(x**2 - 5*x + 6, 'x')
    ai.solve(x**2 + 4, 'x')

    # --- ตรรกศาสตร์ ---
    print("\n\n🧠 หมวดตรรกศาสตร์")
    print("-"*70)
    P, Q, R = Prop("P"), Prop("Q"), Prop("R")

    # Modus Ponens
    ai.check_argument([Implies(P, Q), P], Q,
                      "Modus Ponens: ถ้า P→Q และ P จริง แล้ว Q จริง")

    # Fallacy
    ai.check_argument([Implies(P, Q), Q], P,
                      "Fallacy: ถ้า P→Q และ Q จริง แล้ว P จริง (?)")

    # Modus Tollens
    ai.check_argument([Implies(P, Q), Not(Q)], Not(P),
                      "Modus Tollens: ถ้า P→Q และ ¬Q แล้ว ¬P")

    # กฎ De Morgan
    ai.prove_equivalence(
        Not(Or(P, Q)),
        And(Not(P), Not(Q)),
        "กฎ De Morgan: ¬(P∨Q) ≡ (¬P ∧ ¬Q)"
    )

    # Hypothetical Syllogism
    ai.check_argument(
        [Implies(P, Q), Implies(Q, R)],
        Implies(P, R),
        "Hypothetical Syllogism: P→Q, Q→R ⊢ P→R"
    )