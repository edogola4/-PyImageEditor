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
        Read text from PIL image and merge word-level results into lines.
        
        Returns:
            List of TextBlock objects (line-level, not word-level)
        """
        from editor.text_editor import TextBlock
        from utils.line_merger import merge_into_lines
        
        reader = cls.get_reader()
        np_image = np.array(pil_image.convert('RGB'))
        results = reader.readtext(np_image, detail=1, paragraph=False)
        
        # Step 1: Parse raw EasyOCR results into word-level blocks
        word_blocks = cls._parse_results(results)
        
        # Step 2: Merge word-level blocks into line-level blocks
        line_blocks = merge_into_lines(word_blocks)
        
        return line_blocks
    
    @classmethod
    def _parse_results(cls, results) -> list:
        """Parse EasyOCR results into word-level TextBlock objects."""
        from editor.text_editor import TextBlock
        
        blocks = []
        for idx, (bbox, text, conf) in enumerate(results):
            if conf < 0.35:
                continue
            if not text.strip():
                continue
            
            # EasyOCR bbox = [[x1,y1],[x2,y1],[x2,y2],[x1,y2]]
            xs = [int(pt[0]) for pt in bbox]
            ys = [int(pt[1]) for pt in bbox]
            
            x = min(xs)
            y = min(ys)
            w = max(xs) - min(xs)
            h = max(ys) - min(ys)
            
            if w < 2 or h < 2:
                continue
            
            blocks.append(TextBlock(
                text=text.strip(),
                x=x,
                y=y,
                width=w,
                height=h,
                conf=float(conf),
                font_size_estimate=int(h * 0.75),
                block_id=idx,
            ))
        
        return blocks
