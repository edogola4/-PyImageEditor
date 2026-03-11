"""File handling utilities for opening and saving images."""
import os
from typing import Optional, Tuple
from PIL import Image


def open_image(filepath: str) -> Tuple[Image.Image, dict]:
    """Open image and return PIL Image object with metadata."""
    img = Image.open(filepath)
    
    # Handle animated GIFs - load first frame
    if img.format == 'GIF' and hasattr(img, 'is_animated') and img.is_animated:
        img.seek(0)
    
    # Convert to RGB if necessary
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')
    
    # Extract metadata
    file_size = os.path.getsize(filepath)
    metadata = {
        'filename': os.path.basename(filepath),
        'format': img.format or 'UNKNOWN',
        'width': img.width,
        'height': img.height,
        'file_size': file_size,
        'dpi': img.info.get('dpi', (72, 72))
    }
    
    return img, metadata


def save_image(image: Image.Image, filepath: str, original_dpi: Tuple[int, int] = (72, 72)) -> None:
    """Save image to file with format-specific optimizations."""
    file_ext = os.path.splitext(filepath)[1].lower()
    
    save_kwargs = {'dpi': original_dpi}
    
    if file_ext in ['.jpg', '.jpeg']:
        save_kwargs['quality'] = 95
        save_kwargs['optimize'] = True
        if image.mode == 'RGBA':
            image = image.convert('RGB')
    elif file_ext == '.png':
        save_kwargs['optimize'] = True
    elif file_ext == '.webp':
        save_kwargs['quality'] = 95
        if image.mode == 'RGBA':
            image = image.convert('RGB')
    
    image.save(filepath, **save_kwargs)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
