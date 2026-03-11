"""Shape drawing operations."""
from PIL import Image, ImageDraw
from typing import Tuple


def draw_rectangle(image: Image.Image, x1: int, y1: int, x2: int, y2: int, 
                   color: Tuple[int, int, int], thickness: int) -> Image.Image:
    """Draw a rectangle on the image."""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    draw.rectangle([x1, y1, x2, y2], outline=color, width=thickness)
    return img_copy


def draw_circle(image: Image.Image, cx: int, cy: int, radius: int, 
                color: Tuple[int, int, int], thickness: int) -> Image.Image:
    """Draw a circle on the image."""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.ellipse(bbox, outline=color, width=thickness)
    return img_copy


def draw_line(image: Image.Image, x1: int, y1: int, x2: int, y2: int, 
              color: Tuple[int, int, int], thickness: int) -> Image.Image:
    """Draw a line on the image."""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    draw.line([x1, y1, x2, y2], fill=color, width=thickness)
    return img_copy
