
import os
from dotenv import load_dotenv
from core.orchestrator import Orchestrator

load_dotenv()

print("=" * 70)
print("🧪 WORZ SOVEREIGN CORE - END-TO-END TEST")
print("=" * 70)

# ใช้ API key จาก environment หรือ mock สำหรับทดสอบ
api_key = os.getenv("GROQ_API_KEY", "test_key")

try:
    core = Orchestrator(api_key)
    print("\n✅ Orchestrator initialized successfully\n")
    
    # Test cases
    tests = [
        ("2+2", "Fast Track Math"),
        ("สูตรพื้นที่วงกลม", "Knowledge Base - Formula Query"),
        ("กฎของนิวตัน", "Knowledge Base - Physics Law"),
        ("modus ponens", "Knowledge Base - Logic Rule"),
        ("ขั้นตอนการแก้สมการ", "Knowledge Base - Procedure"),
    ]
    
    for query, description in tests:
        print(f"\n📝 Test: {description}")
        print(f"   Input: {query}")
        try:
            result = core.run(query)
            print(f"   Output: {result[:150]}..." if len(str(result)) > 150 else f"   Output: {result}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Initialization error: {e}")
    print("Note: Some tests may require a valid GROQ_API_KEY")
