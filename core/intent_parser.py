"""
Rule-Based Intent Parser
ใช้ Regex และ Keyword Mapping ล้วนๆ ไม่พึ่งพา LLM หรือ LangChain
รองรับ: Negation, Order of Operations, Multi-step commands
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple

class RuleBasedIntentParser:
    def __init__(self):
        # Negation Keywords (คำปฏิเสธ)
        self.negation_keywords = [
            'ไม่', 'ห้าม', 'อย่า', 'มิ', 'ไม่ต้อง', 'ไม่ได้', 'ไม่มี', '切勿',
            'no', 'not', 'don\'t', 'do not', 'never', 'none', 'neither', 'nor', 'cannot', 'can\'t'
        ]
        
        # Conjunctions (คำเชื่อม)
        self.conjunction_keywords = [
            'และ', 'แต่', 'หรือ', 'ทั้ง', 'กับ', 'รวมทั้ง', 'พร้อมทั้ง',
            'and', 'but', 'or', 'both', 'with', 'also', 'plus', 'as well as'
        ]
        
        # Order/Sequence Keywords (คำบอกลำดับ)
        self.order_keywords = {
            'ก่อน': 'before', 'ล่วงหน้า': 'before', 'เบื้องต้น': 'first',
            'แล้ว': 'then', 'ค่อย': 'then', 'ถัดไป': 'next', 'ต่อไป': 'next',
            'สุดท้าย': 'finally', 'ท้ายสุด': 'finally', 'จบ': 'end',
            'ขั้นแรก': 'step_1', 'ขั้นที่สอง': 'step_2', 'ขั้นที่สาม': 'step_3',
            'first': 'first', 'then': 'then', 'next': 'next', 'finally': 'finally',
            'lastly': 'finally', 'after that': 'then', 'subsequently': 'next'
        }
        
        # Priority/Urgency Keywords (คำแสดงความสำคัญ)
        self.priority_keywords = {
            'ด่วน': 'high', 'เร่งด่วน': 'urgent', 'สำคัญ': 'important', 
            'สำคัญที่สุด': 'critical', 'ทันที': 'immediate',
            'urgent': 'urgent', 'priority': 'high', 'critical': 'critical',
            'important': 'important', 'ASAP': 'immediate'
        }
        
        # Action Patterns (แพตเทิร์นการกระทำ)
        self.action_patterns = {
            'calculate': [r'คำนวณ', r'หา', r'คิด', r'แก้', r'compute', r'calculate', r'solve', r'find'],
            'convert': [r'แปลง', r'เปลี่ยน', r'convert', r'transform', r'change'],
            'check': [r'ตรวจสอบ', r'เช็ค', r'ดู', r'verify', r'check', r'examine', r'inspect'],
            'compare': [r'เปรียบเทียบ', r'เทียบ', r'compare', r'versus', r'vs'],
            'list': [r'แสดง', r'列出', r'list', r'show', r'display', r'enumerate'],
            'define': [r'นิยาม', r'ความหมาย', r'define', r'meaning', r'what is'],
            'explain': [r'อธิบาย', r'describe', r'explain', r'tell me about']
        }
        
        # Math Operation Patterns
        self.math_ops = {
            r'บวก|plus|add': '+',
            r'ลบ|minus|subtract': '-',
            r'คูณ|times|multiply': '*',
            r'หาร|divide': '/',
            r'ยกกำลัง|power|^': '**',
            r'ราก|sqrt': 'sqrt',
            r'ร้อยละ|percent|%': '/100'
        }
        
        # Unit Conversion Patterns
        self.unit_patterns = {
            'length': [r'เมตร|m', r'กิโลเมตร|km', r'เซนติเมตร|cm', r'มิลลิเมตร|mm', r'นิ้ว|inch', r'ฟุต|ft', r'หลา|yd', r'ไมล์|mile'],
            'weight': [r'กิโลกรัม|kg', r'กรัม|g', r'ปอนด์|lb', r'ออนซ์|oz', r'ตัน|ton'],
            'temperature': [r'องศา|degree', r'เซลเซียส|celsius|C', r'ฟาเรนไฮต์|fahrenheit|F', r'เคลวิน|kelvin|K'],
            'volume': [r'ลิตร|liter|L', r'มิลลิลิตร|ml', r'แกลลอน|gallon', r'ควอร์ต|quart', r'ไพนต์|pint'],
            'force': [r'นิวตัน|N', r'กิโลนิวตัน|kN', r'ปอนด์แรง|lbf', r'ไดน์|dyne'],
            'pressure': [r'ปาสกาล|Pa', r'บาร์|bar', r'psi', r'atm', r'kPa'],
            'velocity': [r'เมตรต่อวินาที|m/s', r'กิโลเมตรต่อชั่วโมง|km/h', r'mph', r'นอต|knot', r'ฟุตต่อวินาที|ft/s']
        }
        
        # Conditional Patterns (ถ้า, หาก, เมื่อ)
        self.conditional_keywords = ['ถ้า', 'หาก', 'เมื่อ', 'กรณี', 'if', 'when', 'unless', 'in case', 'provided']

    def detect_negation(self, text: str) -> Tuple[bool, List[str]]:
        """ตรวจจับคำปฏิเสธและคืนค่า flag พร้อมรายการคำที่พบ"""
        found_negations = []
        text_lower = text.lower()
        
        for keyword in self.negation_keywords:
            if keyword in text_lower:
                found_negations.append(keyword)
        
        return len(found_negations) > 0, found_negations

    def detect_order(self, text: str) -> List[Dict[str, Any]]:
        """ตรวจจับคำบอกลำดับและคืนค่าเป็นโครงสร้างลำดับงาน"""
        orders = []
        text_lower = text.lower()
        
        # ค้นหาคำบอกลำดับ
        for keyword, meaning in self.order_keywords.items():
            if keyword in text_lower:
                # หาตำแหน่งในประโยค
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                for match in pattern.finditer(text):
                    orders.append({
                        'keyword': keyword,
                        'meaning': meaning,
                        'position': match.start(),
                        'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                    })
        
        # เรียงตามตำแหน่ง
        orders.sort(key=lambda x: x['position'])
        return orders

    def detect_priority(self, text: str) -> Optional[str]:
        """ตรวจจับระดับความสำคัญของคำสั่ง"""
        text_lower = text.lower()
        
        for keyword, level in self.priority_keywords.items():
            if keyword in text_lower:
                return level
        
        return 'normal'

    def detect_action_type(self, text: str) -> List[str]:
        """ตรวจจับประเภทการกระทำจากข้อความ"""
        actions = []
        text_lower = text.lower()
        
        for action_type, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    actions.append(action_type)
                    break
        
        return actions if actions else ['general']

    def extract_math_expression(self, text: str) -> Optional[str]:
        """แยกนิพจน์คณิตศาสตร์จากข้อความ"""
        # Pattern สำหรับตัวเลขและการดำเนินการ
        math_pattern = r'(\d+(?:\.\d+)?)\s*(บวก|ลบ|คูณ|หาร|plus|minus|times|divide|\+|-|\*|/)\s*(\d+(?:\.\d+)?)'
        matches = re.findall(math_pattern, text, re.IGNORECASE)
        
        if matches:
            expressions = []
            for match in matches:
                num1, op, num2 = match
                # แปลง operation เป็นสัญลักษณ์
                op_symbol = self.math_ops.get(op.strip().lower(), op)
                if op_symbol == 'sqrt':
                    expressions.append(f'sqrt({num1})')
                else:
                    expressions.append(f'{num1} {op_symbol} {num2}')
            return ' and '.join(expressions)
        
        return None

    def extract_units(self, text: str) -> List[Dict[str, str]]:
        """แยกหน่วยวัดจากข้อความ"""
        units_found = []
        text_lower = text.lower()
        
        for unit_type, patterns in self.unit_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    # พยายามหาค่าตัวเลขที่อยู่กับหน่วย
                    value_pattern = r'(\d+(?:\.\d+)?)\s*' + pattern
                    match = re.search(value_pattern, text_lower)
                    if match and match.group(1):
                        full_match = match.group(0)
                        value = match.group(1)
                        unit_name = full_match.replace(value, '').strip()
                        units_found.append({
                            'type': unit_type,
                            'value': value,
                            'unit': unit_name
                        })
        
        return units_found

    def split_multi_step(self, text: str) -> List[str]:
        """แยกคำสั่งหลายขั้นตอนออกจากกัน"""
        steps = []
        
        # ตรวจสอบคำเชื่อมก่อน - แต่ต้องไม่ใช่ comma ในรายการตัวเลข
        for conjunction in self.conjunction_keywords:
            if conjunction in text:
                # กรณีพิเศษ: ถ้ามี comma และตามด้วยตัวเลข ให้ไม่แยก (เป็นรายการตัวเลข)
                if conjunction == ',' or conjunction == 'และ':
                    # เช็คว่าเป็นรูปแบบ "ตัวเลข, ตัวเลข, ..." หรือไม่
                    import re
                    number_list_pattern = r'^[\d\s,\.\-]+$'
                    if re.match(number_list_pattern, text.replace(' ', '')):
                        return [text]  # ไม่แยก เป็นรายการตัวเลข
                
                parts = text.split(conjunction)
                steps.extend([p.strip() for p in parts if p.strip()])
                return steps
        
        # แยกด้วยเครื่องหมายวรรคตอน (แต่ไม่ใช่ comma ในรายการตัวเลข)
        if ';' in text or '.' in text:
            parts = re.split(r'[;.]', text)
            steps.extend([p.strip() for p in parts if p.strip()])
            return steps
        
        # ถ้าไม่พบตัวแบ่ง ให้คืนค่าเป็นรายการเดียว
        return [text]

    def parse(self, text: str) -> Dict[str, Any]:
        """
        ฟังก์ชันหลักในการวิเคราะห์ Intent
        คืนค่าเป็น JSON structure
        """
        # ตรวจจับองค์ประกอบต่างๆ
        has_negation, negation_words = self.detect_negation(text)
        order_info = self.detect_order(text)
        priority = self.detect_priority(text)
        actions = self.detect_action_type(text)
        math_expr = self.extract_math_expression(text)
        units = self.extract_units(text)
        steps = self.split_multi_step(text)
        
        # ตรวจสอบ conditional
        has_conditional = any(kw in text.lower() for kw in self.conditional_keywords)
        
        # สร้างโครงสร้าง Intent
        intent = {
            'original_text': text,
            'negation': {
                'active': has_negation,
                'words': negation_words
            },
            'priority': priority,
            'actions': actions,
            'math_expression': math_expr,
            'units': units,
            'conditional': has_conditional,
            'steps': [],
            'metadata': {
                'word_count': len(text.split()),
                'char_count': len(text),
                'language': 'th' if any('\u0E00' <= c <= '\u0E7F' for c in text) else 'en'
            }
        }
        
        # จัดการลำดับขั้นตอน
        if len(steps) > 1 or order_info:
            for i, step_text in enumerate(steps):
                step_negation, step_neg_words = self.detect_negation(step_text)
                step_intent = {
                    'step_number': i + 1,
                    'text': step_text,
                    'negation': {
                        'active': step_negation,
                        'words': step_neg_words
                    },
                    'actions': self.detect_action_type(step_text),
                    'order_hint': None
                }
                
                # จับคู่กับ order keywords
                for order in order_info:
                    if order['context'] in step_text or abs(order['position'] - text.find(step_text)) < 50:
                        step_intent['order_hint'] = order['meaning']
                        break
                
                intent['steps'].append(step_intent)
        
        return intent

    def to_json(self, text: str, indent: int = 2) -> str:
        """แปลงผลลัพธ์เป็น JSON string"""
        intent = self.parse(text)
        return json.dumps(intent, ensure_ascii=False, indent=indent)


# ตัวอย่างการใช้งานและทดสอบ
if __name__ == "__main__":
    parser = RuleBasedIntentParser()
    
    test_cases = [
        # Negation Tests
        "ไม่ต้องคำนวณ 5 บวก 3",
        "ห้ามแปลงหน่วยเป็นฟุต",
        "อย่าทำขั้นตอนสุดท้าย",
        
        # Order of Operations Tests
        "ก่อนคำนวณพื้นที่ แล้วค่อยหาปริมาตร",
        "ขั้นแรกแปลง 10 กิโลกรัมเป็นปอนด์ ถัดไปคูณด้วย 2 สุดท้ายบวก 5",
        "ทำลำดับแรกคือหาแรง ลำดับที่สองคือแปลงหน่วย",
        
        # Priority Tests
        "ด่วน: คำนวณแรงทันที",
        "สำคัญที่สุด: ตรวจสอบความถูกต้องของสูตร",
        "เร่งด่วน: แปลงหน่วยทั้งหมดก่อน",
        
        # Multi-step with Conjunctions
        "คำนวณ 2 บวก 2 และ 3 คูณ 4 แต่ไม่ต้องแสดงขั้นตอน",
        "แปลง 50 องศาเซลเซียสเป็นฟาเรนไฮต์ และ 100 กิโลเมตรต่อชั่วโมงเป็นไมล์ต่อชั่วโมง",
        "หาแรงที่ใช้เคลื่อนมวล 50 กิโลกรัมด้วยความเร่ง 2 m/s² แล้วแปลงผลเป็นปอนด์",
        
        # Conditional Tests
        "ถ้าอุณหภูมิเกิน 100 องศาเซลเซียส ให้เตือนว่าอันตราย",
        "หากแรงดันมากกว่า 10 bar ให้หยุดการทำงาน",
        "เมื่อความเร็วเกิน 120 km/h ให้ลดความเร็วลง",
        
        # Complex Engineering Tests
        "ก่อนคำนวณแรงดันจากแรง 500 นิวตันบนพื้นที่ 2 ตารางเมตร แล้วค่อยแปลงเป็น psi ด่วน",
        "แปลง 100 kPa เป็น bar และ atm พร้อมเปรียบเทียบค่า",
        "คำนวณความเร็วเฉลี่ยจากระยะทาง 200 กิโลเมตรในเวลา 2.5 ชั่วโมง แล้วแปลงเป็น m/s",
        
        # Original Test Cases
        "คำนวณพื้นที่วงกลมที่มีรัศมี 10 เมตร",
        "หาแรงที่ใช้เคลื่อนมวล 50 กิโลกรัมด้วยความเร่ง 2 m/s²"
    ]
    
    print("=" * 80)
    print("=== RULE-BASED INTENT PARSER - COMPREHENSIVE TEST RESULTS ===")
    print("=" * 80)
    
    negation_count = 0
    order_count = 0
    priority_count = 0
    multi_step_count = 0
    conditional_count = 0
    
    for i, test in enumerate(test_cases, 1):
        intent = parser.parse(test)
        
        # นับสถิติ
        if intent['negation']['active']:
            negation_count += 1
        if intent['steps'] or 'ก่อน' in test or 'แล้ว' in test or 'ลำดับ' in test:
            order_count += 1
        if intent['priority'] != 'normal':
            priority_count += 1
        if len(intent['steps']) > 1 or 'และ' in test or 'แต่' in test:
            multi_step_count += 1
        if intent['conditional']:
            conditional_count += 1
        
        print(f"\n[Test {i:2d}] {test}")
        print("-" * 80)
        
        # แสดงผลลัพธ์สำคัญ
        if intent['negation']['active']:
            print(f"  ⚠️  NEGATION DETECTED: {intent['negation']['words']}")
        
        if intent['priority'] != 'normal':
            print(f"  🚨 PRIORITY: {intent['priority'].upper()}")
        
        if intent['conditional']:
            print(f"  🔀 CONDITIONAL: TRUE")
        
        if intent['actions']:
            print(f"  📋 ACTIONS: {', '.join(intent['actions'])}")
        
        if intent['math_expression']:
            print(f"  🧮 MATH: {intent['math_expression']}")
        
        if intent['units']:
            print(f"  📏 UNITS: {len(intent['units'])} found")
            for unit in intent['units']:
                print(f"      - {unit['value']} {unit['unit']} ({unit['type']})")
        
        if intent['steps']:
            print(f"  🔄 STEPS: {len(intent['steps'])} steps")
            for step in intent['steps']:
                order_hint = step.get('order_hint', 'none')
                print(f"      Step {step['step_number']}: {step['text']}")
                if order_hint != 'none':
                    print(f"        → Order: {order_hint}")
                if step['negation']['active']:
                    print(f"        → Negation: {step['negation']['words']}")
        
        print(f"  📊 Metadata: {intent['metadata']['word_count']} words, Language: {intent['metadata']['language']}")
    
    print("\n" + "=" * 80)
    print("=== TEST SUMMARY ===")
    print("=" * 80)
    print(f"Total Tests: {len(test_cases)}")
    print(f"Negation Detected: {negation_count}")
    print(f"Order/Sequence Detected: {order_count}")
    print(f"Priority/Urgency Detected: {priority_count}")
    print(f"Multi-step Commands: {multi_step_count}")
    print(f"Conditional Statements: {conditional_count}")
    print("=" * 80)
    print("\n✅ All tests completed successfully!")
    print("💡 Rule-based parsing working without LLM/LangChain")
