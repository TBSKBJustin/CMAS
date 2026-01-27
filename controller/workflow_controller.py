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
        
        # Module routing logic
        try:
            if module_name == "thumbnail_ai":
                return self._run_thumbnail_ai(event_id, event_config)
            elif module_name == "thumbnail_compose":
                return self._run_thumbnail_compose(event_id, event_config)
            elif module_name == "subtitles":
                return self._run_subtitles(event_id, event_config)
            elif module_name == "publish_youtube":
                return self._run_publish_youtube(event_id, event_config)
            elif module_name == "publish_website":
                return self._run_publish_website(event_id, event_config)
            elif module_name == "archive":
                return self._run_archive(event_id, event_config)
            else:
                return {
                    "status": "skipped",
                    "message": f"Unknown module: {module_name}",
                    "timestamp": self._get_timestamp()
                }
        except Exception as e:
            self.logger.error(f"Module {module_name} failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": self._get_timestamp()
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _run_thumbnail_ai(self, event_id: str, event_config: Dict) -> Dict:
        """Run AI thumbnail generation module"""
        self.logger.info("Running thumbnail AI generation...")
        # Placeholder for actual implementation
        return {
            "status": "success",
            "message": "AI thumbnail generated",
            "timestamp": self._get_timestamp()
        }
    
    def _run_thumbnail_compose(self, event_id: str, event_config: Dict) -> Dict:
        """Run thumbnail composition module"""
        self.logger.info("Running thumbnail composition...")
        
        try:
            from modules.thumbnail.composer_pillow import ThumbnailComposer
            
            # Setup output directory
            event_dir = Path("events") / event_id
            output_dir = event_dir / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Get event details
            title = event_config.get("title", "Untitled")
            scripture = event_config.get("scripture", "")
            speaker = event_config.get("speaker", "")
            
            # Output path
            thumbnail_path = output_dir / "thumbnail.jpg"
            
            # Initialize composer
            composer = ThumbnailComposer()
            
            # Look for optional assets
            assets_dir = Path("assets")
            background = None
            logo = None
            
            # Try to find a background image
            bg_dir = assets_dir / "backgrounds"
            if bg_dir.exists():
                bg_files = list(bg_dir.glob("*.jpg")) + list(bg_dir.glob("*.png"))
                if bg_files:
                    background = str(bg_files[0])
            
            # Try to find a logo
            logo_dir = assets_dir / "logos"
            if logo_dir.exists():
                logo_files = list(logo_dir.glob("*.png"))
                if logo_files:
                    logo = str(logo_files[0])
            
            # Compose thumbnail
            success, error = composer.compose(
                output_path=str(thumbnail_path),
                title=title,
                scripture=scripture if scripture else None,
                background=background,
                logo=logo
            )
            
            if success:
                self.logger.info(f"Thumbnail created: {thumbnail_path}")
                return {
                    "status": "success",
                    "message": "Thumbnail composed successfully",
                    "output_file": str(thumbnail_path),
                    "timestamp": self._get_timestamp()
                }
            else:
                self.logger.error(f"Thumbnail composition failed: {error}")
                return {
                    "status": "failed",
                    "error": error,
                    "timestamp": self._get_timestamp()
                }
        
        except Exception as e:
            self.logger.error(f"Thumbnail module error: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": self._get_timestamp()
            }
    
    def _run_subtitles(self, event_id: str, event_config: Dict) -> Dict:
        """Run subtitle generation module"""
        self.logger.info("Running subtitle generation...")
        
        try:
            from modules.subtitles.engine_whispercpp import WhisperCppEngine
            
            # Get input video
            video_files = event_config.get("inputs", {}).get("video_files", [])
            if not video_files:
                return {
                    "status": "failed",
                    "error": "No input video found",
                    "timestamp": self._get_timestamp()
                }
            
            video_path = video_files[0]  # Use first video
            
            # Setup output directory
            event_dir = Path("events") / event_id
            output_dir = event_dir / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Get language and model from event config
            language = event_config.get("language", "auto")
            model = event_config.get("whisper_model", "base")
            
            self.logger.info(f"Using Whisper model: {model}, Language: {language}")
            
            # Initialize engine with selected model
            engine = WhisperCppEngine(model=model)
            
            # Check if model exists
            if not engine.check_model():
                return {
                    "status": "failed",
                    "error": f"Model '{model}' not found. Please download it first.",
                    "timestamp": self._get_timestamp()
                }
            
            # Generate subtitles
            success, error, output_files = engine.generate_subtitles(
                video_path=video_path,
                output_dir=str(output_dir),
                language=language,
                formats=["srt", "vtt"]
            )
            
            if success:
                self.logger.info(f"Subtitles generated: {output_files}")
                return {
                    "status": "success",
                    "message": "Subtitles generated successfully",
                    "model": model,
                    "language": language,
                    "output_files": output_files,
                    "timestamp": self._get_timestamp()
                }
            else:
                self.logger.error(f"Subtitle generation failed: {error}")
                return {
                    "status": "failed",
                    "error": error,
                    "timestamp": self._get_timestamp()
                }
        
        except Exception as e:
            self.logger.error(f"Subtitle module error: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": self._get_timestamp()
            }
    
    def _run_publish_youtube(self, event_id: str, event_config: Dict) -> Dict:
        """Run YouTube publishing module"""
        self.logger.info("Running YouTube upload...")
        # Placeholder for actual implementation
        return {
            "status": "success",
            "message": "Published to YouTube",
            "timestamp": self._get_timestamp()
        }
    
    def _run_publish_website(self, event_id: str, event_config: Dict) -> Dict:
        """Run website publishing module"""
        self.logger.info("Running website publishing...")
        # Placeholder for actual implementation
        return {
            "status": "success",
            "message": "Published to website",
            "timestamp": self._get_timestamp()
        }
    
    def _run_archive(self, event_id: str, event_config: Dict) -> Dict:
        """Run archive module"""
        self.logger.info("Running archive...")
        # Placeholder for actual implementation
        return {
            "status": "success",
            "message": "Archived successfully",
            "timestamp": self._get_timestamp()
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
