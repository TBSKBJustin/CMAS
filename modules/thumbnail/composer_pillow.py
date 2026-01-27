"""
Thumbnail Composer (Pillow) - Compose final thumbnail from layers
"""

import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont


class ThumbnailComposer:
    """Composes final thumbnail from multiple layers"""
    
    DEFAULT_SIZE = (1280, 720)
    
    def __init__(self, assets_dir: str = "assets"):
        """
        Initialize thumbnail composer
        
        Args:
            assets_dir: Path to assets directory
        """
        self.assets_dir = Path(assets_dir)
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("ThumbnailComposer")
        logger.setLevel(logging.INFO)
        return logger
    
    def compose(
        self,
        output_path: str,
        title: str,
        scripture: Optional[str] = None,
        background: Optional[str] = None,
        character: Optional[str] = None,
        pastor: Optional[str] = None,
        logo: Optional[str] = None,
        size: Tuple[int, int] = DEFAULT_SIZE
    ) -> tuple[bool, Optional[str]]:
        """
        Compose thumbnail from layers
        
        Args:
            output_path: Where to save final thumbnail
            title: Sermon title
            scripture: Scripture reference (optional)
            background: Background image path
            character: AI-generated character image path
            pastor: Pastor portrait path
            logo: Church logo path
            size: Output image size (width, height)
            
        Returns:
            (success, error_message)
        """
        try:
            self.logger.info(f"Composing thumbnail: {title}")
            
            # Create base canvas
            canvas = Image.new('RGB', size, color=(255, 255, 255))
            
            # Layer 1: Background
            if background and Path(background).exists():
                bg = Image.open(background)
                bg = bg.resize(size, Image.Resampling.LANCZOS)
                canvas.paste(bg, (0, 0))
            else:
                # Use solid color as fallback
                canvas = Image.new('RGB', size, color=(41, 98, 255))
            
            # Layer 2: Character (if provided)
            if character and Path(character).exists():
                char_img = Image.open(character)
                char_img = self._resize_with_aspect(char_img, max_width=400, max_height=600)
                
                # Position on right side
                char_x = size[0] - char_img.width - 50
                char_y = size[1] - char_img.height - 50
                
                if char_img.mode == 'RGBA':
                    canvas.paste(char_img, (char_x, char_y), char_img)
                else:
                    canvas.paste(char_img, (char_x, char_y))
            
            # Layer 3: Pastor portrait (if provided)
            if pastor and Path(pastor).exists():
                pastor_img = Image.open(pastor)
                pastor_img = self._resize_with_aspect(pastor_img, max_width=200, max_height=200)
                
                # Position on left side
                pastor_x = 50
                pastor_y = size[1] - pastor_img.height - 50
                
                if pastor_img.mode == 'RGBA':
                    canvas.paste(pastor_img, (pastor_x, pastor_y), pastor_img)
                else:
                    canvas.paste(pastor_img, (pastor_x, pastor_y))
            
            # Layer 4: Text overlay
            draw = ImageDraw.Draw(canvas)
            
            # Try to load custom font
            try:
                title_font = ImageFont.truetype(str(self.assets_dir / "fonts" / "bold.ttf"), 72)
                scripture_font = ImageFont.truetype(str(self.assets_dir / "fonts" / "regular.ttf"), 48)
            except:
                # Fallback to default font
                title_font = ImageFont.load_default()
                scripture_font = ImageFont.load_default()
            
            # Draw title with stroke/shadow
            title_x = 50
            title_y = 50
            self._draw_text_with_stroke(
                draw, 
                (title_x, title_y), 
                title, 
                title_font,
                fill_color=(255, 255, 255),
                stroke_color=(0, 0, 0),
                stroke_width=3,
                max_width=size[0] - 500
            )
            
            # Draw scripture reference
            if scripture:
                scripture_y = title_y + 150
                draw.text(
                    (title_x, scripture_y),
                    scripture,
                    font=scripture_font,
                    fill=(255, 255, 255)
                )
            
            # Layer 5: Logo (if provided)
            if logo and Path(logo).exists():
                logo_img = Image.open(logo)
                logo_img = self._resize_with_aspect(logo_img, max_width=150, max_height=150)
                
                # Position in top-right corner
                logo_x = size[0] - logo_img.width - 30
                logo_y = 30
                
                if logo_img.mode == 'RGBA':
                    canvas.paste(logo_img, (logo_x, logo_y), logo_img)
                else:
                    canvas.paste(logo_img, (logo_x, logo_y))
            
            # Save final thumbnail
            canvas.save(output_path, 'JPEG', quality=95)
            self.logger.info(f"Thumbnail saved: {output_path}")
            
            return True, None
        
        except Exception as e:
            self.logger.error(f"Failed to compose thumbnail: {e}")
            return False, str(e)
    
    def _resize_with_aspect(
        self, 
        image: Image.Image, 
        max_width: int, 
        max_height: int
    ) -> Image.Image:
        """Resize image maintaining aspect ratio"""
        ratio = min(max_width / image.width, max_height / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        return image.resize(new_size, Image.Resampling.LANCZOS)
    
    def _draw_text_with_stroke(
        self,
        draw: ImageDraw.ImageDraw,
        position: Tuple[int, int],
        text: str,
        font: ImageFont.ImageFont,
        fill_color: Tuple[int, int, int],
        stroke_color: Tuple[int, int, int],
        stroke_width: int = 2,
        max_width: Optional[int] = None
    ):
        """Draw text with stroke/outline effect"""
        x, y = position
        
        # Wrap text if max_width specified
        if max_width:
            text = self._wrap_text(text, font, max_width)
        
        # Draw stroke
        for offset_x in range(-stroke_width, stroke_width + 1):
            for offset_y in range(-stroke_width, stroke_width + 1):
                draw.text((x + offset_x, y + offset_y), text, font=font, fill=stroke_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=fill_color)
    
    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
        """Wrap text to fit within max_width"""
        # Simple word wrapping
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)


def main():
    """CLI entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Thumbnail Composer')
    parser.add_argument('--title', required=True, help='Sermon title')
    parser.add_argument('--scripture', help='Scripture reference')
    parser.add_argument('--background', help='Background image path')
    parser.add_argument('--character', help='Character image path')
    parser.add_argument('--pastor', help='Pastor portrait path')
    parser.add_argument('--logo', help='Church logo path')
    parser.add_argument('--output', required=True, help='Output thumbnail path')
    
    args = parser.parse_args()
    
    composer = ThumbnailComposer()
    
    success, error = composer.compose(
        args.output,
        args.title,
        args.scripture,
        args.background,
        args.character,
        args.pastor,
        args.logo
    )
    
    if success:
        print(f"✓ Thumbnail created: {args.output}")
    else:
        print(f"✗ Failed: {error}")


if __name__ == '__main__':
    main()
