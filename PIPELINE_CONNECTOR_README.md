# Pipeline Connector -WORZ SOVEREIGN CORE

## ภาพรวม

Pipeline Connector เป็นโมดูลที่เชื่อมต่อ **Intent Parser** กับ **Router** เพื่อประมวลผลคำสั่งแบบหลายขั้นตอน (Multi-step Commands) โดยไม่ต้องใช้ LLM

## ความสามารถหลัก

### 1. Negation Handling (การจัดการคำปฏิเสธ)
- ตรวจจับคำปฏิเสธ: ไม่, ห้าม, อย่า, ไม่ต้อง, no, not, don't
- ข้ามขั้นตอนที่มีการปฏิเสธอัตโนมัติ

### 2. Multi-step Command Processing
- แยกคำสั่งที่มีคำเชื่อม: และ, แต่, หรือ
- ประมวลผลตามลำดับที่กำหนด

### 3. Quantity Extraction (การสกัดค่าตัวเลขและหน่วย)
- สกัดตัวเลขจากข้อความ
- จับคู่กับหน่วยวัด (กิโลกรัม, เมตร, องศา ฯลฯ)

### 4. Action-to-Engine Mapping
- `calculate` → Math Engine
- `convert` → Unit Engine
- `check/compare` → Logic Engine
- `list/define/explain` → General Engine

## การใช้งาน

```python
from core.pipeline_connector import PipelineConnector

connector = PipelineConnector()

# ตัวอย่างการใช้งาน
result = connector.execute("คำนวณ 5 บวก 3")
print(result)

# แบบมีรูปแบบข้อความสวยงาม
formatted = connector.execute_and_format("แปลง 10 กิโลกรัมเป็นปอนด์")
print(formatted)
```

## ตัวอย่างผลลัพธ์

### คำสั่งคณิตศาสตร์
```
Input: คำนวณ 5 บวก 3
Result: 8
```

### คำสั่งที่มีการปฏิเสธ
```
Input: ไม่ต้องคำนวณ 5 บวก 3 และ 10 คูณ 2
Step 1: SKIPPED (Negation detected)
Step 2: 20 (10 * 2)
```

### คำสั่งแปลงหน่วย
```
Input: แปลง 10 กิโลกรัมเป็นปอนด์
Result: 📏 10 kg = 22.0462 lb
```

### คำสั่งหลายขั้นตอน
```
Input: ขั้นแรกคำนวณ 2 บวก 2 ถัดไปคูณด้วย 3
Step 1: 4 (2 + 2)
Step 2: 12 (4 * 3)
```

## โครงสร้างข้อมูล

### Input (จาก Intent Parser)
```json
{
  "original_text": "คำนวณ 5 บวก 3",
  "negation": {"active": false, "words": []},
  "actions": ["calculate"],
  "math_expression": "5 + 3",
  "units": [],
  "steps": [...]
}
```

### Output (จากการประมวลผล)
```json
{
  "original_input": "คำนวณ 5 บวก 3",
  "parsed_intent": {...},
  "execution_results": [
    {
      "status": "completed",
      "step_number": 1,
      "tool_used": "math_engine",
      "result": "Result: 8"
    }
  ],
  "summary": {
    "total_steps": 1,
    "completed": 1,
    "skipped": 0
  }
}
```

## ไฟล์ที่เกี่ยวข้อง

- `core/pipeline_connector.py` - โมดูลหลัก
- `core/intent_parser.py` - ตัววิเคราะห์ความตั้งใจ
- `core/router.py` - ตัวส่งงานไปยัง Engines
- `engines/math_engine.py` - เครื่องมือคณิตศาสตร์
- `engines/unit_engine.py` - เครื่องมือแปลงหน่วย
- `engines/logic_engine.py` - เครื่องมือตรรกะ
- `data/kb.json` - ฐานความรู้ (สูตร, กฎฟิสิกส์, กฎตรรกะ)
- `data/config.yaml` - การตั้งค่าระบบ

## การทดสอบ

```bash
cd /workspace
PYTHONPATH=/workspace python core/pipeline_connector.py
```

## สถานะการพัฒนา

✅ Negation Detection  
✅ Multi-step Commands  
✅ Quantity Extraction  
✅ Unit Conversion  
✅ Math Expressions  
⚠️ Force Calculation (F = m*a) - กำลังพัฒนา  
⚠️ General Engine - ยังไม่พร้อมใช้งาน  

## แผนพัฒนาต่อไป

1. เพิ่มสมรรถนะ General Engine
2. เพิ่ม Statistics Engine
3. เพิ่ม Chemistry Engine
4. ปรับปรุง Quantity Extraction ให้แม่นยำขึ้น
5. เพิ่ม Support สำหรับสมการที่ซับซ้อนมากขึ้น
