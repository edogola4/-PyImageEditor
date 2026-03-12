"""Text detection, selection, replacement, and deletion engine."""
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
import cv2
from collections import Counter
from utils.ocr_engine import OCREngine
from utils.font_matcher import match_font_with_style
from utils.color_utils import sanitize_color, sanitize_color_with_alpha


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
    constituent_blocks: list = None
    
    def __post_init__(self):
        if self.constituent_blocks is None:
            self.constituent_blocks = []


def detect_all_text(pil_image: Image.Image) -> list[TextBlock]:
    """
    Detect all text blocks in image using EasyOCR.
    Returns line-level blocks (words on same line are merged).
    
    Returns:
        List of TextBlock objects with confidence > 0.40
    """
    blocks = OCREngine.read_image(pil_image)
    
    # Filter by confidence and clamp to image bounds
    filtered_blocks = []
    for block in blocks:
        if block.conf <= 0.40:
            continue
        
        if not block.text.strip():
            continue
        
        # Clamp to image bounds
        x = max(0, min(block.x, pil_image.width - 1))
        y = max(0, min(block.y, pil_image.height - 1))
        x2 = max(0, min(block.x + block.width, pil_image.width))
        y2 = max(0, min(block.y + block.height, pil_image.height))
        width = x2 - x
        height = y2 - y
        
        # Skip degenerate boxes
        if width < 2 or height < 2:
            continue
        
        # Update block with clamped coordinates
        block.x = x
        block.y = y
        block.width = width
        block.height = height
        
        filtered_blocks.append(block)
    
    return filtered_blocks


def erase_text_region(pil_image: Image.Image, block: TextBlock, padding: int = 2, all_blocks: list = None) -> Image.Image:
    """
    Erase text region with smart background inpainting.
    CRITICAL: NO blur applied - background stays sharp.
    CRITICAL: Checks for nearby text blocks to avoid overlap.
    
    Args:
        pil_image: Source image
        block: Text block to erase
        padding: Extra pixels around bounding box (reduced from 6 to 2)
        all_blocks: List of all text blocks to check for collisions
    
    Returns:
        Image with text region erased and background reconstructed
    """
    img = pil_image.copy()
    draw = ImageDraw.Draw(img)
    
    # Start with minimal padding
    x1 = max(0, block.x - padding)
    y1 = max(0, block.y - padding)
    x2 = min(img.width, block.x + block.width + padding)
    y2 = min(img.height, block.y + block.height + padding)
    
    # If we have all_blocks, check for collisions and shrink padding if needed
    if all_blocks:
        for other_block in all_blocks:
            # Skip self
            if other_block.block_id == block.block_id:
                continue
            
            # Check if expanded region would overlap with other block
            other_x1 = other_block.x
            other_y1 = other_block.y
            other_x2 = other_block.x + other_block.width
            other_y2 = other_block.y + other_block.height
            
            # Check for overlap
            if not (x2 < other_x1 or x1 > other_x2 or y2 < other_y1 or y1 > other_y2):
                # There's overlap - shrink the erase region to avoid it
                # Shrink from the side closest to the other block
                
                # If other block is above, don't expand upward
                if other_y2 <= block.y and y1 < other_y2:
                    y1 = max(y1, other_y2)
                
                # If other block is below, don't expand downward  
                if other_y1 >= block.y + block.height and y2 > other_y1:
                    y2 = min(y2, other_y1)
                
                # If other block is to the left, don't expand leftward
                if other_x2 <= block.x and x1 < other_x2:
                    x1 = max(x1, other_x2)
                
                # If other block is to the right, don't expand rightward
                if other_x1 >= block.x + block.width and x2 > other_x1:
                    x2 = min(x2, other_x1)
    
    # Ensure we still have a valid region
    x1 = max(0, min(x1, img.width - 1))
    y1 = max(0, min(y1, img.height - 1))
    x2 = max(x1 + 1, min(x2, img.width))
    y2 = max(y1 + 1, min(y2, img.height))
    
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
    
    # Sanitize color before drawing
    bg_color = sanitize_color(bg_color, fallback=(255, 255, 255))
    
    # Fill region with background color - NO blur
    draw.rectangle([x1, y1, x2, y2], fill=bg_color)
    
    # Background is now ready - text will be rendered on top WITHOUT any blur
    return img


