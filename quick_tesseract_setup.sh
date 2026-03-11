#!/bin/bash

echo "=========================================="
echo "Quick Tesseract Setup (No Brew Required)"
echo "=========================================="
echo ""

# Create local bin directory
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/tessdata

echo "Downloading pre-built Tesseract binary..."

# For macOS, we'll use a different approach - download from a mirror
ARCH=$(uname -m)

if [ "$ARCH" = "x86_64" ]; then
    echo "Detected Intel Mac (x86_64)"
    BINARY_URL="https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
elif [ "$ARCH" = "arm64" ]; then
    echo "Detected Apple Silicon Mac (arm64)"
fi

echo ""
echo "Alternative: Install via package manager"
echo ""
echo "Since pre-built binaries for macOS require compilation,"
echo "here are the fastest alternatives:"
echo ""
echo "1. Wait for Homebrew (running in background)"
echo "   - Check with: brew list | grep tesseract"
echo ""
echo "2. Use MacPorts (if installed):"
echo "   sudo port install tesseract"
echo ""
echo "3. Use the app WITHOUT text replacement:"
echo "   python3 main.py"
echo "   (All other features work perfectly!)"
echo ""
echo "4. Manual compile (advanced, 10-15 min):"
echo "   cd ~/Downloads/tesseract-5.5.2"
echo "   ./autogen.sh"
echo "   ./configure"
echo "   make"
echo "   sudo make install"
echo ""

# Check if brew install is still running
if pgrep -f "brew install tesseract" > /dev/null; then
    echo "✓ Homebrew is still installing Tesseract in the background"
    echo "  This usually takes 5-10 minutes on first install"
    echo "  You can continue using the app without text replacement"
    echo ""
    echo "  Check progress with: brew list | grep tesseract"
else
    echo "Run one of the commands above to install Tesseract"
fi

echo ""
echo "=========================================="
echo "Meanwhile, use PyImageEditor without OCR:"
echo "=========================================="
echo ""
echo "python3 main.py"
echo ""
echo "Available features:"
echo "  ✓ Image adjustments (brightness, contrast, etc.)"
echo "  ✓ Filters (grayscale, sepia, blur, etc.)"
echo "  ✓ Shapes and drawing"
echo "  ✓ Manual text overlay"
echo "  ✓ Crop, rotate, resize, flip"
echo "  ✓ Undo/redo"
echo ""
