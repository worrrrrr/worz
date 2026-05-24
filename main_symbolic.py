"""
WORZ SOVEREIGN CORE - Pure Symbolic Mode (No LLM)
ความเร็วสูง: ตอบสนองทันทีด้วย Rule-Based Parsing
"""

import re
import json
import math
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

# ==========================================
# 1. KNOWLEDGE BASE (Hardcoded for Speed)
# ==========================================

KNOWLEDGE_BASE = {
    "formulas": {
        "area_circle": {"pattern": r"พื้นที่.*วงกลม.*รัศมี\s*(\d+(?:\.\d+)?)", "func": lambda r: math.pi * float(r)**2, "unit": "ตารางหน่วย"},
        "circumference": {"pattern": r"เส้นรอบวง.*วงกลม.*รัศมี\s*(\d+(?:\.\d+)?)", "func": lambda r: 2 * math.pi * float(r), "unit": "หน่วย"},
        "rectangle_area": {"pattern": r"พื้นที่.*สี่เหลี่ยม.*กว้าง\s*(\d+(?:\.\d+)?).*ยาว\s*(\d+(?:\.\d+)?)", "func": lambda w, l: float(w) * float(l), "unit": "ตารางหน่วย"},
        "triangle_area": {"pattern": r"พื้นที่.*สามเหลี่ยม.*ฐาน\s*(\d+(?:\.\d+)?).*สูง\s*(\d+(?:\.\d+)?)", "func": lambda b, h: 0.5 * float(b) * float(h), "unit": "ตารางหน่วย"},
        "pythagoras": {"pattern": r"หา.*ด้านฉาก.*ด้านประกอบ\s*(\d+(?:\.\d+)?).*และ\s*(\d+(?:\.\d+)?)", "func": lambda a, b: math.sqrt(float(a)**2 + float(b)**2), "unit": "หน่วย"},
    },
    "conversions": {
        "km_to_m": {"pattern": r"(\d+(?:\.\d+)?)\s*(?:กิโลเมตร|km)", "factor": 1000, "target": "เมตร"},
        "m_to_cm": {"pattern": r"(\d+(?:\.\d+)?)\s*(?:เมตร|m)(?!ตร)", "factor": 100, "target": "เซนติเมตร"},
        "kg_to_g": {"pattern": r"(\d+(?:\.\d+)?)\s*(?:กิโลกรัม|kg)", "factor": 1000, "target": "กรัม"},
        "hr_to_min": {"pattern": r"(\d+(?:\.\d+)?)\s*(?:ชั่วโมง|hr|h)", "factor": 60, "target": "นาที"},
    },
    "logic_keywords": {
        "calculate": ["คำนวณ", "หา", "คิด", "เท่ากับ", "result"],
        "convert": ["แปลง", "เปลี่ยน", "เทียบ"],
        "compare": ["เปรียบเทียบ", "มากกว่า", "น้อยกว่า", "เท่ากันไหม"],
        "define": ["คืออะไร", "หมายถึง", "นิยาม"]
    }
}

# ==========================================
# 2. RULE-BASED INTENT PARSER (แทนที่ LLM)
# ==========================================

class SymbolicParser:
    def __init__(self):
        self.commands = []

    def parse(self, text: str) -> Dict[str, Any]:
        """แปลงข้อความธรรมชาติเป็น Command Object"""
        text = text.strip().lower()
        
        # 1. ตรวจสอบการแปลงหน่วย (Conversion)
        for key, rule in KNOWLEDGE_BASE["conversions"].items():
            match = re.search(rule["pattern"], text)
            if match:
                value = float(match.group(1))
                return {
                    "intent": "convert",
                    "engine": "unit",
                    "params": {"value": value, "type": key, "result_unit": rule["target"]}
                }

        # 2. ตรวจสอบสูตรคณิตศาสตร์ (Math Formulas)
        for key, rule in KNOWLEDGE_BASE["formulas"].items():
            match = re.search(rule["pattern"], text)
            if match:
                groups = [float(g) for g in match.groups()]
                return {
                    "intent": "calculate",
                    "engine": "math",
                    "formula": key,
                    "params": {"args": groups}
                }

        # 3. ตรวจสอบคำสั่งพื้นฐาน (Basic Arithmetic)
        # เช่น "12 บวก 5", "100 หาร 4"
        arithmetic_ops = {
            "บวก": "+", "plus": "+", 
            "ลบ": "-", "minus": "-", 
            "คูณ": "*", "times": "*", 
            "หาร": "/", "divided by": "/"
        }
        
        for thai_op, symbol in arithmetic_ops.items():
            pattern = rf"(\d+(?:\.\d+)?)\s*{thai_op}\s*(\d+(?:\.\d+)?)"
            match = re.search(pattern, text)
            if match:
                a, b = float(match.group(1)), float(match.group(2))
                return {
                    "intent": "calculate",
                    "engine": "math",
                    "operation": "basic",
                    "params": {"a": a, "b": b, "op": symbol}
                }

        # 4. ตรวจสอบคำสั่งทั่วไป (Fallback)
        if any(k in text for k in KNOWLEDGE_BASE["logic_keywords"]["define"]):
            return {"intent": "query", "engine": "knowledge", "params": {"query": text}}
            
        if any(k in text for k in KNOWLEDGE_BASE["logic_keywords"]["compare"]):
            return {"intent": "compare", "engine": "logic", "params": {"text": text}}

        # ไม่รู้จัก
        return {"intent": "unknown", "engine": None, "message": "ไม่เข้าใจคำสั่ง ลองใช้ 'พื้นที่วงกลมรัศมี 5' หรือ 'แปลง 5 กิโลเมตร'"}

