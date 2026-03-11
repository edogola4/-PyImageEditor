"""Text overlay operations with font detection."""
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional
from utils.font_matcher import detect_font_from_image, match_font


def add_text(image: Image.Image, text: str, x: int, y: int, 
             font_path: Optional[str], font_size: int, 
             color: Tuple[int, int, int]) -> Image.Image:
    """Add text overlay to image with specified font and color."""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    
    try:
        if font_path and font_path != "default":
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    
    draw.text((x, y), text, fill=color, font=font)
    return img_copy


def detect_and_match_font(image: Image.Image) -> str:
    """Detect font from image and match to system font."""
    detected = detect_font_from_image(image)
    return match_font(detected)
