"""Text detection, selection, replacement, and deletion engine."""
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
import cv2
from collections import Counter
from utils.ocr_engine import OCREngine
from utils.font_matcher import match_font_with_style


@dataclass
class TextBlock:
    """Represents a detected text block."""
    text: str
    x: int
    y: int
    width: int
    height: int
    conf: float
    font_size_estimate: int
    block_id: int


def detect_all_text(pil_image: Image.Image) -> list[TextBlock]:
    """
    Detect all text blocks in image using EasyOCR.
    
    Returns:
        List of TextBlock objects with confidence > 0.40
    """
    results = OCREngine.read_image(pil_image)
    blocks = []
    
    for idx, (bbox, text, conf) in enumerate(results):
        if conf <= 0.40:
            continue
        
        # Convert bbox points to x, y, width, height
        points = np.array(bbox)
        x = int(points[:, 0].min())
        y = int(points[:, 1].min())
        x2 = int(points[:, 0].max())
        y2 = int(points[:, 1].max())
        width = x2 - x
        height = y2 - y
        
        # Estimate font size from bounding box height
        font_size_estimate = max(8, int(height * 0.8))
        
        blocks.append(TextBlock(
            text=text,
            x=x,
            y=y,
            width=width,
            height=height,
            conf=conf,
            font_size_estimate=font_size_estimate,
            block_id=idx
        ))
    
    return blocks


def erase_text_region(pil_image: Image.Image, block: TextBlock, padding: int = 6) -> Image.Image:
    """
    Erase text region with smart background inpainting.
    
    Args:
        pil_image: Source image
        block: Text block to erase
        padding: Extra pixels around bounding box
    
    Returns:
        Image with text region erased
    """
    img = pil_image.copy()
    draw = ImageDraw.Draw(img)
    
    # Expand bounding box with padding, clamped to image bounds
    x1 = max(0, block.x - padding)
    y1 = max(0, block.y - padding)
    x2 = min(img.width, block.x + block.width + padding)
    y2 = min(img.height, block.y + block.height + padding)
    
    # Sample background color from border edges
    np_img = np.array(img)
    samples = []
    
    # Top edge
    if y1 > 0:
        samples.extend(np_img[y1:y1+2, x1:x2].reshape(-1, 3).tolist())
    # Bottom edge
    if y2 < img.height:
        samples.extend(np_img[y2-2:y2, x1:x2].reshape(-1, 3).tolist())
    # Left edge
    if x1 > 0:
        samples.extend(np_img[y1:y2, x1:x1+2].reshape(-1, 3).tolist())
    # Right edge
    if x2 < img.width:
        samples.extend(np_img[y1:y2, x2-2:x2].reshape(-1, 3).tolist())
    
    # Get most common color
    if samples:
        bg_color = tuple(Counter(map(tuple, samples)).most_common(1)[0][0])
    else:
        bg_color = (255, 255, 255)
    
    # Fill region with background color
    draw.rectangle([x1, y1, x2, y2], fill=bg_color)
    
    # Apply slight blur to soften edges
    region = img.crop((x1, y1, x2, y2))
    region = region.filter(ImageFilter.GaussianBlur(radius=1))
    img.paste(region, (x1, y1))
    
    return img


