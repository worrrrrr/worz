# 🌌 WORZ SOVEREIGN CORE v2.0

ระบบ AI Agent ลูกผสม (Neuro-Symbolic) ที่รวมพลังระหว่าง **LLM (Neural)** ในการวิเคราะห์เจตนา และ **Python Engines (Symbolic)** ในการประมวลผลตรรกะระดับโอลิมปิกคณิตศาสตร์ (IMO).

## 🏗️ Architecture Layers
- **Orchestrator:** ผู้คุมกฎและ State Management (Control Plane)
- **Parser (Neural):** ใช้ Groq Llama 3.3 สกัด Intent เป็น Structured JSON
- **Engines (Symbolic):** หน่วยประมวลผลเฉพาะทาง (Math, Logic, General)
- **Tools:** ฟังก์ชัน Atomic สำหรับการทำงานกับระบบปฏิบัติการ (OS/API)

## 🎯 Key Features
- **IMO-Level Math:** แก้สมการ Transcendental ($3^x = x^9$) ได้แม่นยำด้วย Sympy
- **Semantic Intent:** แปลงภาษาพูดเป็น Function Arguments 100%
- **Modular Expansion:** เพิ่ม Engine ใหม่ได้โดยไม่ต้องแก้ Code หลัก

## 🚀 Installation
1. `pip install -r requirements.txt`
2. สร้างไฟล์ `.env` และใส่ `GROQ_API_KEY`
3. รัน `python main.py`