"""
Memory - Persistent storage for conversation context and results.
"""
import json
import os
from typing import Any, Dict


class Memory:
    """Manages persistent memory storage using JSON files."""
    
    def __init__(self, path: str = "data/memory.json"):
        """Initialize memory with file path.
        
        Args:
            path: Path to the memory JSON file
        """
        self.path = path
        self._ensure_directory()
        self._initialize_file()
    
    def _ensure_directory(self):
        """Ensure the directory for memory file exists."""
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
    
    def _initialize_file(self):
        """Initialize memory file with default structure if it doesn't exist."""
        if not os.path.exists(self.path):
            default_data = {"history": [], "last_result": 0}
            with open(self.path, "w") as f:
                json.dump(default_data, f)
    
    def save(self, key: str, value: Any):
        """Save a key-value pair to memory.
        
        Args:
            key: Storage key
            value: Value to store
        """
        data = self.load_all()
        data[key] = value
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)
    
    def load_all(self) -> Dict[str, Any]:
        """Load all memory data.
        
        Returns:
            Dictionary containing all stored data
        """
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"history": [], "last_result": 0}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific value from memory.
        
        Args:
            key: Storage key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        data = self.load_all()
        return data.get(key, default)
    
    def add_to_history(self, entry: Dict[str, Any]):
        """Add an entry to the history.
        
        Args:
            entry: History entry dictionary
        """
        data = self.load_all()
        if "history" not in data:
            data["history"] = []
        data["history"].append(entry)
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)
    
    def add_to_reasoning_history(self, entry: Dict[str, Any]):
        """Add an entry to the reasoning_history.
        
        Args:
            entry: Reasoning history entry dictionary
        """
        data = self.load_all()
        if "reasoning_history" not in data:
            data["reasoning_history"] = []
        data["reasoning_history"].append(entry)
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)
    
    def limit_history(self, max_entries: int = 50):
        """Limit the history to prevent memory.json from growing too large.
        
        Args:
            max_entries: Maximum number of entries to keep (default: 50)
        """
        data = self.load_all()
        
        # Limit regular history
        if "history" in data and len(data["history"]) > max_entries:
            data["history"] = data["history"][-max_entries:]
        
        # Limit reasoning history
        if "reasoning_history" in data and len(data["reasoning_history"]) > max_entries:
            data["reasoning_history"] = data["reasoning_history"][-max_entries:]
        
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)
    
    def add(self, key: str, value: Any):
        """Alias for save method - adds a key-value pair to memory.
        
        Args:
            key: Storage key
            value: Value to store
        """
        self.save(key, value)
    
    def summarize_old_memories(self, threshold: float = 0.3):
        """Summarize old memories with low relevance score to save storage space.
        
        Args:
            threshold: Relevance score threshold below which memories will be summarized (default: 0.3)
            
        Returns:
            Dictionary with summary statistics
        """
        data = self.load_all()
        summarized_count = 0
        active_count = 0
        
        # Process history entries
        if "history" in data:
            new_history = []
            for entry in data["history"]:
                relevance = entry.get("relevance", 1.0)
                if relevance < threshold:
                    # Summarize this entry
                    if isinstance(entry, dict) and "content" in entry:
                        original_content = str(entry.get("content", ""))
                        entry["content"] = f"[SUMMARIZED] {original_content[:50]}..." if len(original_content) > 50 else f"[SUMMARIZED] {original_content}"
                        entry["summarized"] = True
                        summarized_count += 1
                    else:
                        summarized_count += 1
                else:
                    active_count += 1
                new_history.append(entry)
            data["history"] = new_history
        
        # Process reasoning_history entries
        if "reasoning_history" in data:
            new_reasoning = []
            for entry in data["reasoning_history"]:
                relevance = entry.get("relevance", 1.0)
                if relevance < threshold:
                    # Summarize this entry
                    if isinstance(entry, dict) and "steps" in entry:
                        original_steps = entry.get("steps", [])
                        entry["steps"] = [f"[SUMMARIZED] Step {i+1}" for i in range(min(3, len(original_steps)))]
                        entry["summarized"] = True
                        summarized_count += 1
                    else:
                        summarized_count += 1
                else:
                    active_count += 1
                new_reasoning.append(entry)
            data["reasoning_history"] = new_reasoning
        
        # Save updated data
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)
        
        return {
            "summarized_count": summarized_count,
            "active_count": active_count,
            "status": "success",
            "threshold_used": threshold
        }
