# Tesseract OCR Installation Guide

## Quick Install Options

### Option 1: Homebrew (Recommended for macOS)
```bash
brew install tesseract
```
**Note:** First install may take 5-10 minutes as it downloads dependencies.

### Option 2: Direct Download (Faster for macOS)
1. Download pre-built binary from: https://github.com/tesseract-ocr/tesseract/releases
2. Or use MacPorts:
   ```bash
   sudo port install tesseract
   ```

### Option 3: Conda (If you use Anaconda/Miniconda)
```bash
conda install -c conda-forge tesseract
```

### Option 4: Manual Binary (Fastest)
Download from: https://digi.bib.uni-mannheim.de/tesseract/
- For macOS: Download the .pkg installer
- Double-click to install
- Add to PATH: `export PATH="/usr/local/bin:$PATH"`

## Verify Installation

After installing, verify it works:
```bash
tesseract --version
```

Should output something like:
```
tesseract 5.x.x
```

## Add to PATH (if needed)

If tesseract is installed but not found:

### macOS/Linux
Add to `~/.zshrc` or `~/.bash_profile`:
```bash
export PATH="/usr/local/bin:$PATH"
export PATH="/opt/homebrew/bin:$PATH"  # For M1/M2 Macs
```

Then reload:
```bash
source ~/.zshrc
```

### Check Installation Location
```bash
# Find where tesseract is installed
find /usr -name tesseract 2>/dev/null
find /opt -name tesseract 2>/dev/null
```

## Using the App Without Tesseract

The text replacement feature requires Tesseract OCR. However, all other features work fine:
- Image adjustments (brightness, contrast, etc.)
- Filters (grayscale, sepia, blur, etc.)
- Shapes and drawing
- Manual text overlay (without detection)
- Crop, rotate, resize, flip

## Troubleshooting

### "tesseract is not installed"
- Install using one of the methods above
- Restart your terminal/IDE after installation
- Verify with `tesseract --version`

### "not in your PATH"
- Add tesseract location to PATH (see above)
- Restart terminal
- Try running from a new terminal window

### Still not working?
- Check if Python can find it:
  ```bash
  python3 -c "import pytesseract; print(pytesseract.get_tesseract_version())"
  ```
- If this fails, set the path manually in Python:
  ```python
  pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
  ```

## Quick Test

After installation, test with:
```bash
cd /Users/brandon/image_editor
python3 verify_text_replacement.py
```

Should show: "✓ Tesseract binary found"
