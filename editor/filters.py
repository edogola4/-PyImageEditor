"""Image filter operations."""
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np
try:
    import cv2
except ImportError:
    cv2 = None


def to_grayscale(image: Image.Image) -> Image.Image:
    """Convert image to grayscale."""
    return image.convert('L').convert('RGB')


def to_sepia(image: Image.Image) -> Image.Image:
    """Apply sepia tone filter using RGB matrix transform."""
    img_array = np.array(image, dtype=np.float32)
    sepia_matrix = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])
    sepia_img = img_array @ sepia_matrix.T
    sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
    return Image.fromarray(sepia_img)


def apply_blur(image: Image.Image, radius: int = 2) -> Image.Image:
    """Apply Gaussian blur filter."""
    return image.filter(ImageFilter.GaussianBlur(radius))


def apply_sharpen(image: Image.Image) -> Image.Image:
    """Apply sharpen filter."""
    return image.filter(ImageFilter.SHARPEN)


def edge_detection(image: Image.Image) -> Image.Image:
    """Apply edge detection using Canny algorithm."""
    try:
        import cv2
        img_array = np.array(image.convert('L'))
        edges = cv2.Canny(img_array, 100, 200)
        return Image.fromarray(edges).convert('RGB')
    except ImportError:
        return image.filter(ImageFilter.FIND_EDGES).convert('RGB')


def emboss(image: Image.Image) -> Image.Image:
    """Apply emboss filter."""
    return image.filter(ImageFilter.EMBOSS)


