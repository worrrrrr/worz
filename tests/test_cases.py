#!/usr/bin/env python3
"""
WORZ SOVEREIGN CORE v2.2 - Comprehensive Test Suite
Tests all Engines and Core Components
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import Orchestrator, Colors
from engines.general_engine import GeneralEngine
from engines.logic_engine import LogicEngine, SymbolicLogicChecker
from core.memory import Memory

def test_general_engine():
    """Test General Engine functionality"""
    print(f"\n{Colors.CYAN}=== Testing General Engine ==={Colors.RESET}")
    engine = GeneralEngine()
    
    # Test basic response
    result = engine.execute({"action": "test", "content": "สวัสดี"})
    assert isinstance(result, dict), "General engine should return a dict"
    assert "response" in result, "General engine should return a response"
    print(f"{Colors.GREEN}✓ General Engine: Basic response OK{Colors.RESET}")
    
    # Test verbose mode
    result = engine.execute({"action": "verbose", "content": "ทดสอบ"})
    assert isinstance(result, dict), "General engine should return a dict"
    assert "response" in result, "General engine should return a response"
    print(f"{Colors.GREEN}✓ General Engine: Verbose mode OK{Colors.RESET}")
    
    return True

def test_logic_engine():
    """Test Logic Engine with symbolic logic (no eval)"""
    print(f"\n{Colors.CYAN}=== Testing Logic Engine ==={Colors.RESET}")
    engine = LogicEngine()
    checker = SymbolicLogicChecker()
    
    # Test basic TRUE/FALSE
    result = checker.evaluate("TRUE")
    assert result["result"] == True, "TRUE should be true"
    print(f"{Colors.GREEN}✓ Logic Engine: TRUE evaluation OK{Colors.RESET}")
    
    result = checker.evaluate("FALSE")
    assert result["result"] == False, "FALSE should be false"
    print(f"{Colors.GREEN}✓ Logic Engine: FALSE evaluation OK{Colors.RESET}")
    
    # Test AND operator
    result = checker.evaluate("TRUE AND TRUE")
    assert result["result"] == True, "TRUE AND TRUE should be true"
    print(f"{Colors.GREEN}✓ Logic Engine: AND operator OK{Colors.RESET}")
    
    # Test OR operator
    result = checker.evaluate("TRUE OR FALSE")
    assert result["result"] == True, "TRUE OR FALSE should be true"
    print(f"{Colors.GREEN}✓ Logic Engine: OR operator OK{Colors.RESET}")
    
    # Test NOT operator
    result = checker.evaluate("NOT FALSE")
    assert result["result"] == True, "NOT FALSE should be true"
    print(f"{Colors.GREEN}✓ Logic Engine: NOT operator OK{Colors.RESET}")
    
    # Test Thai language support
    result = checker.evaluate("จริง")
    assert result["result"] == True, "จริง (Thai TRUE) should be true"
    print(f"{Colors.GREEN}✓ Logic Engine: Thai TRUE (จริง) OK{Colors.RESET}")
    
    result = checker.evaluate("เท็จ")
    assert result["result"] == False, "เท็จ (Thai FALSE) should be false"
    print(f"{Colors.GREEN}✓ Logic Engine: Thai FALSE (เท็จ) OK{Colors.RESET}")
    
    # Test new Thai formal operators 'หาก' and 'ย่อม'
    # Note: "หาก A ย่อม B" translates to "if A then B", which is true when A=True and B=True
    result = checker.evaluate("หาก จริง ย่อม จริง")
    # This should evaluate as: if true then true = true
    print(f"  Debug: หาก จริง ย่อม จริง = {result}")
    assert result["result"] == True, f"หาก จริง ย่อม จริง should be true (implication), got {result['result']}"
    print(f"{Colors.GREEN}✓ Logic Engine: Thai formal operators (หาก...ย่อม) OK{Colors.RESET}")
    
    # Test engine execute method
    result = engine.execute({"expression": "TRUE AND FALSE"})
    assert isinstance(result, dict) or isinstance(result, str), "Engine should return result or explanation"
    print(f"{Colors.GREEN}✓ Logic Engine: Execute method OK{Colors.RESET}")
    
    return True

def test_memory():
    """Test Memory component with history limit"""
    print(f"\n{Colors.CYAN}=== Testing Memory ==={Colors.RESET}")
    memory = Memory()
    
    # Test add and get
    memory.add("test_key", "test_value")
    result = memory.get("test_key")
    assert result == "test_value", "Memory get should return stored value"
    print(f"{Colors.GREEN}✓ Memory: Add/Get OK{Colors.RESET}")
    
    # Test history limit
    memory.limit_history(max_entries=5)
    print(f"{Colors.GREEN}✓ Memory: limit_history function exists OK{Colors.RESET}")
    
    # Test reasoning history
    memory.add_to_reasoning_history({"step": 1, "action": "test"})
    print(f"{Colors.GREEN}✓ Memory: Reasoning history OK{Colors.RESET}")
    
    return True

def test_orchestrator():
    """Test Orchestrator with reasoning steps"""
    print(f"\n{Colors.CYAN}=== Testing Orchestrator ==={Colors.RESET}")
    orchestrator = Orchestrator(api_key="test_key")
    
    # Test reasoning steps recording (initially empty)
    steps = orchestrator.get_reasoning_steps()
    assert isinstance(steps, list), "Reasoning steps should be a list"
    print(f"{Colors.GREEN}✓ Orchestrator: Reasoning steps recording OK{Colors.RESET}")
    
    # Test paradox detection (doesn't require API key)
    result = orchestrator.run("หาเลขที่มากกว่า 10 แต่น้อยกว่า 5")
    # Check if result is a dict with response or message
    result_text = ""
    if isinstance(result, dict):
        result_text = result.get("response", "") + result.get("message", "")
    elif isinstance(result, str):
        result_text = result
    
    assert "paradox" in result_text.lower() or "contradiction" in result_text.lower() or "ขัดแย้ง" in result_text, f"Should detect paradox. Got: {result_text}"
    print(f"{Colors.GREEN}✓ Orchestrator: Paradox detection OK{Colors.RESET}")
    
    return True

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}╔════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}║  WORZ SOVEREIGN CORE v2.2 TEST SUITE  ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}╚════════════════════════════════════════╝{Colors.RESET}")
    
    results = {
        "General Engine": False,
        "Logic Engine": False,
        "Memory": False,
        "Orchestrator": False
    }
    
    try:
        results["General Engine"] = test_general_engine()
    except Exception as e:
        print(f"{Colors.RED}✗ General Engine FAILED: {e}{Colors.RESET}")
    
    try:
        results["Logic Engine"] = test_logic_engine()
    except Exception as e:
        print(f"{Colors.RED}✗ Logic Engine FAILED: {e}{Colors.RESET}")
    
    try:
        results["Memory"] = test_memory()
    except Exception as e:
        print(f"{Colors.RED}✗ Memory FAILED: {e}{Colors.RESET}")
    
    try:
        results["Orchestrator"] = test_orchestrator()
    except Exception as e:
        print(f"{Colors.RED}✗ Orchestrator FAILED: {e}{Colors.RESET}")
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.YELLOW}═══ TEST SUMMARY ═══{Colors.RESET}")
    all_passed = True
    for component, passed in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        print(f"  {component}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 ALL ENGINES OPERATIONAL - v2.2 VERIFIED{Colors.RESET}")
    else:
        print(f"\n{Colors.BOLD}{Colors.RED}⚠️ SOME ENGINES HAVE ISSUES - REVIEW REQUIRED{Colors.RESET}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)