def render_replacement_text(
    image: Image.Image,
    block: TextBlock,
    new_text: str,
    font_path: str,
    font_size: int,
    color: tuple[int, int, int]
) -> Image.Image:
    """
    Render replacement text at block position.
    
    Args:
        image: Image to draw on
        block: Original text block
        new_text: Replacement text
        font_path: Path to font file
        font_size: Initial font size
        color: RGB color tuple
    
    Returns:
        Image with text rendered
    """
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    # Load font and adjust size to fit
    current_size = font_size
    while current_size >= 8:
        try:
            font = ImageFont.truetype(font_path, current_size)
            bbox = draw.textbbox((0, 0), new_text, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= block.width:
                break
            current_size -= 1
        except:
            font = ImageFont.load_default()
            break
    else:
        try:
            font = ImageFont.truetype(font_path, 8)
        except:
            font = ImageFont.load_default()
    
    # Draw text at block position
    draw.text((block.x, block.y), new_text, fill=color, font=font)
    
    return img


def replace_text_in_image(
    pil_image: Image.Image,
    block: TextBlock,
    new_text: str,
    font_path: str,
    color: tuple[int, int, int]
) -> Image.Image:
    """
    Replace text block with new text.
    
    Args:
        pil_image: Source image
        block: Text block to replace
        new_text: Replacement text
        font_path: Path to font file
        color: RGB color tuple
    
    Returns:
        Image with text replaced
    """
    img = erase_text_region(pil_image, block)
    img = render_replacement_text(img, block, new_text, font_path, block.font_size_estimate, color)
    return img


def delete_text_region(
    pil_image: Image.Image,
    block: TextBlock,
    padding: int = 6
) -> Image.Image:
    """
    Delete text region without replacement.
    
    Args:
        pil_image: Source image
        block: Text block to delete
        padding: Extra pixels around bounding box
    
    Returns:
        Image with text deleted
    """
    return erase_text_region(pil_image, block, padding)


def delete_multiple_regions(
    pil_image: Image.Image,
    blocks: list[TextBlock],
    padding: int = 6
) -> Image.Image:
    """
    Delete multiple text regions in one pass.
    
    Args:
        pil_image: Source image
        blocks: List of text blocks to delete
        padding: Extra pixels around bounding box
    
    Returns:
        Image with all text deleted
    """
    img = pil_image.copy()
    for block in blocks:
        img = erase_text_region(img, block, padding)
    return img


def extract_text_properties(pil_image: Image.Image, block: TextBlock) -> dict:
    """
    Extract ALL text properties from original text block.
    This is called BEFORE erasing to capture exact visual properties.
    
    Returns dict with:
        color, background_color, font_size, is_bold, is_italic,
        has_shadow, shadow_color, shadow_offset, has_outline,
        outline_color, outline_width, opacity, letter_spacing, best_font_path
    """
    # Crop exact bounding box
    x1, y1 = max(0, block.x), max(0, block.y)
    x2 = min(pil_image.width, block.x + block.width)
    y2 = min(pil_image.height, block.y + block.height)
    region = pil_image.crop((x1, y1, x2, y2))
    np_region = np.array(region)
    
    # Convert to grayscale for binary mask
    gray = cv2.cvtColor(np_region, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Determine if text is dark or light
    text_is_dark = np.mean(gray) > 127
    if text_is_dark:
        binary = cv2.bitwise_not(binary)
    
    # Extract text and background pixels
    text_mask = binary == 255
    bg_mask = binary == 0
    
    if np.any(text_mask):
        text_pixels = np_region[text_mask]
        text_color = tuple(int(x) for x in np.median(text_pixels, axis=0))
    else:
        text_color = (0, 0, 0)
    
    if np.any(bg_mask):
        bg_pixels = np_region[bg_mask]
        bg_color = tuple(int(x) for x in np.median(bg_pixels, axis=0))
    else:
        bg_color = (255, 255, 255)
    
    # Detect bold from edge thickness
    edges = cv2.Canny(gray, 50, 150)
    if np.any(edges):
        dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 3)
        avg_stroke = np.mean(dist_transform[dist_transform > 0]) if np.any(dist_transform > 0) else 1
        is_bold = avg_stroke > 2.5
    else:
        is_bold = False
    
    # Detect italic from character slant
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    is_italic = False
    if contours:
        angles = []
        for cnt in contours:
            if len(cnt) >= 5:
                rect = cv2.minAreaRect(cnt)
                angle = abs(rect[2])
                if angle > 5 and angle < 85:
                    angles.append(angle)
        if angles and np.mean(angles) > 5:
            is_italic = True
    
    # Detect shadow (check region below-right)
    has_shadow = False
    shadow_color = (0, 0, 0)
    shadow_offset = (0, 0)
    if block.y + block.height + 3 < pil_image.height and block.x + block.width + 3 < pil_image.width:
        shadow_region = np.array(pil_image.crop((block.x + 1, block.y + 1,
                                                   block.x + block.width + 3,
                                                   block.y + block.height + 3)))
        if np.mean(shadow_region) < np.mean(np_region) - 25:
            has_shadow = True
            shadow_color = tuple(int(x) for x in np.median(shadow_region.reshape(-1, 3), axis=0))
            shadow_offset = (1, 1)
    
    # Detect outline (check border pixels)
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(binary, kernel, iterations=1)
    outline_mask = dilated - binary
    has_outline = np.sum(outline_mask) > (block.width + block.height) * 2
    if has_outline and np.any(outline_mask):
        outline_pixels = np_region[outline_mask > 0]
        outline_color = tuple(int(x) for x in np.median(outline_pixels, axis=0))
        outline_width = 1
    else:
        outline_color = (0, 0, 0)
        outline_width = 0
    
    # Match font based on detected style
    best_font_path = match_font_with_style(is_bold, is_italic)
    
    return {
        'color': text_color,
        'background_color': bg_color,
        'font_size': block.font_size_estimate,
        'is_bold': is_bold,
        'is_italic': is_italic,
        'has_shadow': has_shadow,
        'shadow_color': shadow_color,
        'shadow_offset': shadow_offset,
        'has_outline': has_outline,
        'outline_color': outline_color,
        'outline_width': outline_width,
        'opacity': 1.0,
        'letter_spacing': 0,
        'best_font_path': best_font_path
    }


def detect_text_color(pil_image: Image.Image, block: TextBlock) -> tuple[int, int, int]:
    """
    Auto-detect text color from block region.
    This is a simplified version that calls extract_text_properties.
    
    Args:
        pil_image: Source image
        block: Text block to analyze
    
    Returns:
        RGB color tuple
    """
    try:
        props = extract_text_properties(pil_image, block)
        return props['color']
    except:
        return (0, 0, 0)


def replace_all_matching(
    pil_image: Image.Image,
    blocks: list[TextBlock],
    target_text: str,
    new_text: str,
    font_path: str,
    color: tuple[int, int, int]
) -> Image.Image:
    """
    Replace all blocks matching target text.
    
    Args:
        pil_image: Source image
        blocks: All detected text blocks
        target_text: Text to match (case-insensitive)
        new_text: Replacement text
        font_path: Path to font file
        color: RGB color tuple
    
    Returns:
        Image with all matching text replaced
    """
    img = pil_image.copy()
    target_lower = target_text.lower()
    
    for block in blocks:
        if block.text.lower() == target_lower:
            img = replace_text_in_image(img, block, new_text, font_path, color)
    
    return img