def create_text_mask(region: Image.Image) -> Image.Image:
    """
    Create a high-quality binary mask isolating text pixels from background.
    
    Args:
        region: Image region containing text
    
    Returns:
        PIL Image mask (L mode) where 255=text, 0=background
    """
    gray = np.array(region.convert('L'))
    h, w = gray.shape
    
    # Sample corners AND edges for better background detection
    samples = []
    
    # Corners
    samples.append(gray[0, 0])
    if w > 1:
        samples.append(gray[0, w-1])
    if h > 1:
        samples.append(gray[h-1, 0])
    if h > 1 and w > 1:
        samples.append(gray[h-1, w-1])
    
    # Edge midpoints for better sampling
    if w > 2:
        samples.append(gray[0, w//2])  # Top middle
        if h > 1:
            samples.append(gray[h-1, w//2])  # Bottom middle
    if h > 2:
        samples.append(gray[h//2, 0])  # Left middle
        if w > 1:
            samples.append(gray[h//2, w-1])  # Right middle
    
    bg_luminance = np.mean(samples)
    
    # Adaptive thresholding with tighter threshold for better text isolation
    if cv2 is not None:
        if bg_luminance < 128:
            # Dark background: text is LIGHT
            threshold = int(bg_luminance + 40)  # Increased from 30 to 40
            _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        else:
            # Light background: text is DARK
            threshold = int(bg_luminance - 40)  # Increased from 30 to 40
            _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
        
        # Clean up mask with morphological operations
        kernel = np.ones((3, 3), np.uint8)  # Increased from (2,2) to (3,3)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Dilate slightly to ensure we capture all text pixels
        kernel_dilate = np.ones((2, 2), np.uint8)
        mask = cv2.dilate(mask, kernel_dilate, iterations=1)
    else:
        # Fallback without cv2
        threshold = int(bg_luminance + 40) if bg_luminance < 128 else int(bg_luminance - 40)
        if bg_luminance < 128:
            mask = np.where(gray > threshold, 255, 0).astype(np.uint8)
        else:
            mask = np.where(gray < threshold, 255, 0).astype(np.uint8)
    
    return Image.fromarray(mask, mode='L')


def apply_text_only_filter(
    region: Image.Image,
    filter_type: str,
    intensity: float = 1.0
) -> Image.Image:
    """
    Apply filter ONLY to text pixels with MAXIMUM effectiveness.
    Background stays completely untouched.
    
    Args:
        region: Image region containing text
        filter_type: Filter name
        intensity: Filter intensity
    
    Returns:
        Image with filter applied only to text pixels
    """
    text_mask = create_text_mask(region)
    
    # Convert to numpy for pixel-level manipulation
    original_np = np.array(region.convert('RGB'))
    mask_np = np.array(text_mask)
    
    # Apply filter with ENHANCED intensity for better visibility
    if filter_type == "blur":
        radius = max(1.0, intensity * 5)  # Increased from 3 to 5
        filtered = region.filter(ImageFilter.GaussianBlur(radius=radius))
    
    elif filter_type == "sharpen":
        # Apply sharpen multiple times for stronger effect
        filtered = region
        sharpen_amount = 1.0 + intensity * 3.0  # Increased from 2.0 to 3.0
        enhancer = ImageEnhance.Sharpness(filtered)
        filtered = enhancer.enhance(sharpen_amount)
    
    elif filter_type == "brightness":
        # Enhanced brightness range
        enhancer = ImageEnhance.Brightness(region)
        brightness_amount = intensity * 1.5  # Amplify effect
        filtered = enhancer.enhance(brightness_amount)
    
    elif filter_type == "contrast":
        # Enhanced contrast range
        enhancer = ImageEnhance.Contrast(region)
        contrast_amount = intensity * 1.5  # Amplify effect
        filtered = enhancer.enhance(contrast_amount)
    
    elif filter_type == "saturation":
        # Enhanced saturation range
        enhancer = ImageEnhance.Color(region)
        saturation_amount = intensity * 1.5  # Amplify effect
        filtered = enhancer.enhance(saturation_amount)
    
    elif filter_type == "grayscale":
        filtered = region.convert('L').convert('RGB')
    
    elif filter_type == "sepia":
        img = np.array(region.convert('RGB'), dtype=np.float64)
        r = img[:,:,0]*0.393 + img[:,:,1]*0.769 + img[:,:,2]*0.189
        g = img[:,:,0]*0.349 + img[:,:,1]*0.686 + img[:,:,2]*0.168
        b = img[:,:,0]*0.272 + img[:,:,1]*0.534 + img[:,:,2]*0.131
        sepia = np.stack([
            np.clip(r, 0, 255),
            np.clip(g, 0, 255),
            np.clip(b, 0, 255)
        ], axis=2).astype(np.uint8)
        filtered = Image.fromarray(sepia)
    
    elif filter_type == "invert":
        filtered = ImageOps.invert(region.convert('RGB'))
    
    elif filter_type == "emboss":
        # Apply emboss multiple times for stronger effect
        filtered = region.filter(ImageFilter.EMBOSS)
        if intensity > 1.0:
            filtered = filtered.filter(ImageFilter.EMBOSS)
    
    elif filter_type == "pixelate":
        pixel_size = max(2, int(intensity * 15))  # Increased from 10 to 15
        small = region.resize(
            (max(1, region.width // pixel_size),
             max(1, region.height // pixel_size)),
            Image.NEAREST
        )
        filtered = small.resize(region.size, Image.NEAREST)
    
    else:
        filtered = region
    
    # Convert filtered to numpy
    filtered_np = np.array(filtered.convert('RGB'))
    
    # Create result by blending at pixel level
    result_np = original_np.copy()
    
    # Apply filtered pixels ONLY where mask indicates text
    # Use mask as alpha channel for precise control
    mask_3d = np.stack([mask_np, mask_np, mask_np], axis=2) / 255.0
    
    # Blend: result = filtered * mask + original * (1 - mask)
    result_np = (filtered_np * mask_3d + original_np * (1 - mask_3d)).astype(np.uint8)
    
    return Image.fromarray(result_np)


def apply_named_filter(
    region: Image.Image,
    filter_type: str,
    intensity: float = 1.0
) -> Image.Image:
    """
    Apply named filter to image region.
    Most filters only affect text pixels, leaving background untouched.
    
    Args:
        region: Image region to filter
        filter_type: Filter name (grayscale, sepia, blur, etc.)
        intensity: Filter intensity (0.0 to 2.0)
    
    Returns:
        Filtered image region
    """
    filter_type = filter_type.lower()
    
    try:
        # Filters that affect ONLY text pixels (background stays untouched)
        text_only_filters = [
            'sharpen', 'blur', 'brightness', 'contrast', 'saturation',
            'grayscale', 'sepia', 'invert', 'emboss', 'pixelate'
        ]
        
        if filter_type in text_only_filters:
            return apply_text_only_filter(region, filter_type, intensity)
        
        # Filters that affect entire region (artistic/special effects)
        if filter_type == "edge_detection" or filter_type == "edge detection":
            if cv2 is None:
                return region.filter(ImageFilter.FIND_EDGES).convert('RGB')
            cv_img = cv2.cvtColor(np.array(region), cv2.COLOR_RGB2BGR)
            edges = cv2.Canny(cv_img, 50, 150)
            edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            return Image.fromarray(edges_rgb)
        
        elif filter_type == "highlight":
            enhancer = ImageEnhance.Brightness(region)
            bright = enhancer.enhance(1.4)
            overlay = Image.new('RGB', region.size, (255, 255, 0))
            return Image.blend(bright, overlay, alpha=0.25)
        
        elif filter_type == "redact":
            return Image.new('RGB', region.size, (0, 0, 0))
        
        elif filter_type == "whiteredact" or filter_type == "white redact":
            return Image.new('RGB', region.size, (255, 255, 255))
        
        else:
            return region
    
    except Exception:
        return region
