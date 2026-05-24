"""
Orchestrator - Core coordination module for WORZ SOVEREIGN CORE
Routes requests to appropriate engines and manages context.
Version 2.2: Enhanced reasoning trace and ANSI color support
"""
import re
from typing import Dict, Any, Optional, List

from core.parser import IntentParser
from core.router import Router
from core.memory import Memory
from core.knowledge_base import get_knowledge_base


# ANSI Color codes for terminal output
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


class Orchestrator:
    """Main orchestrator that coordinates parsing, routing, and memory."""
    
    def __init__(self, api_key: str = "default_key"):
        """Initialize the Orchestrator with required components.
        
        Args:
            api_key: API key for LLM services (default: "default_key" for testing)
        """
        self.parser = IntentParser(api_key)
        self.router = Router()
        self.memory = Memory()
        self.kb = get_knowledge_base()
        self.reasoning_steps: List[Dict[str, Any]] = []
        self.verbose_mode = False
    
    def get_reasoning_steps(self) -> List[Dict[str, Any]]:
        """Get all recorded reasoning steps.
        
        Returns:
            List of reasoning step dictionaries
        """
        return self.reasoning_steps
    
    def _is_math_expression(self, user_input: str) -> bool:
        """Check if input is a pure math expression (fast track).
        
        Args:
            user_input: User's input string
            
        Returns:
            bool: True if input appears to be a math expression
        """
        has_no_letters = not re.search(r'[a-zA-Zก-ฮ]', user_input)
        is_math_chars = re.match(r'^[0-9\s\+\-\*\/\^\(\)\.\=\!]+$', user_input)
        return has_no_letters and bool(is_math_chars)
    
    def _has_knowledge_keywords(self, user_input: str) -> bool:
        """Check if input contains knowledge-related keywords."""
        # Exclude paradox-related patterns from knowledge detection
        if self._detect_advanced_paradox(user_input):
            return False
        if self._detect_paradox(user_input):
            return False
            
        keywords = [
            'formula', 'กฎ', 'สูตร', 'prove', 'พิสูจน์', 'theorem',
            'พื้นที่', 'ปริมาตร', 'ความเร็ว', 'แรง', 'ตรรกะ', 'logic',
            'physics', 'math', 'ขั้นตอน', 'procedure', 'วิธีทำ'
        ]
        return any(keyword in user_input.lower() for keyword in keywords)
    
    def _detect_paradox(self, user_input: str) -> Optional[str]:
        """Detect logical paradoxes or contradictions in user input.
        
        Args:
            user_input: User's input string
            
        Returns:
            Explanation of paradox if detected, None otherwise
        """
        # Pattern: number > X but < Y where X >= Y
        import re
        
        # Thai pattern: หาเลขที่ > A แต่น้อยกว่า B OR มากกว่า A แต่น้อยกว่า B
        thai_patterns = [
            # Pattern 1: มากกว่า A แต่น้อยกว่า B
            r'มาก(?:กว่า|ๆ)\s*(\d+(?:\.\d+)?)\s*(?:แต่|และ|ซึ่ง)\s*น้อย(?:กว่า|ๆ)\s*(\d+(?:\.\d+)?)',
            # Pattern 2: > A แต่น้อยกว่า B
            r'>\s*(\d+(?:\.\d+)?)\s*(?:แต่|และ|ซึ่ง)\s*น้อย(?:กว่า|ๆ)\s*(\d+(?:\.\d+)?)',
            # Pattern 3: หาเลขที่มากกว่า A แต่น้อยกว่า B
            r'(?:หา|เลขที่).*?มาก(?:กว่า|ๆ)\s*(\d+(?:\.\d+)?)\s*(?:แต่|และ|ซึ่ง)\s*น้อย(?:กว่า|ๆ)\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in thai_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                groups = match.groups()
                try:
                    lower_bound = float(groups[0])
                    upper_bound = float(groups[1])
                    if lower_bound >= upper_bound:
                        return (f"⚠️ **ตรวจพบความขัดแย้งทางตรรกะ (Paradox)**\n\n"
                                f"คุณต้องการหาเลขที่ **มากกว่า {lower_bound}** แต่ **น้อยกว่า {upper_bound}**\n\n"
                                f"🧠 **เหตุผลทางตรรกะ:**\n"
                                f"   - เซตของจำนวนที่มากกว่า {lower_bound} คือ {{{lower_bound}, ∞}}\n"
                                f"   - เซตของจำนวนที่น้อยกว่า {upper_bound} คือ {{-∞, {upper_bound}}}\n"
                                f"   - อินเตอร์เซกชันของทั้งสองเซตคือ: ∅ (เซตว่าง)\n\n"
                                f"❌ **สรุป:** ไม่มีจำนวนจริงใดที่เป็นไปตามเงื่อนไขนี้ เพราะ {lower_bound} ≥ {upper_bound}\n"
                                f"   นี่เป็นตัวอย่างของ **Contradiction** ในตรรกศาสตร์")
                except (ValueError, TypeError):
                    pass
        
        # English pattern: number > X but less than Y
        eng_patterns = [
            r'greater than\s*(\d+(?:\.\d+)?)\s*(?:but|and)\s*less than\s*(\d+(?:\.\d+)?)',
            r'>\s*(\d+(?:\.\d+)?)\s*(?:but|and)\s*<\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in eng_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                groups = match.groups()
                try:
                    lower_bound = float(groups[0])
                    upper_bound = float(groups[1])
                    if lower_bound >= upper_bound:
                        return (f"⚠️ **Logical Paradox Detected**\n\n"
                                f"You're asking for a number **greater than {lower_bound}** but **less than {upper_bound}**\n\n"
                                f"🧠 **Logical Reasoning:**\n"
                                f"   - Set of numbers > {lower_bound}: ({lower_bound}, ∞)\n"
                                f"   - Set of numbers < {upper_bound}: (-∞, {upper_bound})\n"
                                f"   - Intersection: ∅ (empty set)\n\n"
                                f"❌ **Conclusion:** No real number satisfies this condition because {lower_bound} ≥ {upper_bound}")
                except (ValueError, TypeError):
                    pass
        
        return None
    
    def _process_knowledge_query(self, user_input: str) -> Optional[str]:
        """Process knowledge-based queries."""
        knowledge_results = self.kb.search_knowledge(user_input)
        
        if not any(knowledge_results.values()):
            return None
        
        calculation_result = self._extract_calculation_from_knowledge(
            user_input, knowledge_results
        )
        if calculation_result:
            return calculation_result
        
        return self._format_knowledge_results(knowledge_results)
    
    def _extract_calculation_from_knowledge(
        self, user_input: str, knowledge_results: Dict[str, Any]
    ) -> Optional[str]:
        """Extract and execute calculations from knowledge queries."""
        # Circle area calculation
        if 'พื้นที่วงกลม' in user_input or 'area circle' in user_input.lower():
            for item in knowledge_results.get("formulas", []):
                if item['name'] == 'area_circle':
                    radius_match = re.search(r'รัศมี\s*(\d+\.?\d*)', user_input)
                    if radius_match:
                        r = float(radius_match.group(1))
                        intent = {
                            "tool": "math_engine",
                            "params": {"expression": f"3.14159 * {r}^2"}
                        }
                        result = self.router.dispatch(intent)
                        self.memory.save("last_result", result)
                        return result
        
        # Force calculation (F = m*a)
        if 'แรง' in user_input or 'force' in user_input.lower():
            for item in knowledge_results.get("physics_laws", []):
                if item['name'] == 'force':
                    mass_match = re.search(r'มวล\s*(\d+\.?\d*)', user_input)
                    accel_match = re.search(r'ความเร่ง\s*(\d+\.?\d*)', user_input)
                    if mass_match and accel_match:
                        m = float(mass_match.group(1))
                        a = float(accel_match.group(1))
                        intent = {
                            "tool": "math_engine",
                            "params": {"expression": f"{m} * {a}"}
                        }
                        result = self.router.dispatch(intent)
                        self.memory.save("last_result", result)
                        return result
        
        return None
    
    def _format_knowledge_results(self, knowledge_results: Dict[str, Any]) -> str:
        """Format knowledge base search results for display."""
        response_parts = []
        
        if knowledge_results.get("formulas"):
            response_parts.append("Formulas found:")
            for item in knowledge_results["formulas"]:
                response_parts.append(f"  - {item['name']}: {item['formula']}")
        
        if knowledge_results.get("physics_laws"):
            response_parts.append("Physics Laws found:")
            for item in knowledge_results["physics_laws"]:
                response_parts.append(f"  - {item['name']}: {item['law']}")
        
        if knowledge_results.get("logic_rules"):
            response_parts.append("Logic Rules found:")
            for item in knowledge_results["logic_rules"]:
                response_parts.append(f"  - {item['name']}: {item['rule']}")
        
        if knowledge_results.get("procedures"):
            response_parts.append("Procedures found:")
            for item in knowledge_results["procedures"]:
                response_parts.append(f"  - {item['task']}:")
                for step in item['steps']:
                    response_parts.append(f"      {step}")
        
        return "\n".join(response_parts)
    
    def _record_reasoning_step(self, step_name: str, details: Dict[str, Any]):
        """Record a reasoning step for later retrieval."""
        step = {
            "step": step_name,
            "details": details,
            "timestamp": __import__('time').time()
        }
        self.reasoning_steps.append(step)
    
    def _format_reasoning_trace(self) -> str:
        """Format reasoning steps with ANSI colors."""
        if not self.reasoning_steps:
            return ""
        
        output = []
        output.append(f"\n{Colors.BOLD}{Colors.CYAN}═══ [Reasoning Trace] ═══{Colors.RESET}\n")
        
        for i, step in enumerate(self.reasoning_steps, 1):
            step_name = step['step']
            details = step['details']
            
            output.append(f"{Colors.YELLOW}[Step {i}] {Colors.BOLD}{step_name}{Colors.RESET}")
            
            for key, value in details.items():
                output.append(f"  {Colors.GRAY}{key}:{Colors.RESET} {value}")
            
            output.append("")
        
        output.append(f"{Colors.BOLD}{Colors.GREEN}═══ [End Reasoning Trace] ═══{Colors.RESET}\n")
        return "\n".join(output)
    
    def _detect_advanced_paradox(self, user_input: str) -> Optional[str]:
        """Detect advanced logical paradoxes including day-of-week contradictions."""
        # Pattern for day-of-week paradox (Thai)
        # Matches: "วันX...พรุ่งนี้...ไม่...วันY"
        thai_day_pattern = r'วัน([^\s]+).*?พรุ่งนี้.*?ไม่.*?วัน([^\s]+)'
        match = re.search(thai_day_pattern, user_input)
        
        if match:
            today_full = match.group(1).strip()
            tomorrow_claim_full = match.group(2).strip()
            
            # Extract just the day name (last character(s) that form a valid day)
            thai_days = ['จันทร์', 'อังคาร', 'พุธ', 'พฤหัส', 'ศุกร์', 'เสาร์', 'อาทิตย์']
            
            today = None
            for day in thai_days:
                if day in today_full:
                    today = day
                    break
            
            tomorrow_claim = None
            for day in thai_days:
                if day in tomorrow_claim_full:
                    tomorrow_claim = day
                    break
            
            if not today:
                today = today_full[-3:] if len(today_full) >= 3 else today_full
            if not tomorrow_claim:
                tomorrow_claim = tomorrow_claim_full[-3:] if len(tomorrow_claim_full) >= 3 else tomorrow_claim_full
            
            # Map Thai days to numbers
            day_map = {
                'จันทร์': 1, 'monday': 1,
                'อังคาร': 2, 'tuesday': 2,
                'พุธ': 3, 'wednesday': 3,
                'พฤหัส': 4, 'thursday': 4,
                'ศุกร์': 5, 'friday': 5,
                'เสาร์': 6, 'saturday': 6,
                'อาทิตย์': 0, 'dominic': 0, 'sunday': 0,
            }
            
            today_num = day_map.get(today, None)
            tomorrow_num = day_map.get(tomorrow_claim, None)
            
            if today_num is not None and tomorrow_num is not None:
                expected_tomorrow = (today_num + 1) % 7
                
                # Check if the claimed tomorrow matches expected
                if tomorrow_num == expected_tomorrow:
                    self._record_reasoning_step("Paradox Detection", {
                        "input": user_input,
                        "today": today,
                        "claimed_tomorrow": tomorrow_claim,
                        "expected_tomorrow_num": expected_tomorrow,
                        "contradiction": f"If today is {today}, tomorrow MUST be {tomorrow_claim}"
                    })
                    
                    return (f"{Colors.RED}{Colors.BOLD}⚠️ ตรวจพบความขัดแย้งทางตรรกะ (Logical Paradox){Colors.RESET}\n\n"
                            f"{Colors.YELLOW}📝 วิเคราะห์:{Colors.RESET}\n"
                            f"   - คุณบอกว่า: \"วันนี้เป็นวัน{today} และ พรุ่งนี้ไม่ใช่วัน{tomorrow_claim}\"\n"
                            f"   - แต่ตามปฏิทิน: ถ้าวันนี้เป็นวัน{today} → พรุ่งนี้ต้องเป็นวัน{tomorrow_claim}\n\n"
                            f"{Colors.CYAN}🧠 เหตุผลทางตรรกะ:{Colors.RESET}\n"
                            f"   - ให้ P = \"วันนี้เป็นวัน{today}\"\n"
                            f"   - ให้ Q = \"พรุ่งนี้เป็นวัน{tomorrow_claim}\"\n"
                            f"   - ความจริง: P → Q (เป็นสัจนิรันดร์)\n"
                            f"   - คุณอ้าง: P ∧ ¬Q (ความขัดแย้ง!)\n\n"
                            f"{Colors.RED}❌ สรุป: ข้อความนี้เป็น CONTRADICTION ในตรรกศาสตร์{Colors.RESET}")
        
        # English pattern: "Today is X and tomorrow is not Y"
        eng_pattern = r'today\s+is\s+(\w+).*?tomorrow\s+is\s+not\s+(\w+)'
        match = re.search(eng_pattern, user_input, re.IGNORECASE)
        
        if match:
            today = match.group(1).strip().lower()
            tomorrow_claim = match.group(2).strip().lower()
            
            day_map = {
                'monday': 1, 'tuesday': 2, 'wednesday': 3,
                'thursday': 4, 'friday': 5, 'saturday': 6,
                'sunday': 0
            }
            
            today_num = day_map.get(today, None)
            tomorrow_num = day_map.get(tomorrow_claim, None)
            
            if today_num is not None and tomorrow_num is not None:
                expected_tomorrow = (today_num + 1) % 7
                
                if tomorrow_num == expected_tomorrow:
                    self._record_reasoning_step("Paradox Detection", {
                        "input": user_input,
                        "today": today,
                        "claimed_tomorrow": tomorrow_claim,
                        "type": "day-of-week contradiction"
                    })
                    
                    return (f"{Colors.RED}{Colors.BOLD}⚠️ Logical Paradox Detected{Colors.RESET}\n\n"
                            f"{Colors.YELLOW}📝 Analysis:{Colors.RESET}\n"
                            f"   - You claim: \"Today is {today} and tomorrow is not {tomorrow_claim}\"\n"
                            f"   - But by calendar: If today is {today} → tomorrow must be {tomorrow_claim}\n\n"
                            f"{Colors.CYAN}🧠 Logical Reasoning:{Colors.RESET}\n"
                            f"   - Let P = \"Today is {today}\"\n"
                            f"   - Let Q = \"Tomorrow is {tomorrow_claim}\"\n"
                            f"   - Truth: P → Q (tautology)\n"
                            f"   - Your claim: P ∧ ¬Q (contradiction!)\n\n"
                            f"{Colors.RED}❌ Conclusion: This is a CONTRADICTION in logic{Colors.RESET}")
        
        return None
    
    def run(self, user_input: str, return_with_trace: bool = False) -> Dict[str, Any]:
        """Process user input and return response.
        
        Args:
            user_input: User's input string
            return_with_trace: If True, include reasoning trace in output
            
        Returns:
            Dictionary with 'response' and optionally 'reasoning_trace'
        """
        # Reset reasoning steps for new query
        self.reasoning_steps = []
        
        # Check for verbose mode activation
        if "verbose" in user_input.lower() or "monologue" in user_input.lower():
            self.verbose_mode = True
        
        # Advanced Paradox Detection
        paradox_response = self._detect_advanced_paradox(user_input)
        if paradox_response:
            self.memory.save("last_result", paradox_response)
            self.memory.add_to_history({
                "input": user_input,
                "output": paradox_response,
                "type": "paradox"
            })
            self.memory.add_to_reasoning_history({
                "input": user_input,
                "steps": self.reasoning_steps.copy(),
                "timestamp": __import__('time').time()
            })
            
            result_dict = {"response": paradox_response}
            if return_with_trace or self.verbose_mode:
                result_dict["reasoning_trace"] = [step["step"] + ": " + str(step["details"]) for step in self.reasoning_steps]
            return result_dict
        
        # Basic Paradox Detection
        paradox_response = self._detect_paradox(user_input)
        if paradox_response:
            self.memory.save("last_result", paradox_response)
            self._record_reasoning_step("Paradox Detection", {"type": "numeric", "input": user_input})
            
            result_dict = {"response": paradox_response}
            if return_with_trace or self.verbose_mode:
                result_dict["reasoning_trace"] = [step["step"] + ": " + str(step["details"]) for step in self.reasoning_steps]
            return result_dict
        
        # Fast Track: Pure math expressions
        if self._is_math_expression(user_input):
            self._record_reasoning_step("Input Analysis", {
                "type": "Math Expression",
                "expression": user_input,
                "track": "Fast Track"
            })
            intent = {"tool": "math_engine", "params": {"expression": user_input}}
            result = self.router.dispatch(intent)
            self.memory.save("last_result", result)
            self._record_reasoning_step("Engine Execution", {
                "engine": "math_engine",
                "result_preview": str(result)[:100]
            })
            
            result_dict = {"response": result}
            if return_with_trace or self.verbose_mode:
                result_dict["reasoning_trace"] = [step["step"] + ": " + str(step["details"]) for step in self.reasoning_steps]
            return result_dict
        
        # Check for verbose/monologue mode request
        if "แสดงขั้นตอนการคิด" in user_input or "reasoning trace" in user_input.lower():
            self.verbose_mode = True
            self._record_reasoning_step("Mode Activation", {
                "mode": "Verbose/Reasoning Trace",
                "triggered_by": user_input[:50]
            })
        
        if self.verbose_mode or "verbose" in user_input.lower() or "monologue" in user_input.lower():
            intent = {
                "tool": "general",
                "params": {
                    "action": "verbose",
                    "content": user_input,
                    "verbose": True
                }
            }
            self._record_reasoning_step("Intent Routing", {
                "target": "general_engine",
                "action": "verbose"
            })
            result = self.router.dispatch(intent)
            self.memory.save("last_result", result)
            self._record_reasoning_step("Output Generation", {
                "result_length": len(str(result)),
                "verbose": True
            })
            
            result_dict = {"response": result} if isinstance(result, str) else result
            result_dict["verbose"] = True
            if return_with_trace or self.verbose_mode:
                result_dict["reasoning_trace"] = [step["step"] + ": " + str(step["details"]) for step in self.reasoning_steps]
            return result_dict
        
        # Knowledge Query Track
        if self._has_knowledge_keywords(user_input):
            self._record_reasoning_step("Knowledge Query", {
                "keywords_detected": True,
                "input_preview": user_input[:50]
            })
            knowledge_response = self._process_knowledge_query(user_input)
            if knowledge_response:
                self._record_reasoning_step("Knowledge Retrieval", {
                    "response_length": len(knowledge_response)
                })
                
                result_dict = {"response": knowledge_response}
                if return_with_trace or self.verbose_mode:
                    result_dict["reasoning_trace"] = [step["step"] + ": " + str(step["details"]) for step in self.reasoning_steps]
                return result_dict
        
        # Slow Track: AI + Memory Context
        self._record_reasoning_step("Slow Track", {
            "reason": "Complex query requiring AI context",
            "input_preview": user_input[:50]
        })
        
        mem_data = self.memory.load_all()
        last_result = mem_data.get('last_result', 'N/A')
        context_input = f"Context: Last math result was {last_result}. User: {user_input}"
        
        self._record_reasoning_step("Memory Context", {
            "last_result": str(last_result)[:50],
            "context_built": True
        })
        
        intent = self.parser.parse(context_input)
        self._record_reasoning_step("Intent Parsing", {
            "intent_tool": intent.get('tool', 'unknown'),
            "intent_params_count": len(intent.get('params', {}))
        })
        
        self.kb.apply_knowledge(intent)
        result = self.router.dispatch(intent)
        
        self._record_reasoning_step("Engine Execution", {
            "engine": intent.get('tool', 'unknown'),
            "result_preview": str(result)[:100]
        })
        
        if "Result:" in str(result):
            self.memory.save("last_result", result)
        
        self._record_reasoning_step("Memory Update", {
            "saved": "Result:" in str(result),
            "key": "last_result"
        })
        
        result_dict = {"response": result}
        if return_with_trace or self.verbose_mode:
            result_dict["reasoning_trace"] = [step["step"] + ": " + str(step["details"]) for step in self.reasoning_steps]
        return result_dict
    
    def get_reasoning_steps(self) -> List[Dict[str, Any]]:
        """Return the list of reasoning steps."""
        return self.reasoning_steps.copy()
