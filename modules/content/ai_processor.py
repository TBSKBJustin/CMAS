"""
AI Content Processor using Ollama
Corrects subtitles and generates summaries for downstream tasks
"""
import logging
import json
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import requests


class AIContentProcessor:
    """Uses Ollama to correct subtitles and generate content summaries"""
    
    def __init__(
        self,
        model: str = "qwen2.5:latest",
        host: str = "http://localhost:11434",
        logger: Optional[logging.Logger] = None
    ):
        self.model = model
        self.host = host
        self.logger = logger or logging.getLogger(__name__)
        self.api_url = f"{host}/api/generate"
        
    def _check_ollama_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Ollama not available: {e}")
            return False
    
    def _check_model_available(self) -> bool:
        """Check if the specified model is available"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(m.get("name") == self.model for m in models)
            return False
        except Exception as e:
            self.logger.error(f"Failed to check model: {e}")
            return False
    
    def _call_ollama(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Call Ollama API and get response"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(self.api_url, json=payload, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                self.logger.error(f"Ollama API error: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to call Ollama: {e}")
            return None
    
    def _parse_srt(self, srt_path: str) -> List[Dict]:
        """Parse SRT file into structured data"""
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by double newline to get subtitle blocks
        blocks = re.split(r'\n\n+', content.strip())
        subtitles = []
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0])
                    timestamp = lines[1]
                    text = '\n'.join(lines[2:])
                    subtitles.append({
                        'index': index,
                        'timestamp': timestamp,
                        'text': text
                    })
                except ValueError:
                    continue
        
        return subtitles
    
    def _write_srt(self, subtitles: List[Dict], output_path: str):
        """Write structured data back to SRT format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for sub in subtitles:
                f.write(f"{sub['index']}\n")
                f.write(f"{sub['timestamp']}\n")
                f.write(f"{sub['text']}\n\n")
    
    def correct_subtitles(
        self,
        srt_path: str,
        output_dir: str,
        batch_size: int = 10
    ) -> Tuple[bool, Optional[str], Dict[str, str]]:
        """
        Correct subtitles using AI
        
        Args:
            srt_path: Path to original SRT file
            output_dir: Directory to save corrected SRT
            batch_size: Number of subtitle segments to correct at once
            
        Returns:
            (success, error_message, output_files)
        """
        try:
            if not self._check_ollama_available():
                return False, "Ollama service not available", {}
            
            if not self._check_model_available():
                return False, f"Model {self.model} not available", {}
            
            self.logger.info(f"Correcting subtitles: {srt_path}")
            
            # Parse SRT
            subtitles = self._parse_srt(srt_path)
            if not subtitles:
                return False, "Failed to parse SRT file", {}
            
            self.logger.info(f"Parsed {len(subtitles)} subtitle segments")
            
            # Correct in batches
            corrected_subtitles = []
            system_prompt = """You are a subtitle correction assistant. Your task is to:
1. Fix spelling errors and typos
2. Correct grammar mistakes
3. Fix mistranscribed words that don't make sense in context
4. Keep the meaning and timing the same
5. Respond ONLY with the corrected text, no explanations

Keep the corrections minimal and natural."""
            
            for i in range(0, len(subtitles), batch_size):
                batch = subtitles[i:i + batch_size]
                
                # Prepare batch text
                batch_text = "\n---\n".join([
                    f"[{sub['index']}] {sub['text']}"
                    for sub in batch
                ])
                
                prompt = f"""Correct the following subtitle segments. Return them in the same format with [index] prefix:

{batch_text}"""
                
                self.logger.info(f"Correcting batch {i//batch_size + 1}/{(len(subtitles) + batch_size - 1)//batch_size}")
                
                corrected_text = self._call_ollama(prompt, system_prompt)
                
                if not corrected_text:
                    # Fallback: keep original
                    corrected_subtitles.extend(batch)
                    continue
                
                # Parse corrected text
                corrected_lines = corrected_text.split('\n---\n')
                
                for j, sub in enumerate(batch):
                    if j < len(corrected_lines):
                        # Extract corrected text (remove [index] prefix)
                        corrected = re.sub(r'^\[\d+\]\s*', '', corrected_lines[j].strip())
                        corrected_subtitles.append({
                            'index': sub['index'],
                            'timestamp': sub['timestamp'],
                            'text': corrected if corrected else sub['text']
                        })
                    else:
                        corrected_subtitles.append(sub)
            
            # Write corrected SRT
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            base_name = Path(srt_path).stem
            if base_name.endswith('_audio'):
                base_name = base_name[:-6]
            
            corrected_srt = output_path / f"{base_name}_corrected.srt"
            self._write_srt(corrected_subtitles, str(corrected_srt))
            
            self.logger.info(f"Corrected SRT saved to: {corrected_srt}")
            
            return True, None, {"corrected_srt": str(corrected_srt)}
            
        except Exception as e:
            error_msg = f"Subtitle correction failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return False, error_msg, {}
    
    def generate_summary(
        self,
        srt_path: str,
        output_dir: str,
        summary_length: str = "medium"
    ) -> Tuple[bool, Optional[str], Dict[str, str]]:
        """
        Generate content summary from subtitles
        
        Args:
            srt_path: Path to SRT file (preferably corrected version)
            output_dir: Directory to save summary
            summary_length: "short", "medium", or "long"
            
        Returns:
            (success, error_message, output_files)
        """
        try:
            if not self._check_ollama_available():
                return False, "Ollama service not available", {}
            
            if not self._check_model_available():
                return False, f"Model {self.model} not available", {}
            
            self.logger.info(f"Generating summary from: {srt_path}")
            
            # Parse and extract all text
            subtitles = self._parse_srt(srt_path)
            if not subtitles:
                return False, "Failed to parse SRT file", {}
            
            full_text = ' '.join([sub['text'] for sub in subtitles])
            
            # Determine summary length instructions
            length_instructions = {
                "short": "a concise summary in 2-3 paragraphs (150-200 words)",
                "medium": "a comprehensive summary in 4-5 paragraphs (300-400 words)",
                "long": "a detailed summary in 6-8 paragraphs (500-600 words)"
            }
            
            length_instruction = length_instructions.get(summary_length, length_instructions["medium"])
            
            system_prompt = """You are a sermon/speech summarization assistant. Your task is to:
1. Identify the main topics and themes
2. Extract key points and important messages
3. Note any scripture references or important quotes
4. Capture the overall message and purpose
5. Write in a clear, organized manner"""
            
            prompt = f"""Please create {length_instruction} of the following sermon/speech transcript:

{full_text}

Include:
- Main topic and theme
- Key points discussed
- Important messages or takeaways
- Any notable quotes or references

Summary:"""
            
            self.logger.info("Calling AI to generate summary...")
            summary_text = self._call_ollama(prompt, system_prompt)
            
            if not summary_text:
                return False, "Failed to generate summary", {}
            
            # Save summary
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            base_name = Path(srt_path).stem
            if base_name.endswith('_corrected'):
                base_name = base_name[:-10]
            elif base_name.endswith('_audio'):
                base_name = base_name[:-6]
            
            summary_file = output_path / f"{base_name}_summary.txt"
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"# Content Summary\n\n")
                f.write(f"Generated from: {Path(srt_path).name}\n")
                f.write(f"Summary length: {summary_length}\n\n")
                f.write("---\n\n")
                f.write(summary_text)
            
            self.logger.info(f"Summary saved to: {summary_file}")
            
            return True, None, {"summary": str(summary_file)}
            
        except Exception as e:
            error_msg = f"Summary generation failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return False, error_msg, {}
    
    def process_content(
        self,
        srt_path: str,
        output_dir: str,
        correct_subtitles: bool = True,
        generate_summary: bool = True,
        summary_length: str = "medium",
        batch_size: int = 10
    ) -> Tuple[bool, Optional[str], Dict[str, str]]:
        """
        Complete AI content processing pipeline
        
        Args:
            srt_path: Path to original SRT file
            output_dir: Directory to save outputs
            correct_subtitles: Whether to correct subtitles
            generate_summary: Whether to generate summary
            summary_length: Summary length ("short", "medium", "long")
            batch_size: Batch size for subtitle correction
            
        Returns:
            (success, error_message, output_files)
        """
        output_files = {}
        
        # Step 1: Correct subtitles
        if correct_subtitles:
            success, error, files = self.correct_subtitles(srt_path, output_dir, batch_size)
            if not success:
                return False, f"Subtitle correction failed: {error}", output_files
            output_files.update(files)
            
            # Use corrected version for summary
            srt_for_summary = files.get("corrected_srt", srt_path)
        else:
            srt_for_summary = srt_path
        
        # Step 2: Generate summary
        if generate_summary:
            success, error, files = self.generate_summary(srt_for_summary, output_dir, summary_length)
            if not success:
                return False, f"Summary generation failed: {error}", output_files
            output_files.update(files)
        
        return True, None, output_files
