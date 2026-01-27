"""
Manual Ingest - Validate and attach selected file
"""

import os
import shutil
from pathlib import Path
from typing import Optional


class ManualIngest:
    """Handles manual file selection and validation"""
    
    SUPPORTED_FORMATS = {'.mp4', '.mkv', '.mov', '.avi', '.flv', '.webm'}
    
    def __init__(self):
        pass
    
    def validate_file(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        Validate that a file exists and is a supported video format
        
        Args:
            file_path: Path to video file
            
        Returns:
            (is_valid, error_message)
        """
        path = Path(file_path)
        
        # Check existence
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        # Check if it's a file
        if not path.is_file():
            return False, f"Path is not a file: {file_path}"
        
        # Check format
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return False, f"Unsupported format: {path.suffix}. Supported: {self.SUPPORTED_FORMATS}"
        
        # Check file size (should not be 0)
        if path.stat().st_size == 0:
            return False, "File is empty (0 bytes)"
        
        return True, None
    
    def attach_to_event(
        self, 
        source_path: str, 
        event_path: str, 
        copy: bool = True
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Attach a video file to an event
        
        Args:
            source_path: Path to source video file
            event_path: Path to event directory
            copy: If True, copy the file; if False, move it
            
        Returns:
            (success, error_message, destination_path)
        """
        # Validate source file
        is_valid, error = self.validate_file(source_path)
        if not is_valid:
            return False, error, None
        
        # Create input directory if needed
        input_dir = Path(event_path) / "input"
        input_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine destination path
        source = Path(source_path)
        dest_path = input_dir / source.name
        
        # Handle name conflicts
        counter = 1
        while dest_path.exists():
            stem = source.stem
            suffix = source.suffix
            dest_path = input_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        # Copy or move file
        try:
            if copy:
                shutil.copy2(source, dest_path)
            else:
                shutil.move(str(source), dest_path)
            
            return True, None, str(dest_path)
        
        except Exception as e:
            return False, f"Failed to transfer file: {str(e)}", None
    
    def get_info(self, file_path: str) -> dict:
        """
        Get basic file information
        
        Args:
            file_path: Path to video file
            
        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        
        if not path.exists():
            return {"error": "File not found"}
        
        stat = path.stat()
        
        return {
            "name": path.name,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "extension": path.suffix,
            "modified": stat.st_mtime
        }


def main():
    """CLI entry point for testing"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Manual Video Ingestion')
    parser.add_argument('command', choices=['validate', 'attach', 'info'])
    parser.add_argument('--file', required=True, help='Path to video file')
    parser.add_argument('--event', help='Event directory path (for attach command)')
    parser.add_argument('--move', action='store_true', help='Move instead of copy')
    
    args = parser.parse_args()
    
    ingest = ManualIngest()
    
    if args.command == 'validate':
        is_valid, error = ingest.validate_file(args.file)
        if is_valid:
            print("✓ File is valid")
        else:
            print(f"✗ Validation failed: {error}")
    
    elif args.command == 'attach':
        if not args.event:
            print("Error: --event required for attach command")
            return
        
        success, error, dest_path = ingest.attach_to_event(
            args.file, 
            args.event, 
            copy=not args.move
        )
        
        if success:
            print(f"✓ File attached: {dest_path}")
        else:
            print(f"✗ Attach failed: {error}")
    
    elif args.command == 'info':
        info = ingest.get_info(args.file)
        print(json.dumps(info, indent=2))


if __name__ == '__main__':
    main()
