#!/usr/bin/env python3
"""
Test script for Thai language commands:
1. Paradox Test - หาเลขที่ > 10 แต่น้อยกว่า 5
2. Verbose Mode - แสดงขั้นตอนการคิด (Reasoning Trace)
3. Multi-Step Task - คำนวณพื้นที่วงกลม แปลงหน่วย และบันทึกความจำ
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from core.orchestrator import Orchestrator
from core.memory import Memory

def test_paradox():
    """Test 1: Paradox Test - ตรรกะขัดแย้ง"""
    print("=" * 80)
    print("TEST 1: PARADOX TEST")
    print("=" * 80)
    print("คำสั่ง: 'จงหาเลขที่ > 10 แต่น้อยกว่า 5 ถ้าหาไม่ได้ให้บอกเหตุผลทางตรรกะมา'")
    print("-" * 80)
    
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ กรุณาตั้งค่า GROQ_API_KEY ในไฟล์ .env")
            return
        
        core = Orchestrator(api_key)
        query = "จงหาเลขที่ > 10 แต่น้อยกว่า 5 ถ้าหาไม่ได้ให้บอกเหตุผลทางตรรกะมา"
        
        response = core.run(query)
        print(f"\nผลลัพธ์:\n{response}\n")
        
        # ตรวจสอบว่าระบบตรวจจับ Paradox ได้หรือไม่
        if "ขัดแย้ง" in response or "paradox" in response.lower() or "เป็นไปไม่ได้" in response:
            print("✅ ระบบตรวจจับ Paradox ได้ถูกต้อง!")
        else:
            print("⚠️ ระบบอาจไม่ได้ตรวจจับ Paradox อย่างชัดเจน")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
    
    print()


def test_verbose_monologue():
    """Test 2: Show Monologue/Verbose Mode with Reasoning Trace"""
    print("=" * 80)
    print("TEST 2: VERBOSE MODE - REASONING TRACE")
    print("=" * 80)
    print("คำสั่ง: 'เปิดโหมด Verbose และแสดงขั้นตอนการคิด (Reasoning Trace) ในทุกคำตอบที่ได้'")
    print("-" * 80)
    
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ กรุณาตั้งค่า GROQ_API_KEY ในไฟล์ .env")
            return
        
        core = Orchestrator(api_key)
        query = "เปิดโหมด Verbose และแสดงขั้นตอนการคิด (Reasoning Trace)"
        
        response = core.run(query)
        print(f"\nผลลัพธ์:\n{response}\n")
        
        # ตรวจสอบว่ามีขั้นตอนการคิดหรือไม่
        has_reasoning = (
            "ขั้นตอน" in response or 
            "step" in response.lower() or 
            "trace" in response.lower() or
            "VERBOSE" in response or
            "Reasoning" in response
        )
        
        if has_reasoning:
            print("✅ ระบบแสดงขั้นตอนการคิด!")
        else:
            print("⚠️ ระบบอาจไม่ได้แสดงขั้นตอนการคิดอย่างชัดเจน")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
    
    print()


def test_multi_step_task():
    """Test 3: Multi-Step Task with Task Graph"""
    print("=" * 80)
    print("TEST 3: MULTI-STEP TASK - TASK GRAPH")
    print("=" * 80)
    print("คำสั่ง: 'คำนวณพื้นที่วงกลมรัศมี 7 เมตร แล้วแปลงผลลัพธ์เป็นตารางฟุต จากนั้นบันทึกค่าลงในความจำ'")
    print("-" * 80)
    
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ กรุณาตั้งค่า GROQ_API_KEY ในไฟล์ .env")
            return
        
        core = Orchestrator(api_key)
        memory = Memory()
        
        # Clear previous memory for clean test
        memory.save("last_result", None)
        
        query = "คำนวณพื้นที่วงกลมรัศมี 7 เมตร แล้วแปลงผลลัพธ์เป็นตารางฟุต จากนั้นบันทึกค่าลงในความจำ"
        
        print("\n📋 กำลังประมวลผล...")
        response = core.run(query)
        print(f"\nผลลัพธ์:\n{response}\n")
        
        # ตรวจสอบว่ามีการบันทึกในความจำหรือไม่
        mem_data = memory.load_all()
        last_result = mem_data.get('last_result', None)
        
        # ตรวจสอบว่าเป็น multi-step หรือไม่
        has_unit_conversion = (
            "ตารางฟุต" in response or 
            "sq ft" in response.lower() or 
            "ft²" in response.lower() or
            "square feet" in response.lower() or
            "153.9" in response  # Expected result
        )
        
        has_area_calc = (
            "พื้นที่" in response or 
            "area" in response.lower() or
            "Result:" in response  # Math result format
        )
        
        if last_result and str(last_result) != "None":
            print(f"✅ บันทึกในความจำสำเร็จ: {last_result}")
        else:
            print("⚠️ ไม่พบข้อมูลในความจำ")
        
        if has_unit_conversion:
            print("✅ ระบบทำการแปลงหน่วยเป็นตารางฟุต!")
        
        if has_area_calc:
            print("✅ ระบบคำนวณพื้นที่วงกลม!")
        
        # Verify it's a proper multi-step task
        if has_area_calc and has_unit_conversion and (last_result and str(last_result) != "None"):
            print("✅ Multi-step task completed successfully!")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
    
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("WORZ SOVEREIGN CORE - THAI LANGUAGE TEST SUITE")
    print("=" * 80 + "\n")
    
    # Run all three tests
    test_paradox()
    test_verbose_monologue()
    test_multi_step_task()
    
    print("=" * 80)
    print("สรุปผลการทดสอบ:")
    print("  1. Paradox Test - ทดสอบการตรวจจับข้อความขัดแย้งทางตรรกะ")
    print("  2. Verbose Mode - ทดสอบการแสดงขั้นตอนการคิด")
    print("  3. Multi-Step Task - ทดสอบการทำงานหลายขั้นตอนและ Task Graph")
    print("=" * 80)


if __name__ == "__main__":
    main()