def render_replacement_text(
    image: Image.Image,
    block: TextBlock,
    new_text: str,
    properties: dict
) -> Image.Image:
    """
    FIX 4: Render text at EXACT size with NO downscaling blur.
    Renders directly at final pixel size in single pass.
    
    Args:
        image: Image to draw on (with background already erased)
        block: Original text block
        new_text: Replacement text
        properties: Dict with font_path, font_size, color, shadow, outline
    
    Returns:
        Image with text rendered sharply
    """
    # Track original mode
    original_mode = image.mode
    
    # Work in RGBA throughout
    result = image.copy()
    if result.mode != 'RGBA':
        result = result.convert('RGBA')
    
    # Create transparent text layer
    text_layer = Image.new('RGBA', result.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    
    font_path = properties['best_font_path']
    font_size = properties['font_size']
    color = sanitize_color(properties['color'], fallback=(0, 0, 0))
    
    # Load font at EXACT target size - no scaling
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        try:
            font = ImageFont.truetype(match_font_with_style(False, False), font_size)
        except:
            font = ImageFont.load_default()
    
    # Clamp coordinates to image bounds
    x = max(0, min(block.x, image.width - 1))
    y = max(0, min(block.y, image.height - 1))
    
    # Measure the replacement text with the initial font size
    bbox = draw.textbbox((0, 0), new_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # If replacement text is wider than original, scale down font to fit
    if text_width > block.width:
        # Calculate scale factor needed
        scale_factor = block.width / text_width
        font_size = int(font_size * scale_factor * 0.95)  # 0.95 for safety margin
        font_size = max(8, font_size)
        
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()
        
        # Re-measure
        bbox = draw.textbbox((0, 0), new_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    
    # Ensure text fits within image bounds
    text_right = x + text_width
    text_bottom = y + text_height
    
    while (text_right > image.width or text_bottom > image.height) and font_size > 8:
        font_size -= 1
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), new_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_right = x + text_width
        text_bottom = y + text_height
    
    # RENDER ORDER: shadow -> outline -> main text
    # Each layer at exact size, NO blur applied
    
    # 1. Drop shadow (if detected)
    if properties.get('has_shadow'):
        sx = x + properties['shadow_offset'][0]
        sy = y + properties['shadow_offset'][1]
        shadow_color = sanitize_color_with_alpha(properties['shadow_color'], 180, fallback=(80, 80, 80, 180))
        draw.text((sx, sy), new_text, font=font, fill=shadow_color)
    
    # 2. Outline (if detected)
    if properties.get('has_outline'):
        ow = properties.get('outline_width', 1)
        outline_color = sanitize_color_with_alpha(properties['outline_color'], 255, fallback=(0, 0, 0, 255))
        for dx in range(-ow, ow + 1):
            for dy in range(-ow, ow + 1):
                if dx == 0 and dy == 0:
                    continue
                draw.text((x + dx, y + dy), new_text, font=font, fill=outline_color)
    
    # 3. Main text - exact color with full alpha
    text_color = sanitize_color_with_alpha(color, 255)
    draw.text((x, y), new_text, font=font, fill=text_color)
    
    # Verify overlay has non-transparent pixels
    overlay_array = np.array(text_layer)
    if overlay_array[:, :, 3].max() == 0:
        # Fallback: direct draw on result
        direct_draw = ImageDraw.Draw(result)
        text_color = sanitize_color_with_alpha(color, 255)
        direct_draw.text((x, y), new_text, font=font, fill=text_color)
    else:
        # Safe to composite
        result = Image.alpha_composite(result, text_layer)
    
    # Convert back to original mode at the very end
    if original_mode != 'RGBA':
        result = result.convert(original_mode)
    
    return result


def replace_text_in_image(
    pil_image: Image.Image,
    block: TextBlock,
    new_text: str,
    font_path: str,
    color: tuple[int, int, int]
) -> Image.Image:
    """
    Replace text block with new text.
    FIX 6: Extract properties BEFORE erasing.
    
    Args:
        pil_image: Source image
        block: Text block to replace
        new_text: Replacement text
        font_path: Path to font file (can be overridden by auto-detect)
        color: RGB color tuple (can be overridden by auto-detect)
    
    Returns:
        Image with text replaced
    """
    # CRITICAL: Extract ALL properties from ORIGINAL image BEFORE erasing
    properties = extract_text_properties(pil_image, block)
    # Calculate font size AFTER getting font path so we can measure with the actual font
    properties['font_size'] = calculate_font_size(block, pil_image, properties['best_font_path'], block.text)
    properties['color'] = extract_text_color(pil_image, block)
    
    # Override with user-provided values if specified
    if font_path and font_path != 'default':
        properties['best_font_path'] = font_path
    if color != (0, 0, 0):  # If user specified a color
        properties['color'] = color
    
    # Step 1: Erase original text (background reconstruction only)
    img = erase_text_region(pil_image, block)
    
    # Step 2: Render new text on top (NO blur applied after this)
    img = render_replacement_text(img, block, new_text, properties)
    
    return img


def delete_text_region(
    pil_image: Image.Image,
    block: TextBlock,
    padding: int = 2
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
    padding: int = 2
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
        # Pass all blocks to check for collisions
        img = erase_text_region(img, block, padding, all_blocks=blocks)
    return img


def extract_text_color(pil_image: Image.Image, block: TextBlock) -> tuple[int, int, int]:
    """
    FIX 2: Adaptive color detection that works on both light and dark backgrounds.
    Uses corner sampling to determine background luminance.
    """
    # Crop exact bounding box
    x1, y1 = max(0, block.x), max(0, block.y)
    x2 = min(pil_image.width, block.x + block.width)
    y2 = min(pil_image.height, block.y + block.height)
    
    if x2 <= x1 or y2 <= y1:
        return (0, 0, 0)
    
    crop = pil_image.crop((x1, y1, x2, y2))
    img_array = np.array(crop.convert('RGB'))
    
    if img_array.size == 0:
        return (0, 0, 0)
    
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Sample background from corners (4 corner pixels)
    h, w = gray.shape
    corners = [
        img_array[0, 0],
        img_array[0, min(w-1, w-1)],
        img_array[min(h-1, h-1), 0],
        img_array[min(h-1, h-1), min(w-1, w-1)]
    ]
    bg_color = np.mean(corners, axis=0).astype(int)
    bg_luminance = 0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2]
    
    # Adaptive thresholding based on background luminance
    if bg_luminance < 128:
        # Dark background: text is LIGHT (brighter than bg)
        _, mask = cv2.threshold(gray, int(bg_luminance + 30), 255, cv2.THRESH_BINARY)
    else:
        # Light background: text is DARK (darker than bg)
        _, mask = cv2.threshold(gray, int(bg_luminance - 30), 255, cv2.THRESH_BINARY_INV)
    
    # Extract text pixels
    text_pixels = img_array[mask == 255]
    
    if len(text_pixels) == 0:
        # Fallback: contrasting color
        if bg_luminance > 128:
            return (0, 0, 0)  # black on light
        else:
            return (255, 255, 255)  # white on dark
    
    # Return median color of text pixels
    median_color = np.median(text_pixels, axis=0)
    return sanitize_color(median_color, fallback=(0, 0, 0))


def calculate_font_size(block: TextBlock, pil_image: Image.Image, font_path: str = None, sample_text: str = None) -> int:
    """
    Calculate correct font size that will fit in the bounding box.
    Uses binary search to find the font size that renders at the detected height.
    
    Args:
        block: Text block with dimensions
        pil_image: Source image
        font_path: Path to font file to use for measurement
        sample_text: Sample text to measure (defaults to block.text)
    
    Returns:
        Font size in points that will render at the detected height
    """
    if sample_text is None:
        sample_text = block.text if hasattr(block, 'text') else "Ag"
    
    target_height = block.height
    target_width = block.width
    
    # If no font path provided, use a default
    if not font_path or font_path == "default":
        font_path = match_font_with_style(False, False)
    
    # Binary search for the right font size
    min_size = 8
    max_size = 500
    best_size = target_height
    
    # Try to load the font
    try:
        test_font = ImageFont.truetype(font_path, target_height)
    except:
        # If font fails to load, fall back to simple calculation
        return max(8, min(500, target_height))
    
    # Create a temporary draw context for measurement
    temp_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(temp_img)
    
    # Binary search for optimal size
    for _ in range(15):  # Max 15 iterations
        mid_size = (min_size + max_size) // 2
        
        try:
            font = ImageFont.truetype(font_path, mid_size)
            bbox = draw.textbbox((0, 0), sample_text, font=font)
            rendered_height = bbox[3] - bbox[1]
            rendered_width = bbox[2] - bbox[0]
            
            # Check if this size fits
            if rendered_height < target_height * 0.95:
                # Too small, increase
                min_size = mid_size + 1
                best_size = mid_size
            elif rendered_height > target_height * 1.05:
                # Too large, decrease
                max_size = mid_size - 1
            else:
                # Good fit!
                best_size = mid_size
                break
        except:
            # If font loading fails at this size, try smaller
            max_size = mid_size - 1
    
    # Clamp to sane range
    best_size = max(8, min(500, best_size))
    
    return best_size


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
    
    # Use adaptive thresholding
    bg_luminance = np.mean(gray)
    if bg_luminance < 128:
        _, binary = cv2.threshold(gray, int(bg_luminance + 30), 255, cv2.THRESH_BINARY)
    else:
        _, binary = cv2.threshold(gray, int(bg_luminance - 30), 255, cv2.THRESH_BINARY_INV)
    
    # Extract text and background pixels
    text_mask = binary == 255
    bg_mask = binary == 0
    
    if np.any(text_mask):
        text_pixels = np_region[text_mask]
        text_color = sanitize_color(np.median(text_pixels, axis=0), fallback=(0, 0, 0))
    else:
        text_color = (0, 0, 0)
    
    if np.any(bg_mask):
        bg_pixels = np_region[bg_mask]
        bg_color = sanitize_color(np.median(bg_pixels, axis=0), fallback=(255, 255, 255))
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
            shadow_color = sanitize_color(np.median(shadow_region.reshape(-1, 3), axis=0), fallback=(0, 0, 0))
            shadow_offset = (1, 1)
    
    # Detect outline (check border pixels)
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(binary, kernel, iterations=1)
    outline_mask = dilated - binary
    has_outline = np.sum(outline_mask) > (block.width + block.height) * 2
    if has_outline and np.any(outline_mask):
        outline_pixels = np_region[outline_mask > 0]
        outline_color = sanitize_color(np.median(outline_pixels, axis=0), fallback=(0, 0, 0))
        outline_width = 1
    else:
        outline_color = (0, 0, 0)
        outline_width = 0
    
    # Match font based on detected style using classifier
    best_font_path = match_font_with_style(
        is_bold, is_italic,
        region_array=np_region,
        block_height=block.height
    )
    
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
    Wrapper for extract_text_color.
    
    Args:
        pil_image: Source image
        block: Text block to analyze
    
    Returns:
        RGB color tuple
    """
    try:
        return extract_text_color(pil_image, block)
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
    Each block's properties are extracted from ORIGINAL image before any edits.
    
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
    
    # Extract properties for all matching blocks FIRST (from original image)
    matching_blocks = [b for b in blocks if b.text.lower() == target_lower]
    all_properties = []
    
    for block in matching_blocks:
        props = extract_text_properties(pil_image, block)
        # Calculate font size with the actual font path
        props['font_size'] = calculate_font_size(block, pil_image, props['best_font_path'], block.text)
        props['color'] = extract_text_color(pil_image, block)
        if font_path and font_path != 'default':
            props['best_font_path'] = font_path
        if color != (0, 0, 0):
            props['color'] = color
        all_properties.append(props)
    
    # Now erase and render each block
    for block, props in zip(matching_blocks, all_properties):
        img = erase_text_region(img, block)
        img = render_replacement_text(img, block, new_text, props)
    
    return img


def apply_filter_to_text_region(
    pil_image: Image.Image,
    block: TextBlock,
    filter_type: str,
    intensity: float = 1.0
) -> Image.Image:
    """
    Apply filter ONLY to text block region, leaving rest of image untouched.
    
    STRICT ISOLATION RULES:
    - Only pixels inside bbox are modified
    - Filter receives only cropped region, never full image
    - Original image is never mutated
    
    Args:
        pil_image: Source image
        block: Text block defining region to filter
        filter_type: Filter name (grayscale, sepia, blur, etc.)
        intensity: Filter intensity (0.0 to 2.0)
    
    Returns:
        Image with filter applied only to text region
    """
    from editor.filters import apply_named_filter
    
    # RULE 5: Never mutate original
    result = pil_image.copy()
    
    # RULE 4: Clamp bbox to image bounds
    x1 = max(0, block.x)
    y1 = max(0, block.y)
    x2 = min(pil_image.width, block.x + block.width)
    y2 = min(pil_image.height, block.y + block.height)
    
    # Edge case: region too small
    if (x2 - x1) < 5 or (y2 - y1) < 5:
        raise ValueError("Region too small to filter")
    
    bbox = (x1, y1, x2, y2)
    
    # RULE 3: Filter receives only cropped region
    region = result.crop(bbox)
    
    # Handle different image modes
    original_mode = region.mode
    if original_mode == 'RGBA':
        alpha = region.split()[3]
        region = region.convert('RGB')
    elif original_mode == 'L':
        region = region.convert('RGB')
    
    # Apply filter to region only
    filtered_region = apply_named_filter(region, filter_type, intensity)
    
    # Restore original mode
    if original_mode == 'RGBA':
        filtered_region = filtered_region.convert('RGBA')
        filtered_region.putalpha(alpha)
    elif original_mode == 'L':
        filtered_region = filtered_region.convert('L')
    
    # RULE 2: Paste is the ONLY way filtered pixels re-enter
    result.paste(filtered_region, bbox)
    
    return result
