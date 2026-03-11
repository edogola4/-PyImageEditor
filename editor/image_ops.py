"""Image manipulation operations."""
from PIL import Image, ImageEnhance


def brightness(image: Image.Image, factor: float) -> Image.Image:
    """Adjust brightness. Factor: 0.0-2.0, default 1.0."""
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def contrast(image: Image.Image, factor: float) -> Image.Image:
    """Adjust contrast. Factor: 0.0-2.0, default 1.0."""
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def saturation(image: Image.Image, factor: float) -> Image.Image:
    """Adjust saturation. Factor: 0.0-2.0, default 1.0."""
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)


def sharpness(image: Image.Image, factor: float) -> Image.Image:
    """Adjust sharpness. Factor: 0.0-2.0, default 1.0."""
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(factor)


def crop(image: Image.Image, left: int, top: int, right: int, bottom: int) -> Image.Image:
    """Crop image to specified coordinates."""
    if right <= left or bottom <= top:
        raise ValueError("Invalid crop dimensions")
    return image.crop((left, top, right, bottom))


def rotate(image: Image.Image, degrees: float) -> Image.Image:
    """Rotate image by degrees. Degrees: 0-360, expand=True."""
    return image.rotate(-degrees, expand=True)


def flip_horizontal(image: Image.Image) -> Image.Image:
    """Flip image horizontally."""
    return image.transpose(Image.FLIP_LEFT_RIGHT)


def flip_vertical(image: Image.Image) -> Image.Image:
    """Flip image vertically."""
    return image.transpose(Image.FLIP_TOP_BOTTOM)


def resize(image: Image.Image, width: int, height: int, lock_aspect: bool = True) -> Image.Image:
    """Resize image with optional aspect ratio lock."""
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive")
    
    if lock_aspect:
        img_copy = image.copy()
        img_copy.thumbnail((width, height), Image.Resampling.LANCZOS)
        return img_copy
    else:
        return image.resize((width, height), Image.Resampling.LANCZOS)
