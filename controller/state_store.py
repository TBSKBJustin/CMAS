"""
State Store - Saves run state (JSON/SQLite)
"""

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class StateStore:
    """Persists workflow execution state"""
    
    def __init__(self, events_dir: str = "events"):
        self.events_dir = Path(events_dir)
    
    def save_module_result(self, event_id: str, module_name: str, result: Dict) -> None:
        """
        Save the result of a module execution
        
        Args:
            event_id: Event identifier
            module_name: Name of the module
            result: Module execution result dictionary
        """
        event_path = self.events_dir / event_id
        if not event_path.exists():
            raise ValueError(f"Event directory not found: {event_id}")
        
        # Save to logs directory
        result_file = event_path / "logs" / f"{module_name}_result.json"
        result["saved_at"] = datetime.now().isoformat()
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    def get_module_result(self, event_id: str, module_name: str) -> Optional[Dict]:
        """
        Retrieve the result of a previous module execution
        
        Args:
            event_id: Event identifier
            module_name: Name of the module
            
        Returns:
            Module result dictionary or None if not found
        """
        result_file = self.events_dir / event_id / "logs" / f"{module_name}_result.json"
        if not result_file.exists():
            return None
        
        with open(result_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_workflow_state(self, event_id: str, results: Dict) -> None:
        """
        Save the overall workflow execution state
        
        Args:
            event_id: Event identifier
            results: Dictionary of all module results
        """
        event_path = self.events_dir / event_id
        if not event_path.exists():
            raise ValueError(f"Event directory not found: {event_id}")
        
        state_file = event_path / "logs" / "workflow_state.json"
        state = {
            "event_id": event_id,
            "completed_at": datetime.now().isoformat(),
            "module_results": results,
            "overall_status": self._compute_overall_status(results)
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def get_workflow_state(self, event_id: str) -> Optional[Dict]:
        """Retrieve overall workflow state"""
        state_file = self.events_dir / event_id / "logs" / "workflow_state.json"
        if not state_file.exists():
            return None
        
        with open(state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _compute_overall_status(self, results: Dict) -> str:
        """
        Compute overall workflow status from module results
        
        Returns:
            One of: "success", "partial", "failed"
        """
        if not results:
            return "failed"
        
        statuses = [r.get("status", "unknown") for r in results.values()]
        
        if all(s == "success" for s in statuses):
            return "success"
        elif any(s == "success" for s in statuses):
            return "partial"
        else:
            return "failed"
