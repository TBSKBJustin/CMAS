"""
Workflow Controller - Orchestrates modules, queue, and retries
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from controller.event_manager import EventManager
from controller.state_store import StateStore


class WorkflowController:
    """Main orchestrator for the Church Media Automation System"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.event_manager = EventManager()
        self.state_store = StateStore()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("WorkflowController")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def run_event(self, event_id: str, force: bool = False) -> Dict:
        """
        Run workflow for a specific event
        
        Args:
            event_id: Event identifier (e.g., "2026-01-26_0900_sunday-service")
            force: Force re-run even if modules already succeeded
            
        Returns:
            Results dictionary with module statuses
        """
        self.logger.info(f"Starting workflow for event: {event_id}")
        
        # Load event configuration
        event_config = self.event_manager.load_event(event_id)
        if not event_config:
            raise ValueError(f"Event not found: {event_id}")
        
        # Check which modules are enabled
        enabled_modules = self._get_enabled_modules(event_config)
        self.logger.info(f"Enabled modules: {enabled_modules}")
        
        # Run modules in sequence
        results = {}
        for module_name in enabled_modules:
            try:
                result = self._run_module(event_id, module_name, event_config, force)
                results[module_name] = result
                self.state_store.save_module_result(event_id, module_name, result)
            except Exception as e:
                self.logger.error(f"Module {module_name} failed: {str(e)}")
                results[module_name] = {"status": "failed", "error": str(e)}
        
        # Save final workflow state
        self.state_store.save_workflow_state(event_id, results)
        
        return results
    
    def _get_enabled_modules(self, event_config: Dict) -> List[str]:
        """Extract enabled modules from event configuration"""
        modules_config = event_config.get("modules", {})
        return [name for name, enabled in modules_config.items() if enabled]
    
    def _run_module(self, event_id: str, module_name: str, event_config: Dict, force: bool) -> Dict:
        """
        Execute a single module
        
        Args:
            event_id: Event identifier
            module_name: Name of the module to run
            event_config: Full event configuration
            force: Force re-run if already completed
            
        Returns:
            Module execution result
        """
        # Check if already completed (unless force=True)
        if not force:
            existing_result = self.state_store.get_module_result(event_id, module_name)
            if existing_result and existing_result.get("status") == "success":
                self.logger.info(f"Module {module_name} already completed, skipping")
                return existing_result
        
        self.logger.info(f"Running module: {module_name}")
        
        # Module routing logic (to be implemented)
        # This is where we'd call the actual module implementations
        
        return {
            "status": "success",
            "message": f"Module {module_name} completed",
            "timestamp": "2026-01-26T09:00:00Z"
        }


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Church Media Automation Workflow Controller')
    parser.add_argument('command', choices=['run', 'status', 'list'], help='Command to execute')
    parser.add_argument('--event', help='Event ID to process')
    parser.add_argument('--force', action='store_true', help='Force re-run of completed modules')
    
    args = parser.parse_args()
    
    controller = WorkflowController()
    
    if args.command == 'run':
        if not args.event:
            print("Error: --event required for 'run' command")
            return
        results = controller.run_event(args.event, force=args.force)
        print(json.dumps(results, indent=2))
    elif args.command == 'status':
        print("Status command not yet implemented")
    elif args.command == 'list':
        print("List command not yet implemented")


if __name__ == '__main__':
    main()
