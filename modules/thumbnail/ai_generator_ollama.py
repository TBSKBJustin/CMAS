"""
AI Generator (Ollama) - Character image generator (pluggable)
"""

import logging
import requests
from pathlib import Path
from typing import Optional


class OllamaGenerator:
    """Generates character images using Ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        Initialize Ollama generator
        
        Args:
            base_url: Ollama API base URL
            model: Model name to use
        """
        self.base_url = base_url
        self.model = model
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("OllamaGenerator")
        logger.setLevel(logging.INFO)
        return logger
    
    def generate_character(
        self, 
        prompt: str, 
        output_path: str,
        fallback_asset: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Generate a character image based on sermon content
        
        Args:
            prompt: Text prompt describing the desired character/theme
            output_path: Where to save the generated image
            fallback_asset: Path to fallback image if generation fails
            
        Returns:
            (success, error_message)
        """
        self.logger.info(f"Generating character with prompt: {prompt}")
        
        try:
            # Note: This is a placeholder implementation
            # Ollama primarily handles text generation
            # For actual image generation, you might want to use:
            # - Stable Diffusion WebUI API
            # - ComfyUI API
            # - DALL-E / Midjourney API
            
            # For now, we'll just log and use fallback
            self.logger.warning("Image generation not yet implemented, using fallback")
            
            if fallback_asset:
                return self._use_fallback(fallback_asset, output_path)
            
            return False, "Image generation not implemented and no fallback provided"
        
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            
            if fallback_asset:
                return self._use_fallback(fallback_asset, output_path)
            
            return False, str(e)
    
    def _use_fallback(self, fallback_asset: str, output_path: str) -> tuple[bool, Optional[str]]:
        """Copy fallback asset to output path"""
        try:
            from shutil import copy2
            copy2(fallback_asset, output_path)
            self.logger.info(f"Used fallback asset: {fallback_asset}")
            return True, None
        except Exception as e:
            return False, f"Failed to use fallback: {e}"
    
    def generate_prompt_from_sermon(
        self, 
        title: str, 
        scripture: Optional[str] = None,
        series: Optional[str] = None
    ) -> str:
        """
        Generate an image prompt from sermon metadata
        
        Args:
            title: Sermon title
            scripture: Scripture reference
            series: Sermon series name
            
        Returns:
            Image generation prompt
        """
        # Build contextual prompt
        prompt_parts = []
        
        if series:
            prompt_parts.append(f"Series: {series}")
        
        prompt_parts.append(f"Title: {title}")
        
        if scripture:
            prompt_parts.append(f"Scripture: {scripture}")
        
        # Add style guidance
        prompt_parts.append("Style: biblical character, friendly, welcoming, church-appropriate")
        
        return " | ".join(prompt_parts)


def main():
    """CLI entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Thumbnail Character Generator')
    parser.add_argument('--title', required=True, help='Sermon title')
    parser.add_argument('--scripture', help='Scripture reference')
    parser.add_argument('--series', help='Sermon series')
    parser.add_argument('--output', required=True, help='Output image path')
    parser.add_argument('--fallback', help='Fallback asset path')
    parser.add_argument('--model', default='llama2', help='Ollama model name')
    
    args = parser.parse_args()
    
    generator = OllamaGenerator(model=args.model)
    
    # Generate prompt from sermon metadata
    prompt = generator.generate_prompt_from_sermon(
        args.title,
        args.scripture,
        args.series
    )
    
    print(f"Generated prompt: {prompt}")
    
    # Generate character
    success, error = generator.generate_character(
        prompt,
        args.output,
        args.fallback
    )
    
    if success:
        print(f"✓ Character generated: {args.output}")
    else:
        print(f"✗ Generation failed: {error}")


if __name__ == '__main__':
    main()
