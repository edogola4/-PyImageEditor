"""
PyImageEditor - Complete Image Editing Desktop Application

DEPENDENCIES (install these first):
pip install Pillow opencv-python pytesseract fonttools numpy
pip install tkinter (usually built-in with Python)

System Requirements:
- Install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki
- On Mac: brew install tesseract
- On Linux: sudo apt install tesseract-ocr
- On Windows: download installer from above link, add to PATH

Features:
- Support for JPEG, PNG, WEBP, BMP, TIFF, GIF formats
- Brightness, contrast, saturation, sharpness adjustment
- Crop, rotate, flip, resize operations
- Text overlays with automatic font detection and matching
- Shape drawing (rectangle, circle, line)
- Filters: grayscale, sepia, blur, sharpen, edge detection, emboss
- Undo/redo history (10 steps)
- Side-by-side original vs edited preview
- Export in original or custom format with quality preservation
"""

import tkinter as tk
from app import ImageEditorApp


def main():
    """Entry point for the application."""
    root = tk.Tk()
    app = ImageEditorApp(root)
    app.run()


if __name__ == "__main__":
    main()
