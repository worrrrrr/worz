"""
Strategic Goal Alignment & Deep Alignment Loop
จัดการเป้าหมายระยะยาว วิเคราะห์เส้นทาง และตรวจสอบความสอดคล้องกับปรัชญาผู้ใช้
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class GoalManager:
    def __init__(self, user_id: str, philosophy: Optional[str] = None):
        self.user_id = user_id
        self.philosophy = philosophy or "เน้นความเรียบง่าย ประสิทธิภาพสูงสุด และผลลัพธ์ที่ยั่งยืนเหนือกำไรระยะสั้น"
        self.goals = []
        self.alerts = []
        self.goal_file = f"data/goals_{user_id}.json"
        self._load_goals()
    
    def _load_goals(self):
        """โหลดเป้าหมายจากไฟล์"""
        if os.path.exists(self.goal_file):
            try:
                with open(self.goal_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.goals = data.get('goals', [])
                    self.alerts = data.get('alerts', [])
            except:
                self.goals = []
                self.alerts = []
    
    def _save_goals(self):
        """บันทึกเป้าหมายลงไฟล์"""
        os.makedirs('data', exist_ok=True)
        with open(self.goal_file, 'w', encoding='utf-8') as f:
            json.dump({
                'goals': self.goals,
                'alerts': self.alerts,
                'last_updated': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def set_goal(self, goal_text: str, timeframe_months: int = 12, constraints: List[str] = None):
        """ตั้งค่าเป้าหมายใหม่"""
        goal = {
            'id': len(self.goals) + 1,
            'text': goal_text,
            'timeframe_months': timeframe_months,
            'constraints': constraints or [],
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'milestones': [],
            'alignment_score': 1.0
        }
        self.goals.append(goal)
        self._save_goals()
        return goal
    
    def analyze_path(self, goal_text: str) -> Dict[str, Any]:
        """วิเคราะห์เส้นทางสู่เป้าหมาย พร้อมตรวจสอบความสอดคล้องกับปรัชญา"""
        # ค้นหาเป้าหมายที่ใกล้เคียง
        target_goal = None
        for g in self.goals:
            if goal_text.lower() in g['text'].lower() or g['text'].lower() in goal_text.lower():
                target_goal = g
                break
        
        if not target_goal:
            # สร้างเป้าหมายชั่วคราวสำหรับการวิเคราะห์
            target_goal = {
                'id': 'temp',
                'text': goal_text,
                'timeframe_months': 36,
                'constraints': ['ทุนจำกัด'],
                'status': 'analyzing'
            }
        
        # วิเคราะห์เส้นทาง (Symbolic Logic)
        analysis = {
            'goal': target_goal['text'],
            'timeframe': f"{target_goal.get('timeframe_months', 36)} เดือน",
            'philosophy_check': self._check_philosophy_alignment(goal_text),
            'roadmap': self._decompose_with_empathy(goal_text, target_goal.get('constraints', [])),
            'critical_knowledge': self._identify_critical_knowledge(goal_text),
            'risks': self._identify_risks(goal_text),
            'success_probability': self._calculate_success_probability(goal_text)
        }
        
        # ตรวจสอบ Deep Alignment Loop
        if not analysis['philosophy_check']['aligned']:
            alert = {
                'type': 'philosophy_drift',
                'message': f"⚠️ คำเตือน: แนวทางอาจขัดแย้งกับปรัชญา '{self.philosophy}'",
                'details': analysis['philosophy_check']['reason'],
                'timestamp': datetime.now().isoformat()
            }
            self.alerts.append(alert)
            self._save_goals()
            analysis['alert'] = alert
        
        return analysis
    
    def _check_philosophy_alignment(self, goal_text: str) -> Dict[str, Any]:
        """ตรวจสอบความสอดคล้องกับปรัชญาผู้ใช้"""
        keywords_sustainability = ['ยั่งยืน', 'long-term', 'stable', 'eco', 'ethical', 'quality']
        keywords_short_term = ['เร็ว', 'fast', 'quick profit', 'รวยเร็ว', 'get-rich', 'speculate']
        
        score = 0
        reasons = []
        
        for kw in keywords_sustainability:
            if kw.lower() in goal_text.lower():
                score += 0.2
                reasons.append(f"✅ พบแนวคิดยั่งยืน: '{kw}'")
        
        for kw in keywords_short_term:
            if kw.lower() in goal_text.lower():
                score -= 0.3
                reasons.append(f"⚠️ พบแนวคิดระยะสั้น: '{kw}'")
        
        # ตรวจสอบปรัชญาหลัก
        if 'ยั่งยืน' in self.philosophy and 'ยั่งยืน' in goal_text:
            score += 0.5
            reasons.append("✅ สอดคล้องกับปรัชญาหลัก: ความยั่งยืน")
        
        if 'กำไรระยะสั้น' in self.philosophy and any(kw in goal_text for kw in ['เร็ว', 'ด่วน', 'ทันที']):
            score -= 0.2
            reasons.append("⚠️ อาจขัดกับปรัชญา: เน้นความเร็วเกินไป")
        
        aligned = score >= 0.5
        return {
            'aligned': aligned,
            'score': max(0, min(1, score)),
            'reason': '; '.join(reasons) if reasons else 'ไม่พบตัวชี้วัดชัดเจน'
        }
    
    def _decompose_with_empathy(self, goal_text: str, constraints: List[str]) -> List[Dict[str, Any]]:
        """แยกงานย่อยพร้อมระดับความยากและความเห็นอกเห็นใจ"""
        # Decomposition แบบ Empathy-Driven
        phases = [
            {
                'phase': 1,
                'name': 'วางรากฐาน (Foundation)',
                'tasks': [
                    {'task': 'วิจัยตลาดและกำหนดกลุ่มเป้าหมาย', 'difficulty': 'medium', 'energy_cost': 'moderate', 'duration_weeks': 2},
                    {'task': 'วางแผนธุรกิจอย่างยั่งยืน', 'difficulty': 'high', 'energy_cost': 'high', 'duration_weeks': 3},
                    {'task': 'จัดเตรียมทุนเริ่มต้นอย่างประหยัด', 'difficulty': 'high', 'energy_cost': 'high', 'duration_weeks': 4}
                ]
            },
            {
                'phase': 2,
                'name': 'สร้างต้นแบบ (MVP)',
                'tasks': [
                    {'task': 'พัฒนาผลิตภัณฑ์/บริการขั้นต่ำ', 'difficulty': 'high', 'energy_cost': 'very_high', 'duration_weeks': 8},
                    {'task': 'ทดสอบกับกลุ่มลูกค้าเล็ก', 'difficulty': 'medium', 'energy_cost': 'moderate', 'duration_weeks': 4},
                    {'task': 'ปรับปรุงตามฟีดแบ็ก', 'difficulty': 'medium', 'energy_cost': 'moderate', 'duration_weeks': 4}
                ]
            },
            {
                'phase': 3,
                'name': 'ขยายผลอย่างยั่งยืน (Sustainable Growth)',
                'tasks': [
                    {'task': 'สร้างระบบปฏิบัติการที่มั่นคง', 'difficulty': 'high', 'energy_cost': 'high', 'duration_weeks': 12},
                    {'task': 'ขยายฐานลูกค้าอย่างค่อยเป็นค่อยไป', 'difficulty': 'medium', 'energy_cost': 'moderate', 'duration_weeks': 24},
                    {'task': 'วัดผลและปรับสมดุล', 'difficulty': 'low', 'energy_cost': 'low', 'duration_weeks': 4}
                ]
            }
        ]
        
        # ปรับตามข้อจำกัด
        if 'ทุนจำกัด' in constraints:
            phases[0]['tasks'][2]['note'] = '💡 แนะนำ: เริ่มจากเงินทุนตัวเองหรือ Bootstrapping ก่อน'
            phases[1]['tasks'][0]['note'] = '💡 แนะนำ: ใช้เครื่องมือ Open Source และทำเองให้มากที่สุด'
        
        # เพิ่มคำแนะนำด้านพลังงาน
        empathy_advice = {
            'work_rhythm': 'ทำงานหนักสลับเบา: 2 สัปดาห์ ทำงานเข้มข้น ตามด้วย 1 สัปดาห์พักฟื้น',
            'warning_signs': ['นอนไม่หลับ', 'หงุดหงิดง่าย', 'หมดไฟ'],
            'self_care': 'อย่าลืมพักทุก 90 นาที และเฉลิมฉลองความสำเร็จเล็กๆ ทุกสัปดาห์'
        }
        
        return {
            'phases': phases,
            'total_duration_weeks': sum(t['duration_weeks'] for p in phases for t in p['tasks']),
            'empathy_advice': empathy_advice
        }
    
    def _identify_critical_knowledge(self, goal_text: str) -> List[str]:
        """ระบุความรู้ที่สำคัญต่อเป้าหมาย"""
        knowledge_map = {
            'ธุรกิจ': ['FinanceEngine: การคำนวณจุดคุ้มทุน', 'FinanceEngine: ROI และ NPV', 'GeneralEngine: การวางแผนกลยุทธ์'],
            'ยั่งยืน': ['LogicEngine: การคิดเชิงระบบ', 'MathEngine: การพยากรณ์แนวโน้ม'],
            'ทุน': ['FinanceEngine: การบริหารเงินสด', 'FinanceEngine: แหล่งเงินทุนทางเลือก'],
            'ตลาด': ['GeneralEngine: การวิจัยตลาด', 'StatisticsEngine: การวิเคราะห์ข้อมูล']
        }
        
        critical = []
        for keyword, engines in knowledge_map.items():
            if keyword in goal_text:
                critical.extend(engines)
        
        if not critical:
            critical = ['GeneralEngine: การวางแผนโครงการ', 'FinanceEngine: พื้นฐานการเงิน']
        
        return critical[:5]  # เอาแค่ 5 ข้อสำคัญที่สุด
    
    def _identify_risks(self, goal_text: str) -> List[Dict[str, str]]:
        """ระบุความเสี่ยงและวิธีรับมือ"""
        risks = [
            {
                'risk': 'หมดไฟกลางคัน (Burnout)',
                'probability': 'สูง',
                'mitigation': 'แบ่งงานย่อย ฉลองความสำเร็จเล็กๆ พักผ่อนให้เพียงพอ'
            },
            {
                'risk': 'ทุนหมดก่อนบรรลุเป้าหมาย',
                'probability': 'ปานกลาง',
                'mitigation': 'ควบคุมค่าใช้จ่ายอย่างเข้มงวด มองหาแหล่งรายได้เร็ว'
            },
            {
                'risk': 'ตลาดเปลี่ยนเร็วกว่าที่คาด',
                'probability': 'ปานกลาง',
                'mitigation': 'สร้าง MVP เร็ว ทดสอบบ่อย ปรับตัวตามฟีดแบ็ก'
            }
        ]
        return risks
    
    def _calculate_success_probability(self, goal_text: str) -> float:
        """คำนวณความน่าจะเป็นความสำเร็จ (Symbolic Heuristic)"""
        base_prob = 0.5  # พื้นฐาน 50%
        
        # ปรับตามปัจจัย
        if 'ยั่งยืน' in goal_text:
            base_prob += 0.15  # ยั่งยืน = โอกาสสำเร็จสูงกว่า
        if 'ทุนจำกัด' in goal_text:
            base_prob -= 0.1  # ทุนน้อย = ความท้าทายเพิ่ม
        if '3 ปี' in goal_text or 'สามปี' in goal_text:
            base_prob += 0.1  # เวลาพอสมควร
        
        # ปรับตามปรัชญา
        if self._check_philosophy_alignment(goal_text)['aligned']:
            base_prob += 0.15
        
        return min(0.95, max(0.1, base_prob))
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """ดึงรายการแจ้งเตือน"""
        return self.alerts
    
    def clear_alerts(self):
        """ล้างแจ้งเตือน"""
        self.alerts = []
        self._save_goals()
