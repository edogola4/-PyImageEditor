"""Photorealistic inpainting engine for seamless text removal and replacement."""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter
from typing import Tuple
from utils.color_utils import sanitize_color, sanitize_color_with_alpha


def analyze_background_type(pil_image: Image.Image, block) -> dict:
    """
    Analyze background texture type around text block.
    
    Returns:
        dict with 'type' (solid/gradient/textured) and 'variance'
    """
    # Extract border ring (20px around text block)
    padding = 20
    x1 = max(0, block.x - padding)
    y1 = max(0, block.y - padding)
    x2 = min(pil_image.width, block.x + block.width + padding)
    y2 = min(pil_image.height, block.y + block.height + padding)
    
    # Get border region
    border_region = pil_image.crop((x1, y1, x2, y2))
    np_border = np.array(border_region)
    
    # Create mask to exclude the text area itself
    mask = np.ones(np_border.shape[:2], dtype=bool)
    inner_x1 = block.x - x1
    inner_y1 = block.y - y1
    inner_x2 = inner_x1 + block.width
    inner_y2 = inner_y1 + block.height
    
    if inner_x1 >= 0 and inner_y1 >= 0 and inner_x2 <= mask.shape[1] and inner_y2 <= mask.shape[0]:
        mask[inner_y1:inner_y2, inner_x1:inner_x2] = False
    
    # Sample only border pixels
    border_pixels = np_border[mask]
    
    if len(border_pixels) == 0:
        return {'type': 'solid', 'variance': 0, 'pixels': np_border}
    
    # Calculate variance
    variance = np.var(border_pixels)
    
    # Classify background type
    if variance < 10:
        bg_type = 'solid'
    elif variance < 50:
        bg_type = 'gradient'
    else:
        bg_type = 'textured'
    
    return {
        'type': bg_type,
        'variance': variance,
        'pixels': border_pixels,
        'border_region': np_border
    }


def inpaint_solid_background(pil_image: Image.Image, block, bg_info: dict) -> Image.Image:
    """Inpaint solid color background with NO blur."""
    img = pil_image.copy()
    
    # Compute median color from border pixels
    median_color = np.median(bg_info['pixels'], axis=0)
    median_color = sanitize_color(median_color, fallback=(255, 255, 255))
    
    # Fill exact region with median color - NO padding, NO blur
    x1 = max(0, block.x)
    y1 = max(0, block.y)
    x2 = min(img.width, block.x + block.width)
    y2 = min(img.height, block.y + block.height)
    
    # Fill with median color - sharp edges
    draw = ImageDraw.Draw(img)
    draw.rectangle([x1, y1, x2, y2], fill=median_color)
    
    return img


def inpaint_gradient_background(pil_image: Image.Image, block, bg_info: dict) -> Image.Image:
    """Inpaint gradient background with directional color interpolation."""
    img = pil_image.copy()
    np_img = np.array(img)
    
    # Sample colors from edges
    x1, y1 = block.x, block.y
    x2, y2 = block.x + block.width, block.y + block.height
    
    # Clamp to image bounds
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(img.width, x2)
    y2 = min(img.height, y2)
    
    # Sample left and right edge colors
    left_sample_x = max(0, x1 - 5)
    right_sample_x = min(img.width - 1, x2 + 5)
    
    left_colors = np_img[y1:y2, left_sample_x:left_sample_x+1].mean(axis=(0, 1))
    right_colors = np_img[y1:y2, right_sample_x:right_sample_x+1].mean(axis=(0, 1))
    
    # Sample top and bottom edge colors
    top_sample_y = max(0, y1 - 5)
    bottom_sample_y = min(img.height - 1, y2 + 5)
    
    top_colors = np_img[top_sample_y:top_sample_y+1, x1:x2].mean(axis=(0, 1))
    bottom_colors = np_img[bottom_sample_y:bottom_sample_y+1, x1:x2].mean(axis=(0, 1))
    
    # Create horizontal gradient
    width = x2 - x1
    height = y2 - y1
    
    h_gradient = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(width):
        alpha = i / max(width - 1, 1)
        color = (1 - alpha) * left_colors + alpha * right_colors
        h_gradient[:, i] = color.astype(np.uint8)
    
    # Create vertical gradient
    v_gradient = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        alpha = i / max(height - 1, 1)
        color = (1 - alpha) * top_colors + alpha * bottom_colors
        v_gradient[i, :] = color.astype(np.uint8)
    
    # Blend both gradients
    blended_gradient = (h_gradient.astype(float) * 0.5 + v_gradient.astype(float) * 0.5).astype(np.uint8)
    
    # Apply feathering at edges
    feather_size = 2
    mask = np.ones((height, width), dtype=float)
    for i in range(feather_size):
        alpha = (i + 1) / (feather_size + 1)
        mask[i, :] *= alpha
        mask[-(i+1), :] *= alpha
        mask[:, i] *= alpha
        mask[:, -(i+1)] *= alpha
    
    # Blend with original
    original_region = np_img[y1:y2, x1:x2].copy()
    for c in range(3):
        np_img[y1:y2, x1:x2, c] = (
            blended_gradient[:, :, c] * mask + 
            original_region[:, :, c] * (1 - mask)
        ).astype(np.uint8)
    
    return Image.fromarray(np_img)


