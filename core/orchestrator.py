import re
from core.parser import IntentParser
from core.router import Router
from core.memory import Memory
from core.knowledge_base import get_knowledge_base

class Orchestrator:
    def __init__(self, api_key: str):
        self.parser = IntentParser(api_key)
        self.router = Router()
        self.memory = Memory()
        self.kb = get_knowledge_base()

    def run(self, user_input: str) -> str:
        # Fast Track (Math Only)
        if not re.search(r'[a-zA-Zก-ฮ]', user_input) and re.match(r'^[0-9\s\+\-\*\/\^\(\)\.\=\!]+$', user_input):
            res = self.router.dispatch({"tool": "math_engine", "params": {"expression": user_input}})
            self.memory.save("last_result", res)
            return res
        

        # Check for knowledge queries first
        if any(keyword in user_input.lower() for keyword in ['formula', 'กฎ', 'สูตร', 'prove', 'พิสูจน์', 'theorem', 'พื้นที่', 'ปริมาตร', 'ความเร็ว', 'แรง', 'ตรรกะ', 'logic', 'physics', 'math', 'ขั้นตอน', 'procedure', 'วิธีทำ']):
            knowledge_results = self.kb.search_knowledge(user_input)
            if any(knowledge_results.values()):
                # Extract relevant formula and inject into intent for calculation
                intent = {"tool": "math_engine", "params": {}, "knowledge": knowledge_results}
                
                # Find the most relevant formula based on keywords
                if 'พื้นที่วงกลม' in user_input or 'area circle' in user_input.lower():
                    for item in knowledge_results["formulas"]:
                        if item['name'] == 'area_circle':
                            # Extract radius from input
                            radius_match = re.search(r'รัศมี\s*(\d+\.?\d*)', user_input)
                            if radius_match:
                                r = float(radius_match.group(1))
                                intent["params"]["expression"] = f"3.14159 * {r}^2"
                                result = self.router.dispatch(intent)
                                self.memory.save("last_result", result)
                                return result
                elif 'แรง' in user_input or 'force' in user_input.lower():
                    for item in knowledge_results["physics_laws"]:
                        if item['name'] == 'force':
                            # Extract mass and acceleration from input
                            mass_match = re.search(r'มวล\s*(\d+\.?\d*)', user_input)
                            accel_match = re.search(r'ความเร่ง\s*(\d+\.?\d*)', user_input)
                            if mass_match and accel_match:
                                m = float(mass_match.group(1))
                                a = float(accel_match.group(1))
                                intent["params"]["expression"] = f"{m} * {a}"
                                result = self.router.dispatch(intent)
                                self.memory.save("last_result", result)
                                return result
                
                # If no specific calculation found, show formulas
                response_parts = []
                if knowledge_results["formulas"]:
                    response_parts.append("Formulas found:")
                    for item in knowledge_results["formulas"]:
                        response_parts.append(f"  - {item['name']}: {item['formula']}")
                if knowledge_results["physics_laws"]:
                    response_parts.append("Physics Laws found:")
                    for item in knowledge_results["physics_laws"]:
                        response_parts.append(f"  - {item['name']}: {item['law']}")
                if knowledge_results["logic_rules"]:
                    response_parts.append("Logic Rules found:")
                    for item in knowledge_results["logic_rules"]:
                        response_parts.append(f"  - {item['name']}: {item['rule']}")
                if knowledge_results["procedures"]:
                    response_parts.append("Procedures found:")
                    for item in knowledge_results["procedures"]:
                        response_parts.append(f"  - {item['task']}:")
                        for step in item['steps']:
                            response_parts.append(f"      {step}")
                return "\n".join(response_parts)
        
        # Slow Track (AI + Memory Context)
        mem_data = self.memory.load_all()
        context_input = f"Context: Last math result was {mem_data.get('last_result')}. User: {user_input}"
        
        intent = self.parser.parse(context_input)
        self.kb.apply_knowledge(intent)
        result = self.router.dispatch(intent)
        
        
        if "Result:" in str(result): self.memory.save("last_result", result)
        return result