# ==========================================
# 3. ENGINES (Execution Layer)
# ==========================================

class MathEngine:
    def execute(self, command: Dict) -> str:
        if command.get("formula"):
            func = KNOWLEDGE_BASE["formulas"][command["formula"]]["func"]
            unit = KNOWLEDGE_BASE["formulas"][command["formula"]]["unit"]
            try:
                result = func(*command["params"]["args"])
                return f"✅ ผลลัพธ์: {result:.4f} {unit}"
            except Exception as e:
                return f"❌ เกิดข้อผิดพลาดในการคำนวณ: {e}"
        
        elif command.get("operation") == "basic":
            p = command["params"]
            ops = {"+": "+", "-": "-", "*": "x", "/": "/"}
            op_symbol = ops.get(p["op"], "?")
            try:
                if p["op"] == "/":
                    result = p["a"] / p["b"]
                elif p["op"] == "*":
                    result = p["a"] * p["b"]
                elif p["op"] == "+":
                    result = p["a"] + p["b"]
                else:
                    result = p["a"] - p["b"]
                return f"✅ {p['a']} {op_symbol} {p['b']} = {result}"
            except ZeroDivisionError:
                return "❌ ไม่สามารถหารด้วยศูนย์ได้"

class UnitEngine:
    def execute(self, command: Dict) -> str:
        p = command["params"]
        rule_key = p["type"]
        factor = KNOWLEDGE_BASE["conversions"][rule_key]["factor"]
        target_unit = p["result_unit"]
        
        result = p["value"] * factor
        return f"✅ {p['value']} {rule_key.split('_')[0].upper()} = {result} {target_unit}"

class KnowledgeEngine:
    def execute(self, command: Dict) -> str:
        # Mock knowledge base for demo
        kb = {
            "pi": "π (Pi) คืออัตราส่วนของเส้นรอบวงต่อเส้นผ่านศูนย์กลางของวงกลม มีค่าประมาณ 3.14159",
            "python": "Python คือภาษาโปรแกรมระดับสูงที่เน้นความอ่านง่ายและมีประสิทธิภาพ",
            "worz": "WORZ SOVEREIGN CORE คือระบบ AI Agent แบบ Neuro-Symbolic (ปัจจุบันรันโหมด Symbolic ล้วน)"
        }
        query = command["params"]["query"]
        for key, val in kb.items():
            if key in query:
                return f"📚 {val}"
        return "🤔 ขออภัย ฉันยังไม่มีข้อมูลนี้ในฐานความรู้ (โหมด Offline)"

# ==========================================
# 4. ORCHESTRATOR (Main Loop)
# ==========================================

class SovereignCore:
    def __init__(self):
        self.parser = SymbolicParser()
        self.engines = {
            "math": MathEngine(),
            "unit": UnitEngine(),
            "knowledge": KnowledgeEngine(),
            "logic": KnowledgeEngine() # Use same for now
        }
        print("🚀 WORZ SOVEREIGN CORE (Symbolic Mode) พร้อมใช้งาน!")
        print("💡 พิมพ์ 'exit' เพื่อออก")
        print("-" * 40)

    def process(self, user_input: str) -> str:
        # 1. Parse
        command = self.parser.parse(user_input)
        
        # 2. Route & Execute
        engine_name = command.get("engine")
        if not engine_name:
            return command.get("message", "เกิดข้อผิดพลาดที่ไม่ทราบสาเหตุ")
        
        engine = self.engines.get(engine_name)
        if engine:
            return engine.execute(command)
        else:
            return f"⚠️ ไม่มี Engine สำหรับงานนี้ ({engine_name})"

    def run_cli(self):
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit", "ออก"]:
                    print("👋 ขอบคุณที่ใช้บริการ WORZ SOVEREIGN CORE")
                    break
                
                response = self.process(user_input)
                print(f"🤖 WORZ: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 ยกเลิกการทำงาน")
                break
            except Exception as e:
                print(f"❌ System Error: {e}")

# ==========================================
# 5. ENTRY POINT
# ==========================================

if __name__ == "__main__":
    app = SovereignCore()
    app.run_cli()
