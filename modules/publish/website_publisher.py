"""
Website Publisher - Generate markdown and push to git repository
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime


class WebsitePublisher:
    """Publishes sermon content to website via Git"""
    
    def __init__(self, repo_path: str, content_dir: str = "content/sermons"):
        """
        Initialize website publisher
        
        Args:
            repo_path: Path to website git repository
            content_dir: Subdirectory for sermon content (relative to repo)
        """
        self.repo_path = Path(repo_path)
        self.content_dir = content_dir
        self.logger = self._setup_logger()
        
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("WebsitePublisher")
        logger.setLevel(logging.INFO)
        return logger
    
    def publish(
        self,
        event_data: Dict,
        video_url: Optional[str] = None,
        thumbnail_path: Optional[str] = None,
        captions: Optional[Dict[str, str]] = None,
        auto_commit: bool = True,
        auto_push: bool = False
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Publish sermon to website
        
        Args:
            event_data: Event metadata dictionary
            video_url: YouTube video URL (optional)
            thumbnail_path: Path to thumbnail (optional, will be copied)
            captions: Dict of caption files {format: path} (optional)
            auto_commit: Automatically commit changes
            auto_push: Automatically push to remote
            
        Returns:
            (success, error_message, post_path)
        """
        try:
            self.logger.info(f"Publishing: {event_data.get('title')}")
            
            # Generate markdown content
            markdown = self._generate_markdown(event_data, video_url)
            
            # Create post file
            post_path = self._save_post(event_data, markdown)
            
            # Copy assets (thumbnail, captions)
            if thumbnail_path:
                self._copy_asset(thumbnail_path, event_data)
            
            if captions:
                for fmt, path in captions.items():
                    self._copy_asset(path, event_data)
            
            # Git operations
            if auto_commit:
                self._git_add_commit(event_data)
                
                if auto_push:
                    self._git_push()
            
            self.logger.info(f"Published successfully: {post_path}")
            return True, None, str(post_path)
        
        except Exception as e:
            self.logger.error(f"Publishing failed: {e}")
            return False, str(e), None
    
    def _generate_markdown(self, event_data: Dict, video_url: Optional[str]) -> str:
        """Generate markdown content for sermon post"""
        title = event_data.get('title', 'Untitled')
        speaker = event_data.get('speaker', '')
        scripture = event_data.get('scripture', '')
        series = event_data.get('series', '')
        date = event_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Front matter (YAML)
        front_matter = [
            "---",
            f"title: \"{title}\"",
            f"date: {date}",
            f"speaker: \"{speaker}\""
        ]
        
        if series:
            front_matter.append(f"series: \"{series}\"")
        
        if scripture:
            front_matter.append(f"scripture: \"{scripture}\"")
        
        if video_url:
            front_matter.append(f"video_url: \"{video_url}\"")
        
        front_matter.extend([
            "draft: false",
            "---",
            ""
        ])
        
        # Content
        content = []
        
        if series:
            content.append(f"**Series:** {series}\n")
        
        if scripture:
            content.append(f"**Scripture:** {scripture}\n")
        
        if speaker:
            content.append(f"**Speaker:** {speaker}\n")
        
        content.append("")
        
        if video_url:
            content.append("## Watch")
            content.append("")
            content.append(f"[Watch on YouTube]({video_url})")
            content.append("")
        
        content.append("## About This Message")
        content.append("")
        content.append("_Message description coming soon._")
        content.append("")
        
        return "\n".join(front_matter + content)
    
    def _save_post(self, event_data: Dict, markdown: str) -> Path:
        """Save markdown post to file"""
        # Create filename from event data
        date = event_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        title_slug = self._slugify(event_data.get('title', 'untitled'))
        filename = f"{date}-{title_slug}.md"
        
        # Full path
        content_path = self.repo_path / self.content_dir
        content_path.mkdir(parents=True, exist_ok=True)
        
        post_path = content_path / filename
        
        # Write file
        with open(post_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        return post_path
    
    def _copy_asset(self, source_path: str, event_data: Dict):
        """Copy asset (thumbnail, caption) to website repo"""
        import shutil
        
        source = Path(source_path)
        if not source.exists():
            self.logger.warning(f"Asset not found: {source_path}")
            return
        
        # Determine destination
        date = event_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        title_slug = self._slugify(event_data.get('title', 'untitled'))
        
        assets_dir = self.repo_path / "static" / "sermons" / f"{date}-{title_slug}"
        assets_dir.mkdir(parents=True, exist_ok=True)
        
        dest = assets_dir / source.name
        shutil.copy2(source, dest)
        
        self.logger.info(f"Copied asset: {source.name}")
    
    def _git_add_commit(self, event_data: Dict):
        """Add and commit changes"""
        title = event_data.get('title', 'Untitled')
        
        # Git add
        subprocess.run(
            ['git', 'add', '.'],
            cwd=self.repo_path,
            check=True
        )
        
        # Git commit
        commit_message = f"Add sermon: {title}"
        subprocess.run(
            ['git', 'commit', '-m', commit_message],
            cwd=self.repo_path,
            check=True
        )
        
        self.logger.info(f"Committed changes: {commit_message}")
    
    def _git_push(self):
        """Push changes to remote"""
        subprocess.run(
            ['git', 'push'],
            cwd=self.repo_path,
            check=True
        )
        
        self.logger.info("Pushed to remote repository")
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug"""
        text = text.lower()
        text = ''.join(c if c.isalnum() or c in ' -_' else '' for c in text)
        text = '-'.join(text.split())
        return text[:50]


def main():
    """CLI entry point for testing"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Website Publisher')
    parser.add_argument('--repo', required=True, help='Website repository path')
    parser.add_argument('--event-json', required=True, help='Event JSON file')
    parser.add_argument('--video-url', help='YouTube video URL')
    parser.add_argument('--thumbnail', help='Thumbnail path')
    parser.add_argument('--push', action='store_true', help='Auto-push to remote')
    
    args = parser.parse_args()
    
    # Load event data
    with open(args.event_json, 'r') as f:
        event_data = json.load(f)
    
    publisher = WebsitePublisher(args.repo)
    
    success, error, post_path = publisher.publish(
        event_data,
        args.video_url,
        args.thumbnail,
        auto_commit=True,
        auto_push=args.push
    )
    
    if success:
        print(f"✓ Published: {post_path}")
    else:
        print(f"✗ Failed: {error}")


if __name__ == '__main__':
    main()
