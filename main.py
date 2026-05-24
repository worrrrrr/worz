"""
WORZ SOVEREIGN CORE - Main Entry Point
Version: 3.0
"""
import os
from typing import Optional
from dotenv import load_dotenv
from core.orchestrator import Orchestrator, Colors

load_dotenv()


def create_orchestrator(api_key: Optional[str] = None) -> Orchestrator:
    """Create and initialize the Orchestrator instance.
    
    Args:
        api_key: API key for Groq. If None, will use GROQ_API_KEY env var.
        
    Returns:
        Orchestrator: Initialized orchestrator instance
    """
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("API key required. Set GROQ_API_KEY environment variable.")
    return Orchestrator(key)


def confirm_action(action_description: str, risk_level: int) -> bool:
    """Request manual confirmation from user for high-risk actions.
    
    Args:
        action_description: Description of the action to be performed
        risk_level: Risk level (1-5) detected by Guardrails
        
    Returns:
        bool: True if user confirms, False otherwise
    """
    print(f"\n{Colors.RED}⚠️  SECURITY ALERT ⚠️{Colors.RESET}")
    print(f"{Colors.YELLOW}Risk Level: {risk_level}/5{Colors.RESET}")
    print(f"{Colors.BOLD}Action:{Colors.RESET} {action_description}")
    print(f"\n{Colors.RED}Guardrails has detected potential security risks.{Colors.RESET}")
    print(f"{Colors.CYAN}Do you want to proceed? (yes/no){Colors.RESET}")
    
    while True:
        try:
            user_input = input(f"{Colors.CYAN}[Confirm] >>> {Colors.RESET}").strip().lower()
            if user_input in ['yes', 'y']:
                print(f"{Colors.GREEN}✓ Action confirmed by user{Colors.RESET}\n")
                return True
            elif user_input in ['no', 'n']:
                print(f"{Colors.YELLOW}✗ Action cancelled by user{Colors.RESET}\n")
                return False
            else:
                print(f"{Colors.YELLOW}Please enter 'yes' or 'no'{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}✗ Confirmation cancelled{Colors.RESET}\n")
            return False


def main():
    """Main interactive loop for the WORZ SOVEREIGN CORE."""
    try:
        core = create_orchestrator()
    except ValueError as e:
        print(f"❌ Error: {e}")
        return
    
    print("╔══════════════════════════════════════════════╗")
    print("║   WORZ SOVEREIGN CORE v3.0 READY            ║")
    print("║   Features: Self-Reflection | Dynamic Plan  ║")
    print("║           Verifier Mode | Guardrails        ║")
    print("║           Memory Ranking | ANSI Colors      ║")
    print("╚══════════════════════════════════════════════╝")
    print("Commands: 'exit' or 'quit' to stop\n")
    
    while True:
        try:
            user_input = input(f"{Colors.CYAN}[Input] >>> {Colors.RESET}").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print(f"{Colors.YELLOW}👋 Goodbye!{Colors.RESET}")
                break
            
            if not user_input:
                continue
                
            # Check for adversarial patterns before processing
            from core.knowledge_base import get_knowledge_base
            kb = get_knowledge_base()
            adversarial_check = kb.check_adversarial_input(user_input)
            
            if adversarial_check["is_adversarial"] and adversarial_check["risk_level"] >= 3:
                if not confirm_action(
                    f"Detected adversarial pattern: {adversarial_check['detected_patterns'][0]['pattern']}",
                    adversarial_check["risk_level"]
                ):
                    continue
            
            response = core.run(user_input, return_with_trace=False)
            print(f"\n{Colors.BOLD}{Colors.GREEN}[Result]{Colors.RESET} -> {response}\n")
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}👋 Interrupted. Goodbye!{Colors.RESET}")
            break
        except Exception as e:
            print(f"\n{Colors.RED}❌ Error: {str(e)}{Colors.RESET}\n")


if __name__ == "__main__":
    main()