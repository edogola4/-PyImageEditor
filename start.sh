#!/bin/bash

echo "PyImageEditor - Setup and Launch Script"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Check Tesseract installation
if ! command -v tesseract &> /dev/null; then
    echo "⚠ Warning: Tesseract OCR not found"
    echo "  Font detection will not work without Tesseract"
    echo "  Install with: brew install tesseract (macOS) or sudo apt install tesseract-ocr (Linux)"
    echo ""
else
    echo "✓ Tesseract OCR found"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Launch application
echo ""
echo "Launching PyImageEditor..."
echo ""
python3 main.py
