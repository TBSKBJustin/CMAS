"""
YouTube Uploader - Upload video, thumbnail, and captions
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict
import os


class YouTubeUploader:
    """Uploads videos to YouTube with metadata"""
    
    def __init__(self, credentials_path: str = "config/youtube_credentials.json"):
        """
        Initialize YouTube uploader
        
        Args:
            credentials_path: Path to OAuth2 credentials file
        """
        self.credentials_path = credentials_path
        self.logger = self._setup_logger()
        
        # Check if google-api-python-client is available
        try:
            from googleapiclient.discovery import build
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            self.available = True
        except ImportError:
            self.logger.warning(
                "YouTube API libraries not installed. "
                "Install with: pip install google-api-python-client google-auth-oauthlib"
            )
            self.available = False
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("YouTubeUploader")
        logger.setLevel(logging.INFO)
        return logger
    
    def upload(
        self,
        video_path: str,
        title: str,
        description: str,
        thumbnail_path: Optional[str] = None,
        captions: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        category: str = "22",  # People & Blogs
        privacy: str = "private",  # private, unlisted, public
        playlist_id: Optional[str] = None
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Upload video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            thumbnail_path: Path to thumbnail image (optional)
            captions: List of caption file paths (optional)
            tags: List of tags (optional)
            category: YouTube category ID
            privacy: Privacy status (private, unlisted, public)
            playlist_id: Add to playlist (optional)
            
        Returns:
            (success, error_message, video_url)
        """
        if not self.available:
            return False, "YouTube API libraries not installed", None
        
        self.logger.info(f"Uploading video: {title}")
        
        try:
            # Get authenticated service
            youtube = self._get_authenticated_service()
            
            # Upload video
            video_id = self._upload_video(
                youtube,
                video_path,
                title,
                description,
                tags or [],
                category,
                privacy
            )
            
            if not video_id:
                return False, "Video upload failed", None
            
            # Set thumbnail
            if thumbnail_path and Path(thumbnail_path).exists():
                self._set_thumbnail(youtube, video_id, thumbnail_path)
            
            # Upload captions
            if captions:
                for caption_path in captions:
                    if Path(caption_path).exists():
                        self._upload_caption(youtube, video_id, caption_path)
            
            # Add to playlist
            if playlist_id:
                self._add_to_playlist(youtube, video_id, playlist_id)
            
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            self.logger.info(f"Upload successful: {video_url}")
            
            return True, None, video_url
        
        except Exception as e:
            self.logger.error(f"Upload failed: {e}")
            return False, str(e), None
    
    def _get_authenticated_service(self):
        """Authenticate and return YouTube service"""
        from googleapiclient.discovery import build
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import pickle
        
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        
        creds = None
        token_path = "config/youtube_token.pickle"
        
        # Load saved credentials
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('youtube', 'v3', credentials=creds)
    
    def _upload_video(
        self,
        youtube,
        video_path: str,
        title: str,
        description: str,
        tags: List[str],
        category: str,
        privacy: str
    ) -> Optional[str]:
        """Upload video file and return video ID"""
        from googleapiclient.http import MediaFileUpload
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category
            },
            'status': {
                'privacyStatus': privacy
            }
        }
        
        media = MediaFileUpload(
            video_path,
            chunksize=1024*1024,  # 1MB chunks
            resumable=True
        )
        
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                self.logger.info(f"Upload progress: {int(status.progress() * 100)}%")
        
        return response['id']
    
    def _set_thumbnail(self, youtube, video_id: str, thumbnail_path: str):
        """Set video thumbnail"""
        from googleapiclient.http import MediaFileUpload
        
        media = MediaFileUpload(thumbnail_path)
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=media
        ).execute()
        
        self.logger.info(f"Thumbnail set for video {video_id}")
    
    def _upload_caption(self, youtube, video_id: str, caption_path: str):
        """Upload caption file"""
        from googleapiclient.http import MediaFileUpload
        
        # Detect caption format
        ext = Path(caption_path).suffix.lower()
        if ext == '.srt':
            caption_format = 'srt'
        elif ext == '.vtt':
            caption_format = 'webvtt'
        else:
            self.logger.warning(f"Unsupported caption format: {ext}")
            return
        
        body = {
            'snippet': {
                'videoId': video_id,
                'language': 'en',  # TODO: detect language
                'name': 'English'
            }
        }
        
        media = MediaFileUpload(caption_path)
        
        youtube.captions().insert(
            part='snippet',
            body=body,
            media_body=media,
            sync=True
        ).execute()
        
        self.logger.info(f"Caption uploaded for video {video_id}")
    
    def _add_to_playlist(self, youtube, video_id: str, playlist_id: str):
        """Add video to playlist"""
        body = {
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }
        
        youtube.playlistItems().insert(
            part='snippet',
            body=body
        ).execute()
        
        self.logger.info(f"Added video {video_id} to playlist {playlist_id}")


def main():
    """CLI entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube Video Uploader')
    parser.add_argument('--video', required=True, help='Video file path')
    parser.add_argument('--title', required=True, help='Video title')
    parser.add_argument('--description', default='', help='Video description')
    parser.add_argument('--thumbnail', help='Thumbnail image path')
    parser.add_argument('--captions', nargs='+', help='Caption file paths')
    parser.add_argument('--tags', nargs='+', help='Video tags')
    parser.add_argument('--privacy', default='private', choices=['private', 'unlisted', 'public'])
    parser.add_argument('--playlist', help='Playlist ID')
    
    args = parser.parse_args()
    
    uploader = YouTubeUploader()
    
    success, error, video_url = uploader.upload(
        args.video,
        args.title,
        args.description,
        args.thumbnail,
        args.captions,
        args.tags,
        privacy=args.privacy,
        playlist_id=args.playlist
    )
    
    if success:
        print(f"✓ Upload successful: {video_url}")
    else:
        print(f"✗ Upload failed: {error}")


if __name__ == '__main__':
    main()
