import re
from core.parser import IntentParser
from core.router import Router
from core.memory import Memory

class Orchestrator:
    def __init__(self, api_key: str):
        self.parser = IntentParser(api_key)
        self.router = Router()
        self.memory = Memory()

    def run(self, user_input: str) -> str:
        # 🏎️ Fast Track (Math Only)
        if not re.search(r'[a-zA-Zก-ฮ]', user_input) and re.match(r'^[0-9\s\+\-\*\/\^\(\)\.\=\!]+$', user_input):
            res = self.router.dispatch({"tool": "math_engine", "params": {"expression": user_input}})
            self.memory.save("last_result", res)
            return res
        
        # 🧠 Slow Track (AI + Memory Context)
        mem_data = self.memory.load_all()
        context_input = f"Context: Last math result was {mem_data.get('last_result')}. User: {user_input}"
        
        intent = self.parser.parse(context_input)
        result = self.router.dispatch(intent)
        
        # ถ้าเป็นเลข เก็บลง Memory
        if "Result:" in str(result): self.memory.save("last_result", result)
        return result