import importlib
from typing import Dict, Any

class Router:
    def __init__(self):
        self.mapping = {
            "math_engine": "engines.math_engine.MathEngine",
            "project_manager": "engines.general_engine.GeneralEngine",
            "device_controller": "engines.general_engine.GeneralEngine"
        }

    def dispatch(self, intent: Dict[str, Any]) -> Any:
        tool = intent.get("tool")
        
        # ถ้าเป็นคำทักทายหรือคำถามทั่วไป ให้คืนค่าจาก AI ตรงๆ
        if tool == "general":
            return intent.get("params", {}).get("content") or intent.get("params", {}).get("action") or "I understand."

        target = self.mapping.get(tool)
        if not target: return f"Tool '{tool}' is not implemented yet."
            
        try:
            mod_name, cls_name = target.rsplit(".", 1)
            module = importlib.import_module(mod_name)
            engine = getattr(module, cls_name)()
            return engine.execute(intent.get("params", {}))
        except Exception as e:
            return f"Router Error: {str(e)}"