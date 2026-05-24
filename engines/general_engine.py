import os
from typing import Dict, Any

class GeneralEngine:
    def execute(self, params: Dict[str, Any]) -> str:
        action = params.get("action", "").lower()
        name = params.get("project_name") or params.get("name") or "new_item"
        
        if "project" in action or "create" in action:
            os.makedirs(name, exist_ok=True)
            with open(f"{name}/README.md", "w", encoding="utf-8") as f:
                f.write(f"# {name}\nCreated by WORZ CORE.")
            return f"✅ สร้างโปรเจกต์/โฟลเดอร์ '{name}' เรียบร้อย"

        if "list" in action:
            return f"📂 ไฟล์ในนี้: {', '.join(os.listdir('.'))}"

        return f"⚙️ General Task: {action} {name} executed."