"""
OBS Monitor - Watches recording folder for new files
"""

import time
import logging
from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class RecordingHandler(FileSystemEventHandler):
    """Handles file system events for new recordings"""
    
    def __init__(self, callback: Callable[[str], None], extensions: tuple = ('.mp4', '.mkv', '.mov')):
        self.callback = callback
        self.extensions = extensions
        self.logger = logging.getLogger("RecordingHandler")
    
    def on_created(self, event: FileSystemEvent):
        """Called when a new file is created"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix.lower() in self.extensions:
            self.logger.info(f"New recording detected: {file_path}")
            self.callback(str(file_path))


class OBSMonitor:
    """Monitors OBS recording folder for new recordings"""
    
    def __init__(self, watch_path: str, callback: Callable[[str], None]):
        """
        Initialize OBS monitor
        
        Args:
            watch_path: Path to OBS recording folder
            callback: Function to call when new recording is detected
        """
        self.watch_path = Path(watch_path)
        self.callback = callback
        self.observer: Optional[Observer] = None
        self.logger = self._setup_logger()
        
        if not self.watch_path.exists():
            raise ValueError(f"Watch path does not exist: {watch_path}")
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("OBSMonitor")
        logger.setLevel(logging.INFO)
        return logger
    
    def start(self):
        """Start monitoring the recording folder"""
        self.logger.info(f"Starting OBS monitor on: {self.watch_path}")
        
        event_handler = RecordingHandler(self.callback)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.watch_path), recursive=False)
        self.observer.start()
        
        self.logger.info("OBS monitor started successfully")
    
    def stop(self):
        """Stop monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.logger.info("OBS monitor stopped")
    
    def run(self):
        """Run monitor in blocking mode"""
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()


def main():
    """CLI entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OBS Recording Monitor')
    parser.add_argument('watch_path', help='Path to OBS recording folder')
    args = parser.parse_args()
    
    def on_recording_detected(file_path: str):
        print(f"New recording: {file_path}")
        # Here you would typically trigger the workflow controller
    
    monitor = OBSMonitor(args.watch_path, on_recording_detected)
    monitor.run()


if __name__ == '__main__':
    main()
