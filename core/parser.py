import json, os, requests
from groq import Groq
from typing import Dict, Any

class IntentParser:
    def __init__(self, api_key: str):
        # ⚙️ ดึงค่าจาก .env ถ้าไม่มีให้ใช้ Default ตามนี้
        self.mode = os.getenv("LLM_MODE", "groq").lower()
        self.groq_client = Groq(api_key=api_key)
        self.ollama_url = "http://127.0.0.1:11434/api/chat"
        # หากใน .env ไม่มี OLLAMA_MODEL ให้ใช้ qwen2.5:1.5b เป็นมาตรฐาน
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

    def parse(self, query: str) -> Dict[str, Any]:
        # 🧠 System Prompt: หัวใจของการแปลเจตนา
        system_msg = (
            "Extract intent into JSON. Keys: 'tool', 'action', 'params'.\n"
            "CRITICAL: If the user speaks Thai numbers (เช่น 'สองบวกสอง'), "
            "convert them to digits (e.g., '2+2') and put in params['expression'].\n"
            "Tools: [math_engine, project_manager, device_controller]. "
            "If it's just a conversation, use tool: 'general' and put response in params['content']."
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
            
            return result

        except Exception as e:
            # 🆘 Fallback: ถ้า Error ให้คืนค่าเป็นการสนทนาทั่วไป
            return {
                "tool": "general", 
                "params": {"content": f"ระบบติดขัดเล็กน้อย: {str(e)}"}
            }