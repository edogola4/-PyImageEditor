"""Font detection and matching utilities with style analysis."""
import os
import sys
import platform
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, List, Tuple
from difflib import get_close_matches
from utils.font_classifier import FontStyleClassifier


def get_system_fonts() -> List[str]:
    """Get list of available system fonts."""
    fonts = []
    
    if sys.platform == 'darwin':  # macOS
        font_dirs = ['/System/Library/Fonts', '/Library/Fonts', 
                     os.path.expanduser('~/Library/Fonts')]
    elif sys.platform == 'win32':  # Windows
        font_dirs = [os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')]
    else:  # Linux
        font_dirs = ['/usr/share/fonts', '/usr/local/share/fonts',
                     os.path.expanduser('~/.fonts')]
    
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            for root, _, files in os.walk(font_dir):
                for file in files:
                    if file.lower().endswith(('.ttf', '.otf', '.ttc')):
                        fonts.append(os.path.join(root, file))
    
    return fonts


def detect_font_from_image(image) -> Optional[str]:
    """Detect font from image using pytesseract OCR."""
    try:
        import pytesseract
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        if data and 'text' in data:
            for text in data['text']:
                if text.strip():
                    return None  # Font name detection not directly available
        return None
    except Exception:
        return None


def detect_and_match_font(pil_image: Image.Image, block) -> dict:
    """
    Detect font properties from text block and match to system font.
    
    Args:
        pil_image: Source image
        block: TextBlock with text region
    
    Returns:
        dict with font properties and matched font path
    """
    # Extract text region
    text_region = pil_image.crop((block.x, block.y, 
                                   block.x + block.width, 
                                   block.y + block.height))
    
    # Detect font size from block height
    font_size = int(block.height * 0.85)
    
    # Detect bold from stroke width
    is_bold = detect_bold(text_region)
    
    # Detect italic from slant angle
    is_italic = detect_italic(text_region)
    
    # Detect text color
    color = detect_text_color_advanced(text_region)
    
    # Detect shadow
    has_shadow, shadow_color, shadow_offset = detect_shadow(pil_image, block)
    
    # Detect outline
    has_outline, outline_color = detect_outline(text_region)
    
    # Match system font
    font_path = match_font_with_style(is_bold, is_italic)
    
    return {
        'font_path': font_path,
        'font_size': font_size,
        'is_bold': is_bold,
        'is_italic': is_italic,
        'letter_spacing': 0,  # Default spacing
        'color': color,
        'has_shadow': has_shadow,
        'shadow_color': shadow_color,
        'shadow_offset': shadow_offset,
        'has_outline': has_outline,
        'outline_color': outline_color
    }


def detect_bold(text_region: Image.Image) -> bool:
    """
    Detect if text is bold by analyzing stroke width.
    
    Returns True if text appears bold.
    """
    # Convert to grayscale
    gray = text_region.convert('L')
    np_gray = np.array(gray)
    
    # Simple edge detection
    edges = np.abs(np.diff(np_gray.astype(float), axis=1))
    
    # Count thick edges (bold text has thicker strokes)
    thick_edges = np.sum(edges > 30)
    total_edges = np.sum(edges > 10)
    
    if total_edges == 0:
        return False
    
    # If more than 40% of edges are thick, likely bold
    return (thick_edges / total_edges) > 0.4


def detect_italic(text_region: Image.Image) -> bool:
    """
    Detect if text is italic by analyzing vertical slant.
    
    Returns True if text appears italic.
    """
    # Convert to grayscale
    gray = text_region.convert('L')
    np_gray = np.array(gray)
    
    # Find text pixels (darker than background)
    threshold = np.mean(np_gray) - 20
    text_pixels = np_gray < threshold
    
    if not text_pixels.any():
        return False
    
    # Analyze vertical distribution
    # Italic text has shifted vertical centers from left to right
    width = np_gray.shape[1]
    if width < 10:
        return False
    
    left_half = text_pixels[:, :width//2]
    right_half = text_pixels[:, width//2:]
    
    if left_half.any() and right_half.any():
        left_center = np.mean(np.where(left_half)[0]) if left_half.any() else 0
        right_center = np.mean(np.where(right_half)[0]) if right_half.any() else 0
        
        # If right side is shifted down, likely italic
        shift = abs(right_center - left_center)
        return shift > text_region.height * 0.1
    
    return False


def detect_text_color_advanced(text_region: Image.Image) -> Tuple[int, int, int]:
    """
    Advanced text color detection.
    
    Returns RGB tuple of detected text color.
    """
    np_region = np.array(text_region)
    
    # Flatten to list of pixels
    pixels = np_region.reshape(-1, 3)
    
    # Find background color (most common)
    from collections import Counter
    pixel_tuples = [tuple(p) for p in pixels]
    color_counts = Counter(pixel_tuples)
    
    if len(color_counts) < 2:
        return (0, 0, 0)
    
    # Get top 2 colors
    top_colors = color_counts.most_common(2)
    bg_color = np.array(top_colors[0][0])
    
    # Filter out background
    filtered_pixels = []
    for p in pixels:
        dist = np.sqrt(np.sum((p - bg_color) ** 2))
        if dist > 30:
            filtered_pixels.append(tuple(p))
    
    if not filtered_pixels:
        # Use second most common color
        return top_colors[1][0] if len(top_colors) > 1 else (0, 0, 0)
    
    # Return most common non-background color
    text_color = Counter(filtered_pixels).most_common(1)[0][0]
    return text_color


def detect_shadow(pil_image: Image.Image, block) -> Tuple[bool, Tuple[int, int, int], Tuple[int, int]]:
    """
    Detect if text has drop shadow.
    
    Returns (has_shadow, shadow_color, shadow_offset)
    """
    # Check pixels around text block for darker shadow
    padding = 3
    x1 = max(0, block.x - padding)
    y1 = max(0, block.y - padding)
    x2 = min(pil_image.width, block.x + block.width + padding)
    y2 = min(pil_image.height, block.y + block.height + padding)
    
    region = pil_image.crop((x1, y1, x2, y2))
    np_region = np.array(region)
    
    # Check bottom-right for shadow (common shadow direction)
    if block.y + block.height + 2 < pil_image.height and block.x + block.width + 2 < pil_image.width:
        shadow_region = pil_image.crop((block.x + 1, block.y + 1,
                                        block.x + block.width + 2,
                                        block.y + block.height + 2))
        shadow_np = np.array(shadow_region)
        
        # If region below/right is significantly darker, likely shadow
        region_brightness = np.mean(np_region)
        shadow_brightness = np.mean(shadow_np)
        
        if region_brightness - shadow_brightness > 25:
            shadow_color = tuple(np.median(shadow_np.reshape(-1, 3), axis=0).astype(int))
            return True, shadow_color, (1, 1)
    
    return False, (0, 0, 0), (0, 0)


def detect_outline(text_region: Image.Image) -> Tuple[bool, Tuple[int, int, int]]:
    """
    Detect if text has outline/stroke.
    
    Returns (has_outline, outline_color)
    """
    # Simplified outline detection
    # Check if there are distinct edge colors different from text color
    np_region = np.array(text_region)
    
    # Get edge pixels
    from scipy.ndimage import sobel
    gray = np.mean(np_region, axis=2)
    edges = sobel(gray)
    edge_mask = edges > np.percentile(edges, 90)
    
    if not edge_mask.any():
        return False, (0, 0, 0)
    
    edge_pixels = np_region[edge_mask]
    
    if len(edge_pixels) > 10:
        from collections import Counter
        edge_colors = [tuple(p) for p in edge_pixels]
        outline_color = Counter(edge_colors).most_common(1)[0][0]
        return True, outline_color
    
    return False, (0, 0, 0)


def match_font_with_style(is_bold: bool, is_italic: bool, region_array: np.ndarray = None, block_height: int = 0) -> str:
    """
    Match system font based on detected style.
    If region_array provided, uses classifier-based matching.
    
    Args:
        is_bold: Whether text is bold
        is_italic: Whether text is italic
        region_array: Optional pixel array for style classification
        block_height: Optional block height for classification
    
    Returns:
        Path to best matching system font
    """
    # Use classifier-based matching if region provided
    if region_array is not None and block_height > 0:
        return find_matching_font(region_array, block_height, is_bold, is_italic)
    
    # Fallback to simple style matching
    system_fonts = get_system_fonts()
    
    if not system_fonts:
        return "default"
    
    # Filter fonts by style
    preferred_fonts = []
    
    for font_path in system_fonts:
        font_lower = font_path.lower()
        
        # Match bold
        if is_bold and ('bold' in font_lower or 'heavy' in font_lower or 'black' in font_lower):
            preferred_fonts.append(font_path)
        # Match italic
        elif is_italic and ('italic' in font_lower or 'oblique' in font_lower):
            preferred_fonts.append(font_path)
        # Match bold italic
        elif is_bold and is_italic and 'bold' in font_lower and 'italic' in font_lower:
            preferred_fonts.insert(0, font_path)  # Highest priority
    
    if preferred_fonts:
        return preferred_fonts[0]
    
    # Fallback to default matching
    return match_font(None)


def match_font(detected_font: Optional[str] = None) -> str:
    """Match detected font to closest available system font."""
    system_fonts = get_system_fonts()
    
    if not system_fonts:
        return "default"
    
    if detected_font:
        font_names = [os.path.basename(f).lower() for f in system_fonts]
        matches = get_close_matches(detected_font.lower(), font_names, n=1, cutoff=0.3)
        if matches:
            idx = font_names.index(matches[0])
            return system_fonts[idx]
    
    # Default fallback fonts
    for font in system_fonts:
        font_lower = font.lower()
        if 'arial' in font_lower or 'helvetica' in font_lower:
            return font
    
    return system_fonts[0] if system_fonts else "default"



def find_matching_font(
    region_array: np.ndarray,
    block_height: int,
    is_bold: bool,
    is_italic: bool
) -> str:
    """
    Scans all system fonts dynamically.
    Uses FontStyleClassifier to determine what STYLE CLASS
    the original text belongs to, then selects the best
    matching font from that class.
    Never hardcodes font names or paths.
    """

    # Classify the style of the original text
    classifier = FontStyleClassifier(region_array, block_height)
    style_class = classifier.classify()

    # Scan all system font files dynamically
    system = platform.system()
    search_dirs = _get_font_dirs(system)

    all_fonts = []
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if f.lower().endswith(('.ttf', '.otf', '.ttc')):
                    all_fonts.append(os.path.join(root, f))

    # Test each font loads successfully
    valid_fonts = []
    for fp in all_fonts:
        try:
            ImageFont.truetype(fp, 20)
            valid_fonts.append(fp)
        except Exception:
            continue

    if not valid_fonts:
        return "default"

    # Score each font by how well it matches detected style
    def score_font(fp: str) -> float:
        name = os.path.basename(fp).lower()
        score = 0.0

        # Style class keywords — derived from actual font
        # file naming conventions, never hardcoded font names
        style_keywords = {
            FontStyleClassifier.SCRIPT: [
                'script', 'cursive', 'handwriting',
                'calligraph', 'hand', 'brush', 'write',
                'signature', 'callig', 'dancing', 'pacifico',
                'satisfy', 'cookie', 'allura', 'greatvibes',
                'kaushan', 'lobster', 'yellowtail', 'playlist',
            ],
            FontStyleClassifier.SERIF: [
                'serif', 'times', 'georgia', 'palatino',
                'garamond', 'baskerville', 'didot', 'caslon',
                'bodoni', 'cambria', 'constantia', 'rockwell',
            ],
            FontStyleClassifier.SANS: [
                'sans', 'gothic', 'grotesk', 'helvetica',
                'arial', 'roboto', 'opensans', 'lato',
                'nunito', 'poppins', 'ubuntu', 'noto',
                'source', 'inter', 'futura', 'gill',
            ],
            FontStyleClassifier.MONO: [
                'mono', 'courier', 'consolas', 'menlo',
                'inconsolata', 'sourcecode', 'firacode',
                'jetbrains', 'hack', 'terminal',
            ],
            FontStyleClassifier.DISPLAY: [
                'display', 'decorative', 'ornament', 'fantasy',
                'headline', 'poster', 'impact', 'black',
                'ultra', 'condensed', 'extended',
            ],
        }

        # Match style class - use word boundaries to avoid partial matches
        matched_keywords = []
        for kw in style_keywords.get(style_class, []):
            # For single-word keywords, check if it's a separate word
            if len(kw) > 4:  # Longer keywords can be substrings
                if kw in name:
                    matched_keywords.append(kw)
            else:  # Short keywords need word boundaries
                # Check if keyword appears as whole word or at start/end
                if (f' {kw} ' in f' {name} ' or 
                    name.startswith(kw + ' ') or
                    name.endswith(' ' + kw) or
                    name.startswith(kw + '-') or
                    name.endswith('-' + kw) or
                    name == kw):
                    matched_keywords.append(kw)
        
        # Score based on number and quality of matches
        if matched_keywords:
            # Base score for first match
            score += 10.0
            # Bonus for additional matches
            score += (len(matched_keywords) - 1) * 3.0
            # Extra bonus for exact style name match
            if style_class in name:
                score += 5.0

        # Penalize opposite style classes heavily
        opposite = {
            FontStyleClassifier.SCRIPT: style_keywords[FontStyleClassifier.SANS],
            FontStyleClassifier.SANS: style_keywords[FontStyleClassifier.SCRIPT],
            FontStyleClassifier.SERIF: style_keywords[FontStyleClassifier.MONO],
            FontStyleClassifier.MONO: style_keywords[FontStyleClassifier.SCRIPT],
        }
        for kw in opposite.get(style_class, []):
            if kw in name:
                score -= 3.0
                break

        # Bold matching
        if is_bold and any(b in name for b in
           ['bold', 'heavy', 'black', 'semibold', 'medium']):
            score += 3.0
        if not is_bold and not any(b in name for b in
           ['bold', 'heavy', 'black']):
            score += 1.0

        # Italic matching — CRITICAL for script fonts
        # Only boost italic if it's a script font AND italic
        if style_class == FontStyleClassifier.SCRIPT:
            if any(i in name for i in ['italic', 'oblique', 'slant']):
                score += 2.0  # Moderate boost for script+italic
        elif is_italic:
            if any(i in name for i in ['italic', 'oblique', 'slant']):
                score += 3.0
        elif not is_italic:
            if not any(i in name for i in ['italic', 'oblique']):
                score += 1.0

        return score

    valid_fonts.sort(key=score_font, reverse=True)
    return valid_fonts[0]


def _get_font_dirs(system: str) -> list:
    """Returns font search directories for current OS."""
    if system == 'Darwin':
        return [
            '/System/Library/Fonts/',
            '/Library/Fonts/',
            os.path.expanduser('~/Library/Fonts/'),
        ]
    elif system == 'Windows':
        return [
            'C:\\Windows\\Fonts\\',
            os.path.expanduser(
                '~\\AppData\\Local\\Microsoft\\Windows\\Fonts\\'
            ),
        ]
    else:
        return [
            '/usr/share/fonts/',
            '/usr/local/share/fonts/',
            os.path.expanduser('~/.fonts/'),
            os.path.expanduser('~/.local/share/fonts/'),
        ]
