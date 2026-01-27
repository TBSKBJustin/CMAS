"""
Archiver - Optional storage move/cleanup
"""

import logging
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime


class Archiver:
    """Moves completed event outputs to archive storage"""
    
    def __init__(self, archive_root: str = "/archive/church-media"):
        """
        Initialize archiver
        
        Args:
            archive_root: Root path for archive storage (could be NAS)
        """
        self.archive_root = Path(archive_root)
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("Archiver")
        logger.setLevel(logging.INFO)
        return logger
    
    def archive_event(
        self,
        event_path: str,
        keep_local_copy: bool = True,
        compress: bool = False
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Archive an event to long-term storage
        
        Args:
            event_path: Path to event directory
            keep_local_copy: Keep local copy after archiving
            compress: Compress before archiving
            
        Returns:
            (success, error_message, archive_path)
        """
        try:
            event_path = Path(event_path)
            if not event_path.exists():
                return False, f"Event path not found: {event_path}", None
            
            self.logger.info(f"Archiving event: {event_path.name}")
            
            # Create archive directory structure
            year = datetime.now().year
            archive_dest = self.archive_root / str(year) / event_path.name
            archive_dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Archive
            if compress:
                archive_path = self._archive_compressed(event_path, archive_dest)
            else:
                archive_path = self._archive_copy(event_path, archive_dest)
            
            # Remove local copy if requested
            if not keep_local_copy:
                shutil.rmtree(event_path)
                self.logger.info(f"Removed local copy: {event_path}")
            
            self.logger.info(f"Archived to: {archive_path}")
            return True, None, str(archive_path)
        
        except Exception as e:
            self.logger.error(f"Archive failed: {e}")
            return False, str(e), None
    
    def _archive_copy(self, source: Path, dest: Path) -> Path:
        """Copy event directory to archive"""
        shutil.copytree(source, dest, dirs_exist_ok=True)
        return dest
    
    def _archive_compressed(self, source: Path, dest: Path) -> Path:
        """Compress and archive event"""
        import tarfile
        
        archive_file = dest.parent / f"{dest.name}.tar.gz"
        
        with tarfile.open(archive_file, "w:gz") as tar:
            tar.add(source, arcname=source.name)
        
        return archive_file
    
    def cleanup_old_events(
        self,
        events_dir: str,
        days_threshold: int = 90,
        dry_run: bool = True
    ) -> tuple[bool, Optional[str], list]:
        """
        Clean up old local event directories
        
        Args:
            events_dir: Events directory path
            days_threshold: Delete events older than this many days
            dry_run: If True, only list files without deleting
            
        Returns:
            (success, error_message, deleted_events)
        """
        try:
            from datetime import timedelta
            
            events_path = Path(events_dir)
            if not events_path.exists():
                return False, f"Events directory not found: {events_dir}", []
            
            threshold_date = datetime.now() - timedelta(days=days_threshold)
            deleted = []
            
            for event_dir in events_path.iterdir():
                if not event_dir.is_dir():
                    continue
                
                # Check modification time
                mtime = datetime.fromtimestamp(event_dir.stat().st_mtime)
                
                if mtime < threshold_date:
                    if dry_run:
                        self.logger.info(f"Would delete: {event_dir.name}")
                        deleted.append(str(event_dir))
                    else:
                        shutil.rmtree(event_dir)
                        self.logger.info(f"Deleted: {event_dir.name}")
                        deleted.append(str(event_dir))
            
            return True, None, deleted
        
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return False, str(e), []


def main():
    """CLI entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Event Archiver')
    parser.add_argument('command', choices=['archive', 'cleanup'])
    parser.add_argument('--event-path', help='Event directory path (for archive)')
    parser.add_argument('--events-dir', help='Events directory (for cleanup)')
    parser.add_argument('--archive-root', default='/archive/church-media', help='Archive root path')
    parser.add_argument('--keep-local', action='store_true', help='Keep local copy after archive')
    parser.add_argument('--compress', action='store_true', help='Compress before archiving')
    parser.add_argument('--days', type=int, default=90, help='Delete events older than N days')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no actual deletion)')
    
    args = parser.parse_args()
    
    archiver = Archiver(archive_root=args.archive_root)
    
    if args.command == 'archive':
        if not args.event_path:
            print("Error: --event-path required for archive command")
            return
        
        success, error, archive_path = archiver.archive_event(
            args.event_path,
            keep_local_copy=args.keep_local,
            compress=args.compress
        )
        
        if success:
            print(f"✓ Archived to: {archive_path}")
        else:
            print(f"✗ Failed: {error}")
    
    elif args.command == 'cleanup':
        if not args.events_dir:
            print("Error: --events-dir required for cleanup command")
            return
        
        success, error, deleted = archiver.cleanup_old_events(
            args.events_dir,
            days_threshold=args.days,
            dry_run=args.dry_run
        )
        
        if success:
            print(f"✓ Cleanup complete. Events affected: {len(deleted)}")
            for event in deleted:
                print(f"  - {event}")
        else:
            print(f"✗ Failed: {error}")


if __name__ == '__main__':
    main()
