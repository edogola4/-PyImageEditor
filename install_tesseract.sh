#!/bin/bash

echo "=========================================="
echo "Tesseract OCR Easy Installer for macOS"
echo "=========================================="
echo ""

# Check if Homebrew is installed
if command -v brew &> /dev/null; then
    echo "✓ Homebrew is installed"
    echo ""
    echo "Installing Tesseract via Homebrew..."
    echo "This may take 5-10 minutes on first install."
    echo ""
    
    brew install tesseract
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Tesseract installed successfully!"
        echo ""
        tesseract --version
        echo ""
        echo "You can now use the text replacement feature."
        echo "Run: python3 main.py"
    else
        echo ""
        echo "✗ Installation failed. Try manual installation."
    fi
else
    echo "✗ Homebrew is not installed"
    echo ""
    echo "Option 1: Install Homebrew first (recommended)"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "  Then run this script again"
    echo ""
    echo "Option 2: Use Conda (if you have Anaconda/Miniconda)"
    echo "  conda install -c conda-forge tesseract"
    echo ""
    echo "Option 3: Download pre-built binary"
    echo "  Visit: https://formulae.brew.sh/formula/tesseract"
    echo "  Or: https://tesseract-ocr.github.io/tessdoc/Installation.html"
fi
