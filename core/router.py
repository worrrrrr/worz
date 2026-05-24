"""
Router - Dispatches intents to appropriate engines.
"""
import importlib
from typing import Dict, Any, Optional


class Router:
    """Routes parsed intents to corresponding engine implementations."""
    
    def __init__(self):
        """Initialize router with tool-to-engine mapping."""
        self.mapping = {
            "math_engine": "engines.math_engine.MathEngine",
            "logic_engine": "engines.logic_engine.LogicEngine",
            "unit_engine": "engines.unit_engine.UnitEngine",
            "project_manager": "engines.general_engine.GeneralEngine",
            "device_controller": "engines.general_engine.GeneralEngine",
        }
        self._engine_cache = {}
    
    def dispatch(self, intent: Dict[str, Any]) -> Any:
        """Dispatch intent to appropriate engine.
        
        Args:
            intent: Parsed intent dictionary with 'tool' and 'params' keys
            
        Returns:
            Engine execution result or error message
        """
        tool = intent.get("tool")
        
        # Handle general/conversational intents
        if tool == "general":
            params = intent.get("params", {})
            # If it's a verbose action, route to GeneralEngine
            if params.get("action") == "verbose" or params.get("verbose"):
                try:
                    engine = self._get_engine(self.mapping["project_manager"])
                    return engine.execute(params)
                except Exception as e:
                    return f"Router Error: {str(e)}"
            return params.get("content") or params.get("action") or "I understand."
        
        # Check if tool is supported
        target = self.mapping.get(tool)
        if not target:
            return f"Tool '{tool}' is not implemented yet."
        
        # Execute the engine
        try:
            engine = self._get_engine(target)
            return engine.execute(intent.get("params", {}))
        except Exception as e:
            return f"Router Error: {str(e)}"
    
    def _get_engine(self, target: str):
        """Load and cache engine instance.
        
        Args:
            target: Module path string (e.g., 'engines.math_engine.MathEngine')
            
        Returns:
            Engine instance
        """
        if target in self._engine_cache:
            return self._engine_cache[target]
        
        mod_name, cls_name = target.rsplit(".", 1)
        module = importlib.import_module(mod_name)
        engine_class = getattr(module, cls_name)
        engine = engine_class()
        
        self._engine_cache[target] = engine
        return engine
