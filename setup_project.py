import os

def create_structure():
    # 1. นิยามโครงสร้าง Directory และไฟล์ที่ต้องมี
    structure = {
        "core": ["__init__.py", "parser.py", "router.py", "orchestrator.py"],
        "engines": ["__init__.py", "math_engine.py", "unit_engine.py", "logic_engine.py"],
        "tools": ["__init__.py", "calculator.py", "api_helpers.py"],
        "data": {
            "logs": [], # โฟลเดอร์ว่าง
            "files": ["kb.json", "config.yaml"]
        },
        "tests": ["__init__.py", "test_cases.py"]
    }

    print("🚀 Starting Project Setup...")

    # 2. สร้างไฟล์หลักที่ Root
    root_files = ["main.py", ".env", "README.md", ".gitignore"]
    for f in root_files:
        if not os.path.exists(f):
            with open(f, 'w', encoding='utf-8') as file:
                if f == ".env":
                    file.write("GROQ_API_KEY=your_api_key_here\n")
            print(f"✔️ Created root file: {f}")

    # 3. สร้าง Directory และไฟล์ย่อย
    for folder, content in structure.items():
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"📁 Created folder: {folder}")
        
        # กรณีเป็น Dictionary (เช่น dataที่มีโฟลเดอร์ย่อย)
        if isinstance(content, dict):
            for subfolder in content.get("logs", []): # แก้ไขตามโครงสร้างจริงถ้ามีเพิ่ม
                pass 
            os.makedirs(os.path.join(folder, "logs"), exist_ok=True)
            for f in content.get("files", []):
                file_path = os.path.join(folder, f)
                if not os.path.exists(file_path):
                    open(file_path, 'w').close()
        
        # กรณีเป็น List ของไฟล์
        elif isinstance(content, list):
            for f in content:
                file_path = os.path.join(folder, f)
                if not os.path.exists(file_path):
                    with open(file_path, 'w', encoding='utf-8') as file:
                        if f == "__init__.py":
                            pass # ไฟล์ว่างสำหรับ module
                        else:
                            file.write(f"# Placeholder for {f}\n")
                    print(f"  └── 📄 Created: {f}")

    print("\n✅ Project structure is ready!")
    print("Next: Add your Groq API Key to .env and start coding in core/parser.py")

if __name__ == "__main__":
    create_structure()