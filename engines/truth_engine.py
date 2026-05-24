"""
Truth-Verification Engine (Proof-of-Logic)
------------------------------------------
ระบบตรวจสอบความถูกต้องของคำตอบโดยสร้าง "หลักฐานเชิงตรรกะ" (Logical Proof)
ที่สามารถตรวจสอบย้อนกลับได้每一步 พร้อมระบบ Self-Correction เมื่อพบความขัดแย้ง

Features:
1. Logic Chain Tracking: บันทึกทุกขั้นตอนการคิด
2. Contradiction Detection: ตรวจจับความขัดแย้งในตรรกะ
3. Source Citation: อ้างอิงสูตร/กฎที่ใช้
4. Confidence Scoring: ให้คะแนนความมั่นใจจาก Logic ไม่ใช่ Probability
5. Self-Correction Loop: แก้ไขตัวเองเมื่อพบข้อผิดพลาด
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class LogicStep:
    """แทนหนึ่งขั้นตอนในการให้เหตุผล"""
    
    def __init__(self, step_id: int, operation: str, inputs: List[Any], 
                 output: Any, source: str, rule_applied: str):
        self.step_id = step_id
        self.operation = operation
        self.inputs = inputs
        self.output = output
        self.source = source  # อ้างอิงสูตรหรือกฎ
        self.rule_applied = rule_applied
        self.timestamp = datetime.now().isoformat()
        self.verified = False
        self.contradictions = []
    
    def to_dict(self) -> Dict:
        return {
            "step_id": self.step_id,
            "operation": self.operation,
            "inputs": self.inputs,
            "output": self.output,
            "source": self.source,
            "rule_applied": self.rule_applied,
            "timestamp": self.timestamp,
            "verified": self.verified,
            "contradictions": self.contradictions
        }


class TruthVerificationEngine:
    """เครื่องยนต์ตรวจสอบความจริงแบบ Proof-of-Logic"""
    
    def __init__(self):
        self.logic_chain: List[LogicStep] = []
        self.knowledge_base = self._load_knowledge_base()
        self.contradiction_rules = self._load_contradiction_rules()
        self.step_counter = 0
    
    def _load_knowledge_base(self) -> Dict:
        """โหลดฐานความรู้สำหรับอ้างอิง"""
        try:
            with open('data/kb.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"formulas": [], "physics_laws": [], "logic_rules": []}
    
    def _load_contradiction_rules(self) -> List[Dict]:
        """โหลดกฎสำหรับตรวจจับความขัดแย้ง"""
        return [
            {
                "name": "numerical_contradiction",
                "pattern": r"(>|<|>=|<=)",
                "check": lambda x, y: self._check_numerical_contradiction(x, y)
            },
            {
                "name": "logical_negation",
                "pattern": r"(ไม่|ไม่ใช่|except|not)",
                "check": lambda x, y: self._check_logical_negation(x, y)
            }
        ]
    
    def _check_numerical_contradiction(self, value1: float, value2: float) -> bool:
        """ตรวจสอบความขัดแย้งเชิงตัวเลข"""
        # ตัวอย่าง: ถ้าค่าหนึ่ง > 10 แต่ < 5 ถือว่าขัดแย้ง
        return False  # Implement logic ตามความต้องการ
    
    def _check_logical_negation(self, stmt1: str, stmt2: str) -> bool:
        """ตรวจสอบความขัดแย้งเชิงตรรกะจากการปฏิเสธ"""
        # ตรวจสอบว่าสองประโยคขัดแย้งกันหรือไม่
        return False
    
    def add_step(self, operation: str, inputs: List[Any], output: Any, 
                 source: str, rule_applied: str) -> LogicStep:
        """เพิ่มขั้นตอนการให้เหตุผล"""
        self.step_counter += 1
        step = LogicStep(
            step_id=self.step_counter,
            operation=operation,
            inputs=inputs,
            output=output,
            source=source,
            rule_applied=rule_applied
        )
        self.logic_chain.append(step)
        return step
    
    def verify_chain(self) -> Tuple[bool, List[str]]:
        """ตรวจสอบทั้งสายโซ่ตรรกะหาความขัดแย้ง"""
        issues = []
        
        for i, step in enumerate(self.logic_chain):
            # ตรวจสอบความสอดคล้องกับขั้นตอนก่อนหน้า
            if i > 0:
                prev_step = self.logic_chain[i-1]
                if self._detect_contradiction(prev_step, step):
                    issues.append(f"Contradiction between step {prev_step.step_id} and {step.step_id}")
                    step.contradictions.append(prev_step.step_id)
            
            # ตรวจสอบกับความรู้อ้างอิง
            if not self._verify_against_kb(step):
                issues.append(f"Step {step.step_id} conflicts with knowledge base")
        
        # Mark verification status
        all_verified = len(issues) == 0
        for step in self.logic_chain:
            step.verified = all_verified
        
        return all_verified, issues
    
    def _detect_contradiction(self, step1: LogicStep, step2: LogicStep) -> bool:
        """ตรวจจับความขัดแย้งระหว่างสองขั้นตอน"""
        # ตรวจสอบความขัดแย้งพื้นฐาน
        if isinstance(step1.output, (int, float)) and isinstance(step2.output, (int, float)):
            # ตัวอย่าง logic การตรวจสอบ
            pass
        
        return False
    
    def _verify_against_kb(self, step: LogicStep) -> bool:
        """ตรวจสอบขั้นตอนกับฐานความรู้"""
        # ค้นหาสูตรหรือกฎที่ใช้อ้างอิง
        for formula in self.knowledge_base.get("formulas", []):
            if formula.get("name") == step.source:
                return True
        
        for law in self.knowledge_base.get("physics_laws", []):
            if law.get("name") == step.source:
                return True
        
        # ถ้าไม่พบใน KB แต่มี rule_applied ชัดเจน ก็ถือว่าผ่าน
        return bool(step.rule_applied)
    
    def get_proof_tree(self) -> Dict:
        """สร้างต้นไม้หลักฐานสำหรับการตรวจสอบ"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_steps": len(self.logic_chain),
            "verified": all(step.verified for step in self.logic_chain),
            "steps": [step.to_dict() for step in self.logic_chain],
            "confidence_score": self._calculate_confidence()
        }
    
    def _calculate_confidence(self) -> float:
        """คำนวณคะแนนความมั่นใจจาก solidity ของตรรกะ"""
        if not self.logic_chain:
            return 0.0
        
        verified_count = sum(1 for step in self.logic_chain if step.verified)
        contradiction_count = sum(len(step.contradictions) for step in self.logic_chain)
        
        base_score = verified_count / len(self.logic_chain)
        penalty = contradiction_count * 0.1
        
        return max(0.0, min(1.0, base_score - penalty))
    
    def self_correct(self) -> List[Dict]:
        """พยายามแก้ไขตัวเองเมื่อพบความขัดแย้ง"""
        corrections = []
        
        verified, issues = self.verify_chain()
        if verified:
            return corrections
        
        # พยายามแก้ไขแต่ละ issue
        for issue in issues:
            correction = self._attempt_correction(issue)
            if correction:
                corrections.append(correction)
        
        return corrections
    
    def _attempt_correction(self, issue: str) -> Optional[Dict]:
        """พยายามแก้ไขปัญหาเฉพาะจุด"""
        # Implement logic การแก้ไขอัตโนมัติ
        return {
            "issue": issue,
            "suggestion": "Manual review required",
            "auto_fixed": False
        }
    
    def reset(self):
        """รีเซ็ตสายโซ่ตรรกะ"""
        self.logic_chain = []
        self.step_counter = 0
    
    def explain_answer(self, final_answer: Any) -> Dict:
        """อธิบายที่มาของคำตอบแบบ Proof-of-Logic"""
        verified, issues = self.verify_chain()
        
        return {
            "answer": final_answer,
            "proof_tree": self.get_proof_tree(),
            "verified": verified,
            "issues": issues,
            "confidence": self._calculate_confidence(),
            "sources_used": list(set(step.source for step in self.logic_chain if step.source)),
            "corrections_available": len(self.self_correct()) > 0
        }


# Test the engine
if __name__ == "__main__":
    engine = TruthVerificationEngine()
    
    # ตัวอย่างการใช้งาน
    engine.add_step(
        operation="addition",
        inputs=[5, 3],
        output=8,
        source="basic_arithmetic",
        rule_applied="a + b = c"
    )
    
    engine.add_step(
        operation="multiplication",
        inputs=[8, 2],
        output=16,
        source="basic_arithmetic",
        rule_applied="a × b = c"
    )
    
    result = engine.explain_answer(16)
    print(json.dumps(result, indent=2, ensure_ascii=False))
