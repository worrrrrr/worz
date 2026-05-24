import json, os, requests
from groq import Groq
from typing import Dict, Any
from .knowledge_base import get_knowledge_base

class IntentParser:
    def __init__(self, api_key: str):
        # ⚙️ ดึงค่าจาก .env ถ้าไม่มีให้ใช้ Default ตามนี้
        self.mode = os.getenv("LLM_MODE", "groq").lower()
        self.groq_client = Groq(api_key=api_key)
        self.ollama_url = "http://127.0.0.1:11434/api/chat"
        # หากใน .env ไม่มี OLLAMA_MODEL ให้ใช้ qwen2.5:1.5b เป็นมาตรฐาน
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

    def parse(self, query: str) -> Dict[str, Any]:
        # 🧠 System Prompt: หัวใจของการแปลเจตนา พร้อมจับ Negation, Conjunctions, Conditionals, Sequences
        system_msg = (
            "Extract intent into JSON. Keys: 'tool', 'action', 'params', 'negation', 'conjunctions', 'conditionals', 'sequences', 'priority'.\n"
            "CRITICAL: If the user speaks Thai numbers (เช่น 'สองบวกสอง'), "
            "convert them to digits (e.g., '2+2') and put in params['expression'].\n"
            "Tools: [math_engine, logic_engine, unit_engine, project_manager, device_controller]. "
            "If it's just a conversation, use tool: 'general' and put response in params['content'].\n"
            "--- NEGATION HANDLING ---\n"
            "Detect words: 'ไม่ต้อง', 'อย่า', 'ห้าม', 'ไม่', 'no', 'not', 'don't', 'never', 'none'\n"
            "Set params['negation'] = true if negation is present\n"
            "--- CONJUNCTION HANDLING ---\n"
            "Detect words: 'และ', 'แต่', 'หรือ', 'ทั้ง', 'กับ', 'and', 'but', 'or', 'both', 'with'\n"
            "Set params['conjunctions'] = list of detected conjunctions\n"
            "--- CONDITIONAL HANDLING ---\n"
            "Detect words: 'ถ้า', 'หาก', 'เมื่อ', 'unless', 'if', 'when', 'while', 'กรณีที่', 'สมมติว่า'\n"
            "Set params['conditionals'] = list of detected conditional phrases\n"
            "--- SEQUENCE HANDLING ---\n"
            "Detect words: 'ก่อน', 'หลัง', 'แล้ว', 'ต่อไป', 'ขั้นแรก', 'ขั้นที่สอง', 'สุดท้าย', 'first', 'then', 'next', 'finally', 'after', 'before'\n"
            "Set params['sequences'] = list of steps in order with step numbers\n"
            "--- PRIORITY HANDLING ---\n"
            "Detect words: 'สำคัญที่สุด', 'ด่วน', 'ก่อนอื่น', 'หลัก', 'รอง', 'priority', 'urgent', 'main', 'secondary'\n"
            "Set params['priority'] = 'high'/'medium'/'low' based on context\n"
            "--- LOGIC OPERATIONS ---\n"
            "For logic problems, set tool: 'logic_engine' and put logical expression in params['expression']\n"
            "For complex logic with sequences, set params['steps'] = array of logical operations\n"
            "--- UNIT CONVERSION ---\n"
            "For unit conversion, set tool: 'unit_engine' and put params: {'value': number, 'from': unit, 'to': unit}\n"
            "For multiple conversions, set params['conversions'] = array of conversion tasks\n"
            "--- MATH OPERATIONS ---\n"
            "For multi-step math, set params['steps'] = array of mathematical operations in sequence\n"
            "Return ONLY valid JSON."
        )

        try:
            if self.mode == "ollama":
                # 🏠 Local Processing (Ollama)
                res = requests.post(self.ollama_url, json={
                    "model": self.ollama_model,
                    "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": query}],
                    "format": "json", 
                    "stream": False, 
                    "options": {"temperature": 0}
                }, timeout=15)
                # ดึงคำตอบจากโครงสร้าง Chat API ของ Ollama
                result = json.loads(res.json()['message']['content'])
            else:
                # ☁️ Cloud Processing (Groq)
                res = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": query}],
                    response_format={"type": "json_object"},
                    temperature=0
                )
                result = json.loads(res.choices[0].message.content)

            # 🛡️ Guardrail: มั่นใจว่าต้องมี Key ครบ
            if "tool" not in result: result["tool"] = "general"
            if "params" not in result: result["params"] = {}
            if "negation" not in result["params"]: result["params"]["negation"] = False
            if "conjunctions" not in result["params"]: result["params"]["conjunctions"] = []
            if "conditionals" not in result["params"]: result["params"]["conditionals"] = []
            if "sequences" not in result["params"]: result["params"]["sequences"] = []
            if "priority" not in result["params"]: result["params"]["priority"] = "medium"
            
            # 🧠 Apply Knowledge Base
            kb = get_knowledge_base()
            result = kb.apply_knowledge(result)
            
            return result

        except Exception as e:
            # 🆘 Fallback: ถ้า Error ให้คืนค่าเป็นการสนทนาทั่วไป
            return {
                "tool": "general", 
                "params": {
                    "content": f"ระบบติดขัดเล็กน้อย: {str(e)}", 
                    "negation": False, 
                    "conjunctions": [], 
                    "conditionals": [],
                    "sequences": [],
                    "priority": "medium"
                }
            }