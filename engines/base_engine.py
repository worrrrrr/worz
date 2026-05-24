# Base Engine - คลาสพื้นฐานสำหรับทุก Engine ใน WORZ SOVEREIGN CORE v2.1
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class BaseEngine(ABC):
    """คลาสพื้นฐานที่ทุก Engine ต้องสืบทอด
    
    Attributes:
        name (str): ชื่อของ Engine
        version (str): เวอร์ชันของ Engine
        supported_languages (List[str]): ภาษาที่รองรับ
    """
    
    def __init__(self, name: str = "base", version: str = "2.1"):
        self.name = name
        self.version = version
        self.supported_languages = ['th', 'en']
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> str:
        """ métodoหลักสำหรับประมวลผลคำสั่ง
        
        Args:
            params: พารามิเตอร์ในการประมวลผล
            
        Returns:
            str: ผลลัพธ์จากการประมวลผล
        """
        pass
    
    def _get_priority(self, params: Dict[str, Any]) -> str:
        """ดึงค่า priority จาก params"""
        return params.get("priority", "medium")
    
    def _get_steps(self, params: Dict[str, Any]) -> List[str]:
        """ดึงรายการขั้นตอนจาก params"""
        return params.get("steps", [])
    
    def _get_sequences(self, params: Dict[str, Any]) -> List[Dict]:
        """ดึงลำดับการทำงานจาก params"""
        return params.get("sequences", [])
    
    def _format_multi_step_result(self, title: str, results: List[str], priority: str) -> str:
        """จัดรูปแบบผลลัพธ์แบบหลายขั้นตอน
        
        Args:
            title: หัวข้อของผลลัพธ์
            results: รายการผลลัพธ์แต่ละขั้นตอน
            priority: ระดับความสำคัญ
            
        Returns:
            str: ผลลัพธ์ที่จัดรูปแบบแล้ว
        """
        return f"{title} (Priority: {priority}):\n" + "\n".join(results)
    
    def _order_steps_by_sequence(self, steps: List[str], sequences: List[Dict]) -> List[str]:
        """เรียงลำดับขั้นตอนตาม sequences
        
        Args:
            steps: รายการขั้นตอนเดิม
            sequences: ข้อมูลลำดับขั้นตอน
            
        Returns:
            List[str]: รายการขั้นตอนที่เรียงลำดับแล้ว
        """
        if not sequences:
            return steps
        
        ordered_steps = []
        for seq in sorted(sequences, key=lambda x: x.get('step_number', 0)):
            step_name = seq.get('step')
            if step_name and step_name in steps:
                ordered_steps.append(step_name)
        
        # เพิ่มขั้นตอนที่เหลือที่ไม่ได้ระบุใน sequences
        for step in steps:
            if step not in ordered_steps:
                ordered_steps.append(step)
        
        return ordered_steps
    
    def validate_params(self, params: Dict[str, Any], required_keys: List[str]) -> tuple:
        """ตรวจสอบพารามิเตอร์ที่จำเป็น
        
        Args:
            params: พารามิเตอร์ที่จะตรวจสอบ
            required_keys: คีย์ที่จำเป็นต้องมี
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        missing_keys = [key for key in required_keys if key not in params or params[key] is None]
        if missing_keys:
            return False, f"Error: Missing required parameters: {', '.join(missing_keys)}"
        return True, None
    
    def get_engine_info(self) -> Dict[str, Any]:
        """ข้อมูลของ Engine
        
        Returns:
            Dict: ข้อมูล Engine
        """
        return {
            "name": self.name,
            "version": self.version,
            "supported_languages": self.supported_languages
        }