def inpaint_textured_background(pil_image: Image.Image, block) -> Image.Image:
    """Inpaint textured/photo background using OpenCV's intelligent inpainting."""
    # Convert PIL to OpenCV format
    cv_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    # Create inpainting mask
    mask = np.zeros(cv_img.shape[:2], dtype=np.uint8)
    
    # Expand region slightly for better inpainting
    padding = 3
    x1 = max(0, block.x - padding)
    y1 = max(0, block.y - padding)
    x2 = min(cv_img.shape[1], block.x + block.width + padding)
    y2 = min(cv_img.shape[0], block.y + block.height + padding)
    
    mask[y1:y2, x1:x2] = 255
    
    # Apply OpenCV inpainting (TELEA algorithm for texture reconstruction)
    inpainted = cv2.inpaint(cv_img, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    
    # Convert back to PIL
    result = Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))
    
    # Apply subtle smoothing at the boundary
    result_np = np.array(result)
    original_np = np.array(pil_image)
    
    # Create soft edge mask
    edge_mask = np.zeros(mask.shape, dtype=float)
    edge_mask[y1:y2, x1:x2] = 1.0
    edge_mask = gaussian_filter(edge_mask, sigma=1.5)
    
    # Blend with original using soft mask
    for c in range(3):
        result_np[:, :, c] = (
            result_np[:, :, c] * edge_mask + 
            original_np[:, :, c] * (1 - edge_mask)
        ).astype(np.uint8)
    
    return Image.fromarray(result_np)


def smart_inpaint_region(pil_image: Image.Image, block) -> Image.Image:
    """
    Intelligently inpaint text region based on background type.
    
    Returns image with text removed and background reconstructed.
    """
    # Analyze background type
    bg_info = analyze_background_type(pil_image, block)
    
    # Apply appropriate inpainting method
    if bg_info['type'] == 'solid':
        return inpaint_solid_background(pil_image, block, bg_info)
    elif bg_info['type'] == 'gradient':
        return inpaint_gradient_background(pil_image, block, bg_info)
    else:  # textured
        return inpaint_textured_background(pil_image, block)


def detect_text_style(pil_image: Image.Image, block) -> dict:
    """
    Detect text rendering style (shadow, outline, etc.).
    
    Returns dict with style properties.
    """
    # Extract region around text
    padding = 5
    x1 = max(0, block.x - padding)
    y1 = max(0, block.y - padding)
    x2 = min(pil_image.width, block.x + block.width + padding)
    y2 = min(pil_image.height, block.y + block.height + padding)
    
    region = pil_image.crop((x1, y1, x2, y2))
    np_region = np.array(region)
    
    # Detect shadow (darker pixels below/right of text)
    has_shadow = False
    shadow_offset = (0, 0)
    
    # Simple shadow detection: check if there are darker pixels offset from text
    if y2 + 2 < pil_image.height and x2 + 2 < pil_image.width:
        shadow_region = np.array(pil_image.crop((block.x + 1, block.y + 1, 
                                                   min(block.x + block.width + 2, pil_image.width),
                                                   min(block.y + block.height + 2, pil_image.height))))
        if shadow_region.size > 0 and np.mean(shadow_region) < np.mean(np_region) - 20:
            has_shadow = True
            shadow_offset = (1, 1)
    
    return {
        'has_shadow': has_shadow,
        'shadow_offset': shadow_offset,
        'has_outline': False,  # Simplified for now
        'outline_color': (0, 0, 0)
    }


