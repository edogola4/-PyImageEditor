"""Image filter operations."""
from PIL import Image, ImageFilter
import numpy as np


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
