"""Singleton OCR engine manager using EasyOCR."""
import numpy as np
from typing import Optional


class OCREngine:
    """Singleton manager for EasyOCR reader."""
    
    _reader = None
    _loading = False
    
    @classmethod
    def get_reader(cls):
        """Get or initialize the EasyOCR reader."""
        if cls._reader is None and not cls._loading:
            cls._loading = True
            import easyocr
            cls._reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            cls._loading = False
        return cls._reader
    
    @classmethod
    def read_image(cls, pil_image) -> list:
        """
        Read text from PIL image.
        
        Returns:
            List of tuples: (bbox_points, text, confidence)
        """
        reader = cls.get_reader()
        np_image = np.array(pil_image.convert('RGB'))
        return reader.readtext(np_image, detail=1, paragraph=False)
