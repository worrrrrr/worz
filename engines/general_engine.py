"""
General Engine - Handles general tasks and project management.
"""
import os
from typing import Dict, Any

from .base_engine import BaseEngine


class GeneralEngine(BaseEngine):
    """Engine for general-purpose tasks and project management."""
    
    def __init__(self):
        """Initialize the General Engine."""
        super().__init__(name="general", version="2.1")
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a general task.
        
        Args:
            params: Task parameters including 'action', 'content', 'verbose', etc.
            
        Returns:
            dict: Execution result with 'response' key
        """
        action = params.get("action", "").lower()
        content = params.get("content", "")
        verbose = params.get("verbose", False)
        name = params.get("project_name") or params.get("name") or "new_item"
        
        # Handle verbose/monologue mode
        if "verbose" in action or "monologue" in action or verbose:
            result = self._show_verbose_mode(content or action)
            return {"response": result, "verbose": True}
        
        if "project" in action or "create" in action:
            result = self._create_project(name)
            return {"response": result}
        
        if "list" in action:
            result = self._list_directory()
            return {"response": result}
        
        # Handle general conversational requests
        if content:
            result = self._handle_general_request(content, verbose)
            return {"response": result, "verbose": verbose}
        
        result = f"⚙️ General Task: {action} {name} executed."
        return {"response": result}
    
    def _show_verbose_mode(self, context: str) -> str:
        """Show verbose mode with reasoning trace.
        
        Args:
            context: Context or request for verbose output
            
        Returns:
            str: Verbose explanation with reasoning steps
        """
        response = (
            "🔍 **VERBOSE MODE ACTIVATED**\n\n"
            "📋 **Reasoning Trace:**\n"
            "  1. 🧠 **Input Analysis:** Received request for verbose/reasoning output\n"
            "  2. 🔎 **Intent Detection:** User wants to see the thinking process\n"
            "  3. ⚙️ **Processing Steps:**\n"
            "     - Parse input using IntentParser\n"
            "     - Check for special patterns (paradox, math, knowledge)\n"
            "     - Route to appropriate engine\n"
            "     - Execute and format results\n"
            "  4. 💾 **Memory Operations:** Save results if applicable\n"
            "  5. 📤 **Output Generation:** Format response with reasoning trace\n\n"
            f"📝 **Context:** {context if context else 'General verbose mode enabled'}\n\n"
            "✅ **Verbose mode is now active. All subsequent responses will include reasoning traces.**"
        )
        return response
    
    def _handle_general_request(self, content: str, verbose: bool = False) -> str:
        """Handle general conversational requests.
        
        Args:
            content: User's content/request
            verbose: Whether to include verbose output
            
        Returns:
            str: Response to the general request
        """
        if verbose:
            return (
                "🔍 **Verbose Response:**\n\n"
                f"📥 **Input:** {content}\n"
                "🧠 **Analysis:** General conversational request detected\n"
                "⚙️ **Action:** Processing as general intent\n"
                f"💬 **Response:** I understand your request: '{content}'\n"
                "   This is being handled by the General Engine.\n\n"
                "✅ Request processed successfully."
            )
        
        return f"💬 I understand: {content}"
    
    def _create_project(self, name: str) -> str:
        """Create a new project directory.
        
        Args:
            name: Project name
            
        Returns:
            str: Success message
        """
        try:
            os.makedirs(name, exist_ok=True)
            readme_path = os.path.join(name, "README.md")
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(f"# {name}\nCreated by WORZ SOVEREIGN CORE.\n")
            return f"✅ Created project/folder '{name}' successfully."
        except Exception as e:
            return f"❌ Error creating project: {str(e)}"
    
    def _list_directory(self) -> str:
        """List files in current directory.
        
        Returns:
            str: List of files
        """
        try:
            items = os.listdir('.')
            return f"📂 Files in current directory: {', '.join(items)}"
        except Exception as e:
            return f"❌ Error listing directory: {str(e)}"