def render_matched_text(
    image: Image.Image,
    block,
    new_text: str,
    properties: dict
) -> Image.Image:
    """
    Render replacement text with ALL original properties matched exactly.
    Uses properties dict from extract_text_properties().
    
    Args:
        image: Image to draw on
        block: Original text block
        new_text: Replacement text
        properties: Dict with all detected properties
    
    Returns:
        Image with text rendered matching original style
    """
    img = image.copy()
    
    # Render at 3x resolution for anti-aliasing
    scale = 3
    high_res_size = (block.width * scale, block.height * scale)
    text_layer = Image.new('RGBA', high_res_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    
    # Load font with detected properties
    font_path = properties['best_font_path']
    font_size = properties['font_size'] * scale
    
    try:
        if font_path and font_path != "default":
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Calculate text position
    bbox = draw.textbbox((0, 0), new_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Auto-adjust font size if text doesn't fit
    while text_width > high_res_size[0] and font_size > 8 * scale:
        font_size -= scale
        try:
            if font_path and font_path != "default":
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), new_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    
    text_x = (high_res_size[0] - text_width) // 2
    text_y = (high_res_size[1] - text_height) // 2
    
    # Render shadow if detected
    if properties['has_shadow']:
        shadow_offset = (properties['shadow_offset'][0] * scale, 
                        properties['shadow_offset'][1] * scale)
        shadow_color = sanitize_color_with_alpha(properties['shadow_color'], 180, fallback=(80, 80, 80, 180))
        draw.text((text_x + shadow_offset[0], text_y + shadow_offset[1]),
                 new_text, fill=shadow_color, font=font)
    
    # Render outline if detected
    if properties['has_outline']:
        outline_color = sanitize_color_with_alpha(properties['outline_color'], 255, fallback=(0, 0, 0, 255))
        outline_width = properties['outline_width'] * scale
        # Draw outline by rendering text in 8 directions
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if dx != 0 or dy != 0:
                    draw.text((text_x + dx, text_y + dy), new_text, 
                             fill=outline_color, font=font)
    
    # Render main text with EXACT detected color
    text_color = sanitize_color_with_alpha(properties['color'], int(properties['opacity'] * 255), fallback=(0, 0, 0, 255))
    draw.text((text_x, text_y), new_text, fill=text_color, font=font)
    
    # Simulate bold if needed and font doesn't have bold variant
    if properties['is_bold'] and 'bold' not in font_path.lower():
        draw.text((text_x + 1, text_y), new_text, fill=text_color, font=font)
    
    # Downscale with high-quality resampling
    text_layer = text_layer.resize((block.width, block.height), Image.Resampling.LANCZOS)
    
    # Paste with alpha blending
    img.paste(text_layer, (block.x, block.y), text_layer)
    
    return img


def match_image_grain(original: Image.Image, edited: Image.Image, block) -> Image.Image:
    """
    Match film grain and noise from original to edited region.
    """
    orig_np = np.array(original)
    edit_np = np.array(edited)
    
    # Extract region around edit
    padding = 10
    x1 = max(0, block.x - padding)
    y1 = max(0, block.y - padding)
    x2 = min(original.width, block.x + block.width + padding)
    y2 = min(original.height, block.y + block.height + padding)
    
    # Analyze grain in surrounding area
    surround_region = orig_np[y1:y2, x1:x2]
    
    # Compute high-frequency noise level
    if surround_region.size > 0:
        noise_level = np.std(surround_region.astype(float) - gaussian_filter(surround_region.astype(float), sigma=1))
        
        # Add matched noise to edited region
        if noise_level > 2:  # Only if significant grain exists
            edit_region = edit_np[block.y:block.y+block.height, block.x:block.x+block.width]
            noise = np.random.normal(0, noise_level * 0.5, edit_region.shape)
            edit_region = np.clip(edit_region.astype(float) + noise, 0, 255).astype(np.uint8)
            edit_np[block.y:block.y+block.height, block.x:block.x+block.width] = edit_region
    
    return Image.fromarray(edit_np)


def match_local_brightness(original: Image.Image, edited: Image.Image, block) -> Image.Image:
    """
    Match brightness and contrast of edited region to surroundings.
    """
    orig_np = np.array(original).astype(float)
    edit_np = np.array(edited).astype(float)
    
    # Sample surrounding region
    padding = 15
    x1 = max(0, block.x - padding)
    y1 = max(0, block.y - padding)
    x2 = min(original.width, block.x + block.width + padding)
    y2 = min(original.height, block.y + block.height + padding)
    
    # Create mask excluding the text block itself
    surround_mask = np.ones((y2 - y1, x2 - x1), dtype=bool)
    inner_x1 = block.x - x1
    inner_y1 = block.y - y1
    inner_x2 = inner_x1 + block.width
    inner_y2 = inner_y1 + block.height
    
    if inner_x1 >= 0 and inner_y1 >= 0:
        surround_mask[inner_y1:inner_y2, inner_x1:inner_x2] = False
    
    surround_region = orig_np[y1:y2, x1:x2][surround_mask]
    
    if len(surround_region) > 0:
        # Calculate surrounding brightness
        surround_mean = np.mean(surround_region)
        surround_std = np.std(surround_region)
        
        # Calculate edited region brightness
        edit_region = edit_np[block.y:block.y+block.height, block.x:block.x+block.width]
        edit_mean = np.mean(edit_region)
        edit_std = np.std(edit_region)
        
        # Match brightness and contrast
        if edit_std > 0:
            edit_region = (edit_region - edit_mean) * (surround_std / edit_std) + surround_mean
            edit_region = np.clip(edit_region, 0, 255)
            edit_np[block.y:block.y+block.height, block.x:block.x+block.width] = edit_region
    
    return Image.fromarray(edit_np.astype(np.uint8))


def post_process_edit(
    original_image: Image.Image,
    edited_image: Image.Image,
    block
) -> Image.Image:
    """
    Apply post-processing to make edit indistinguishable from original.
    
    Matches grain, brightness, and compression artifacts.
    """
    # Match film grain
    result = match_image_grain(original_image, edited_image, block)
    
    # Match local brightness and contrast
    result = match_local_brightness(original_image, result, block)
    
    return result


def professional_replace_text(
    pil_image: Image.Image,
    block,
    new_text: str,
    font_path: str = None,
    color: Tuple[int, int, int] = None,
    font_size: int = None
) -> Image.Image:
    """
    Professional-grade text replacement with photorealistic results.
    
    CRITICAL: This function AUTO-DETECTS all properties from original text.
    The font_path and color parameters are OPTIONAL overrides only.
    If not provided, properties are extracted from the original text.
    
    This is the master function that combines all techniques.
    """
    from editor.text_editor import extract_text_properties, render_replacement_text
    
    # Step 1: Extract ALL properties from original text FIRST
    properties = extract_text_properties(pil_image, block)
    
    # Allow manual overrides (but default to auto-detected)
    if color is not None:
        properties['color'] = color
    if font_path is not None and font_path != "default":
        properties['best_font_path'] = font_path
    if font_size is not None:
        properties['font_size'] = font_size
    
    # Step 2: Remove original text with intelligent inpainting
    img = smart_inpaint_region(pil_image, block)
    
    # Step 3: Render new text with SHARP rendering (NO blur)
    # Use render_replacement_text from text_editor.py which renders at exact size
    img = render_replacement_text(img, block, new_text, properties)
    
    # Step 4: NO post-processing blur - keep text sharp
    # Only match grain if significant noise exists
    orig_np = np.array(pil_image)
    edit_np = np.array(img)
    
    # Sample surrounding region for noise
    padding = 10
    x1 = max(0, block.x - padding)
    y1 = max(0, block.y - padding)
    x2 = min(pil_image.width, block.x + block.width + padding)
    y2 = min(pil_image.height, block.y + block.height + padding)
    
    surround_region = orig_np[y1:y2, x1:x2]
    if surround_region.size > 0:
        noise_level = np.std(surround_region.astype(float) - gaussian_filter(surround_region.astype(float), sigma=1))
        
        # Only add grain if original has significant noise (> 5)
        if noise_level > 5:
            edit_region = edit_np[block.y:block.y+block.height, block.x:block.x+block.width]
            noise = np.random.normal(0, noise_level * 0.3, edit_region.shape)
            edit_region = np.clip(edit_region.astype(float) + noise, 0, 255).astype(np.uint8)
            edit_np[block.y:block.y+block.height, block.x:block.x+block.width] = edit_region
            img = Image.fromarray(edit_np)
    
    return img


def professional_delete_text(
    pil_image: Image.Image,
    block
) -> Image.Image:
    """
    Professional-grade text deletion with photorealistic background reconstruction.
    
    Text is completely removed with no visible artifacts.
    """
    # Step 1: Remove text with intelligent inpainting
    img = smart_inpaint_region(pil_image, block)
    
    # Step 2: Post-process to match grain and lighting
    img = post_process_edit(pil_image, img, block)
    
    return img
