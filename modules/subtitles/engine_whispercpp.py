"""
Subtitle Engine - whisper.cpp implementation (Primary engine)
Updated to be the default subtitle generation engine
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional, List, Dict


class WhisperCppEngine:
    """Subtitle generation using whisper.cpp (default engine)"""
    
    SUPPORTED_MODELS = {
        'tiny': 'ggml-tiny.bin',
        'base': 'ggml-base.bin',
        'small': 'ggml-small.bin',
        'medium': 'ggml-medium.bin',
        'large': 'ggml-large-v3.bin'
    }
    
    def __init__(self, model: str = "base", models_dir: str = "models", whisper_bin: str = "whisper"):
        """
        Initialize whisper.cpp engine
        
        Args:
            model: Model size (tiny, base, small, medium, large)
            models_dir: Directory containing GGML models
            whisper_bin: Path to whisper.cpp executable
        """
        self.model_name = model
        self.models_dir = Path(models_dir)
        self.whisper_bin = whisper_bin
        self.logger = self._setup_logger()
        
        # Get model file path
        model_file = self.SUPPORTED_MODELS.get(model, self.SUPPORTED_MODELS['base'])
        self.model_path = self.models_dir / model_file
        
        # Check if whisper.cpp is available
        self.available = self._check_availability()
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("WhisperCppEngine")
        logger.setLevel(logging.INFO)
        return logger
    
    def _check_availability(self) -> bool:
        """Check if whisper.cpp is installed"""
        try:
            result = subprocess.run(
                [self.whisper_bin, '--help'],
                capture_output=True,,
        translate_to_english: bool = False
    ) -> tuple[bool, Optional[str], Dict[str, str]]:
        """
        Generate subtitles from video
        
        Args:
            video_path: Path to input video file
            output_dir: Directory to save subtitle files
            language: Language code (e.g., "en", "zh", "auto")
            formats: List of output formats (e.g., ["srt", "vtt"])
            translate_to_english: Translate to English
            
        Returns:
            (success, error_message, output_files)
        """
        if not self.available:
            return False, "whisper.cpp is not installed", {}
        
        if not self.check_model():
            return False, f"Model not found: {self.model_path}", {}
        (
                video_path, output_dir, language, formats, translate_to_english
            )
            
            if success:
                return True, None, output
            
            # Fallback: extract audio and retry
            self.logger.warning(f"Direct transcription failed: {error}")
            self.logger.info("Falling back to audio extraction")
            
            audio_path = self._extract_audio(video_path, output_dir)
            if not audio_path:
                return False, "Failed to extract audio", {}
            
            success, error, output = self._transcribe(
                audio_path, output_dir, language, formats, translate_to_englishuto")
            formats: List of output formats (e.g., ["srt", "vtt"])
            
        Returns:
            (success, error_message, output_files)
        """
        if formats is None:
            formats = ["srt", "vtt"]
        
        self.logger(
        self,
        input_path: str,
        output_dir: str,
        language: str,
        formats: List[str],
        translate: bool
    ) -> tuple[bool, Optional[str], Dict[str, str]]:
        """Transcribe audio/video file"""
        try:
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)
            
            base_name = Path(input_path).stem
            output_files = {}
            
            # Build whisper.cpp command
            cmd = [
                self.whisper_bin,
                "-m", str(self.model_path),
                "-f", input_path,
                "-of", str(output_dir_path),
            ]
            
            # Set language
            if language != "auto":
                cmd.extend(["-l", language])
            
            # Translation
            if translate:
                cmd.append("-tr")
            
            # Output formats
            format_flags = {
                'srt': '-osrt',
                'vtt': '-ovtt',
                'txt': '-otxt',
                'json': '-oj'
            }
            
            for fmt in formats:
                if fmt in format_flags:
                    cmd.append(format_flags[fmt])
            
            # Add threading and processing options
            cmd.extend([
                "-t", "4",  # 4 threads
                "-p", "1",  # 1 processor
            
    
    def _transcribe_direct(
        self,
        input_path: str,
        output_dir: str,
        language: str,
        formats: List[str]
    ) -> tuple[bool, Optional[str], dict]:
        """Attempt direct transcription"""
        try:
            output_files = {}
            base_name = Path(input_path).st or "Transcription failed", {}
            
            # Collect output files
            # whisper.cpp outputs with pattern: filename.{format}
            for fmt in formats:
                # Try different possible output names
                possible_names = [
                    output_dir_path / f"{base_name}.{fmt}",
                    output_dir_path / base_name / f"{base_name}.{fmt}",
                ]
                
                for output_path in possible_names:
                    if output_path.exists():
                        output_files[fmt] = str(output_path)
                        break
            
            if not output_files:
                return False, "No output files generated", {}
            
            self.logger.info(f"Generated subtitles: {list(output_files.keys())}")
            return True, None, output_files
        
        except subprocess.TimeoutExpired:
            return False, "Transcription timeout (>1 (whisper requirement)
                "-ac", "1",  # Mono
                "-y",  # Overwrite
                str(audio_path)
            ]
            
            self.logger.info("Extracting audio with ffmpeg")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                self.logger.error(f"Audio extraction failed: {result.stderr}")
                return None
            
            return str(audio_path)
        
        except Exception as e:
            self.logger.error(f"Audio extraction error: {e}")
            return None
    
    @staticmethod
    def list_available_models() -> List[str]:
        """List available model sizes"""
        return list(WhisperCppEngine.SUPPORTED_MODELS.keys()
    def _extract_audio(self, video_path: str, output_dir: str) -> Optional[str]:
        """Extract audio from video using ffmpeg"""
        try:
            audio_path = Path(output_dir) / f"{Path(video_path).stem}_audio.wav"
            
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vn",  # No video
                "-acodec", "pcm_s16le",  # 16-bit PCM
                "-ar", "16000",  # 16kHz sample rate
                "-ac", "1",  # Mono
                "-y",  # Overwrite
                str(audio_path)
            ]base', 
                       choices=WhisperCppEngine.list_available_models(),
                       help='Whisper model size')
    parser.add_argument('--language', default='auto', help='Language code (en, zh, etc.)')
    parser.add_argument('--formats', nargs='+', default=['srt', 'vtt'], 
                       choices=['srt', 'vtt', 'txt', 'json'],
                       help='Output formats')
    parser.add_argument('--translate', action='store_true', help='Translate to English')
    parser.add_argument('--models-dir', default='models', help='Models directory')
    
    args = parser.parse_args()
    
    engine = WhisperCppEngine(
        model=args.model,
        models_dir=args.models_dir
    )
    
    success, error, output_files = engine.generate_subtitles(
        args.video,
        args.output_dir,
        args.language,
        args.formats,
        args.translatern None
            
            return str(audio_path)
        
        except Exception as e:
            self.logger.error(f"Audio extraction error: {e}")
            return None
    
    def _transcribe_audio(
        self,
        audio_path: str,
        output_dir: str,
        language: str,
        formats: List[str]
    ) -> tuple[bool, Optional[str], dict]:
        """Transcribe from extracted audio"""
        return self._transcribe_direct(audio_path, output_dir, language, formats)


def main():
    """CLI entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Subtitle Generation (whisper.cpp)')
    parser.add_argument('--video', required=True, help='Input video path')
    parser.add_argument('--output-dir', required=True, help='Output directory')
    parser.add_argument('--model', default='models/ggml-base.bin', help='Whisper model path')
    parser.add_argument('--language', default='auto', help='Language code')
    parser.add_argument('--formats', nargs='+', default=['srt', 'vtt'], help='Output formats')
    
    args = parser.parse_args()
    
    engine = WhisperCppEngine(model_path=args.model)
    
    success, error, output_files = engine.generate_subtitles(
        args.video,
        args.output_dir,
        args.language,
        args.formats
    )
    
    if success:
        print("✓ Subtitles generated:")
        for fmt, path in output_files.items():
            print(f"  {fmt}: {path}")
    else:
        print(f"✗ Failed: {error}")


if __name__ == '__main__':
    main()
