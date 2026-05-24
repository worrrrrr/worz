# Knowledge Base - ฐานความรู้สำหรับ AI Agent
# เก็บสูตรคณิตศาสตร์ กฎฟิสิกส์ และหลักการต่างๆ

from typing import Dict, Any, List

class KnowledgeBase:
    def __init__(self):
        # สูตรคณิตศาสตร์
        self.math_formulas = {
            # เรขาคณิต
            "area_circle": "pi * r^2",
            "circumference_circle": "2 * pi * r",
            "area_triangle": "0.5 * base * height",
            "area_rectangle": "length * width",
            "area_square": "side^2",
            "volume_sphere": "(4/3) * pi * r^3",
            "volume_cube": "side^3",
            "volume_cylinder": "pi * r^2 * h",
            "pythagorean": "a^2 + b^2 = c^2",
            
            # พีชคณิต
            "quadratic_formula": "(-b ± sqrt(b^2 - 4ac)) / (2a)",
            "difference_of_squares": "a^2 - b^2 = (a+b)(a-b)",
            "square_of_sum": "(a+b)^2 = a^2 + 2ab + b^2",
            "square_of_diff": "(a-b)^2 = a^2 - 2ab + b^2",
            
            # ตรรกะและเซต
            "demorgan_1": "not (A and B) = (not A) or (not B)",
            "demorgan_2": "not (A or B) = (not A) and (not B)",
            "contrapositive": "(A implies B) = (not B implies not A)",
            
            # แคลคูลัส
            "derivative_power_rule": "d/dx(x^n) = n*x^(n-1)",
            "integral_power_rule": "∫x^n dx = x^(n+1)/(n+1) + C",
            "product_rule": "d/dx(f*g) = f'*g + f*g'",
            "chain_rule": "d/dx(f(g(x))) = f'(g(x)) * g'(x)",
        }
        
        # กฎฟิสิกส์
        self.physics_laws = {
            # การเคลื่อนที่
            "velocity": "v = d/t",
            "acceleration": "a = (v_f - v_i)/t",
            "force": "F = m*a",
            "newton_second": "F = m*a",
            "kinetic_energy": "KE = 0.5*m*v^2",
            "potential_energy": "PE = m*g*h",
            "work": "W = F*d*cos(θ)",
            "power": "P = W/t",
            
            # ไฟฟ้า
            "ohm_law": "V = I*R",
            "electric_power": "P = V*I",
            "series_resistance": "R_total = R1 + R2 + ...",
            "parallel_resistance": "1/R_total = 1/R1 + 1/R2 + ...",
            
            # ความร้อน
            "heat_transfer": "Q = m*c*ΔT",
            "ideal_gas": "PV = nRT",
            
            # ค่าคงที่
            "gravity": "g = 9.8 m/s^2",
            "speed_of_light": "c = 299792458 m/s",
            "planck_constant": "h = 6.626×10^-34 J·s",
        }
        
        # กฎตรรกะ
        self.logic_rules = {
            # Rules of Inference
            "modus_ponens": "[(A → B) ∧ A] → B",
            "modus_tollens": "[(A → B) ∧ ¬B] → ¬A",
            "hypothetical_syllogism": "[(A → B) ∧ (B → C)] → (A → C)",
            "disjunctive_syllogism": "[(A ∨ B) ∧ ¬A] → B",
            "constructive_dilemma": "[(A → B) ∧ (C → D) ∧ (A ∨ C)] → (B ∨ D)",
            
            # Logical Equivalences
            "double_negation": "¬¬A ≡ A",
            "commutative_and": "A ∧ B ≡ B ∧ A",
            "commutative_or": "A ∨ B ≡ B ∨ A",
            "associative_and": "(A ∧ B) ∧ C ≡ A ∧ (B ∧ C)",
            "associative_or": "(A ∨ B) ∨ C ≡ A ∨ (B ∨ C)",
            "distributive_1": "A ∧ (B ∨ C) ≡ (A ∧ B) ∨ (A ∧ C)",
            "distributive_2": "A ∨ (B ∧ C) ≡ (A ∨ B) ∧ (A ∨ C)",
            "absorption_1": "A ∧ (A ∨ B) ≡ A",
            "absorption_2": "A ∨ (A ∧ B) ≡ A",
        }
        
        # คำศัพท์และความสัมพันธ์
        self.semantic_relations = {
            # Synonyms (คำพ้องความหมาย)
            "big": ["large", "huge", "enormous", "vast", "massive"],
            "small": ["tiny", "little", "miniature", "microscopic"],
            "fast": ["quick", "rapid", "swift", "speedy"],
            "slow": ["sluggish", "leisurely", "gradual"],
            
            # Antonyms (คำตรงข้าม)
            "hot": "cold",
            "light": "dark",
            "up": "down",
            "left": "right",
            "increase": "decrease",
            "add": "subtract",
            "multiply": "divide",
            
            # Hierarchies (ลำดับชั้น)
            "animal": ["mammal", "bird", "reptile", "fish", "amphibian"],
            "mammal": ["human", "dog", "cat", "elephant", "whale"],
            "shape": ["circle", "triangle", "square", "rectangle", "polygon"],
            "number_type": ["integer", "rational", "irrational", "real", "complex"],
        }
        
        # ลำดับขั้นตอนมาตรฐาน
        self.standard_procedures = {
            "solve_equation": [
                "1. Identify the type of equation",
                "2. Simplify both sides",
                "3. Move all terms to one side",
                "4. Factor or use formula",
                "5. Solve for variable",
                "6. Check solution"
            ],
            "prove_theorem": [
                "1. State what is given",
                "2. State what needs to be proved",
                "3. Draw diagram if applicable",
                "4. List known facts and definitions",
                "5. Construct logical steps",
                "6. Conclude with Q.E.D."
            ],
            "unit_conversion": [
                "1. Identify starting unit",
                "2. Identify target unit",
                "3. Find conversion factor",
                "4. Set up conversion equation",
                "5. Calculate result",
                "6. Verify units cancel correctly"
            ],
            "logic_proof": [
                "1. List premises",
                "2. Identify conclusion",
                "3. Apply rules of inference",
                "4. Use logical equivalences",
                "5. Derive intermediate steps",
                "6. Reach conclusion"
            ]
        }
    
    def get_formula(self, name: str) -> str:
        """ดึงสูตรคณิตศาสตร์"""
        return self.math_formulas.get(name, f"Formula '{name}' not found.")
    
    def get_physics_law(self, name: str) -> str:
        """ดึงกฎฟิสิกส์"""
        return self.physics_laws.get(name, f"Physics law '{name}' not found.")
    
    def get_logic_rule(self, name: str) -> str:
        """ดึงกฎตรรกะ"""
        return self.logic_rules.get(name, f"Logic rule '{name}' not found.")
    
    def get_synonyms(self, word: str) -> List[str]:
        """หาคำพ้องความหมาย"""
        return self.semantic_relations.get(word.lower(), [])
    
    def get_antonym(self, word: str) -> str:
        """หาคำตรงข้าม"""
        return self.semantic_relations.get(word.lower(), None)
    
    def get_procedure(self, task: str) -> List[str]:
        """ดึงขั้นตอนมาตรฐาน"""
        return self.standard_procedures.get(task, [])
    
    def search_knowledge(self, query: str) -> Dict[str, Any]:
        """ค้นหาความรู้จากคำค้นหา - รองรับทั้งไทยและอังกฤษ"""
        results = {
            "formulas": [],
            "physics_laws": [],
            "logic_rules": [],
            "procedures": []
        }
        
        query_lower = query.lower()
        
        # Mapping คำศัพท์ภาษาไทยเป็นภาษาอังกฤษ
        th_to_en_map = {
            'พื้นที่': ['area'],
            'วงกลม': ['circle'],
            'สามเหลี่ยม': ['triangle'],
            'สี่เหลี่ยม': ['square', 'rectangle'],
            'ปริมาตร': ['volume'],
            'ทรงกลม': ['sphere'],
            'ลูกบาศก์': ['cube'],
            'ทรงกระบอก': ['cylinder'],
            'พีทาโกรัส': ['pythagorean'],
            'สมการ': ['equation', 'formula'],
            'กำลังสอง': ['square', 'quadratic'],
            'กฎ': ['law', 'rule'],
            'นิวตัน': ['newton'],
            'ความเร็ว': ['velocity', 'speed'],
            'ความเร่ง': ['acceleration'],
            'แรง': ['force'],
            'พลังงาน': ['energy'],
            'จลน์': ['kinetic'],
            'ศักย์': ['potential'],
            'งาน': ['work'],
            'กำลัง': ['power'],
            'ไฟฟ้า': ['electric', 'voltage', 'current', 'resistance'],
            'ความร้อน': ['heat', 'thermal'],
            'แก๊ส': ['gas'],
            'ตรรกะ': ['logic', 'logical'],
            'โมดัส': ['modus'],
            'โพเนนส์': ['ponens'],
            'โทลเลนส์': ['tollens'],
            'ซิลโลจิซึม': ['syllogism'],
            'ดีมอร์แกน': ['demorgan', 'de morgan'],
            'โมดัส โพเนนส์': ['modus ponens'],
            'โมดัส': ['modus'],
            'โพเนนส์': ['ponens'],
            'โทลเลนส์': ['tollens'],
            'ขั้นตอน': ['procedure', 'steps', 'method'],
            'วิธีทำ': ['procedure', 'steps', 'method'],
            'แก้': ['solve', 'solution'],
            'พิสูจน์': ['prove', 'proof', 'theorem'],
        }
        
        # แปลงคำไทยเป็นอังกฤษเพื่อค้นหา
        expanded_queries = [query_lower]
        for th_word, en_words in th_to_en_map.items():
            if th_word in query_lower:
                expanded_queries.extend(en_words)
        
        # ค้นหาด้วยทุก query
        for q in expanded_queries:
        
            # ค้นหาในสูตรคณิตศาสตร์
            for key, value in self.math_formulas.items():
                if q in key.lower() or q in value.lower():
                    item = {"name": key, "formula": value}
                    if item not in results["formulas"]:
                        results["formulas"].append(item)
            
            # ค้นหาในกฎฟิสิกส์
            for key, value in self.physics_laws.items():
                if q in key.lower() or q in value.lower():
                    item = {"name": key, "law": value}
                    if item not in results["physics_laws"]:
                        results["physics_laws"].append(item)
            
            # ค้นหาในกฎตรรกะ
            for key, value in self.logic_rules.items():
                if q in key.lower() or q in value.lower():
                    item = {"name": key, "rule": value}
                    if item not in results["logic_rules"]:
                        results["logic_rules"].append(item)
            
            # ค้นหาในขั้นตอน
            for key, value in self.standard_procedures.items():
                if q in key.lower():
                    item = {"task": key, "steps": value}
                    if item not in results["procedures"]:
                        results["procedures"].append(item)
        
        return results
    
    def apply_knowledge(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """ประยุกต์ใช้ความรู้กับ Intent"""
        params = intent.get("params", {})
        tool = intent.get("tool", "")
        
        # ถ้ามี mention ถึงสูตรหรือกฎ ให้เพิ่มข้อมูล
        if "formula" in str(params).lower() or "กฎ" in str(params):
            search_results = self.search_knowledge(str(params))
            if search_results["formulas"] or search_results["physics_laws"]:
                params["knowledge_context"] = search_results
        
        # ถ้าเป็นโจทย์ปัญหา ให้เพิ่มขั้นตอน
        if tool in ["math_engine", "logic_engine"]:
            if "solve" in str(params).lower() or "证明" in str(params) or "พิสูจน์" in str(params):
                procedure = self.get_procedure("solve_equation") if tool == "math_engine" else self.get_procedure("logic_proof")
                params["suggested_steps"] = procedure
        
        intent["params"] = params
        return intent

# Singleton instance
_kb_instance = None

def get_knowledge_base() -> KnowledgeBase:
    """Get singleton KnowledgeBase instance"""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance
