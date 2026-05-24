import os
from dotenv import load_dotenv
from core.orchestrator import Orchestrator

load_dotenv()

def main():
    # Initialize the Sovereign Core
    core = Orchestrator(os.getenv("GROQ_API_KEY"))
    
    print("--- WORZ SOVEREIGN CORE v2.0 READY ---")
    while True:
        user_input = input("\n[Input] >>> ")
        if user_input.lower() in ['exit', 'quit']: break
        
        # Orchestra ทำงานเบื้องหลังทั้งหมด
        response = core.run(user_input)
        print(f"\n[Result] -> {response}")

if __name__ == "__main__":
    main()