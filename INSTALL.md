# Installation Guide

Complete installation instructions for PyImageEditor on all platforms.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for first-time OCR model download)

## Quick Install (All Platforms)

```bash
# 1. Clone or download the repository
cd image_editor

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Verify installation
python3 verify_install.py

# 4. Run the application
python3 main.py
```

## Platform-Specific Instructions

### macOS

#### 1. Install Python (if not already installed)
```bash
# Using Homebrew
brew install python@3.11

# Or download from python.org
# https://www.python.org/downloads/macos/
```

#### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

#### 3. Verify Installation
```bash
python3 verify_install.py
```

#### 4. Run Application
```bash
python3 main.py
```

**Note:** tkinter is included with Python from python.org. If using Homebrew Python and tkinter is missing:
```bash
brew install python-tk@3.11
```

---

### Linux (Ubuntu/Debian)

#### 1. Install Python and tkinter
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
```

#### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

#### 3. Verify Installation
```bash
python3 verify_install.py
```

#### 4. Run Application
```bash
python3 main.py
```

**Troubleshooting:**
- If `pip3 install` fails with permissions error, use: `pip3 install --user -r requirements.txt`
- For GPU acceleration (optional): Install CUDA toolkit

---

### Windows

#### 1. Install Python
1. Download Python 3.11+ from https://www.python.org/downloads/windows/
2. Run installer
3. **Important:** Check "Add Python to PATH" during installation
4. Verify installation:
   ```cmd
   python --version
   ```

#### 2. Install Dependencies
Open Command Prompt or PowerShell:
```cmd
pip install -r requirements.txt
```

#### 3. Verify Installation
```cmd
python verify_install.py
```

#### 4. Run Application
```cmd
python main.py
```

**Troubleshooting:**
- If `pip` is not recognized, use: `python -m pip install -r requirements.txt`
- tkinter is included with standard Python installation
- For GPU acceleration (optional): Install CUDA toolkit

---

## Dependencies Explained

### Core Dependencies (Installed via pip)

| Package | Purpose | Size |
|---------|---------|------|
| Pillow | Image processing and manipulation | ~3 MB |
| opencv-python | Advanced filters (edge detection, etc.) | ~50 MB |
| easyocr | Text detection (no external binaries) | ~80 MB + models |
| fonttools | System font enumeration | ~2 MB |
| numpy | Array operations | ~15 MB |
| scipy | Scientific computing | ~30 MB |

### Built-in Dependencies

- **tkinter**: GUI framework (included with Python)

### First Run: OCR Model Download

On first text detection, EasyOCR will download language models:
- English model: ~80 MB
- Downloaded to: `~/.EasyOCR/model/`
- One-time download, cached for future use
- Requires internet connection

---

## Verification

Run the verification script to check all dependencies:

```bash
python3 verify_install.py
```

Expected output:
```
PyImageEditor Installation Verification
==================================================

Python version: 3.11.x
✓ Python version OK

Checking dependencies:
--------------------------------------------------
✓ Pillow installed
✓ opencv-python installed
✓ easyocr installed
✓ fonttools installed
✓ numpy installed
✓ scipy installed
✓ tkinter installed

==================================================
✓ All dependencies installed successfully!

You can now run the application:
  python3 main.py
```

---

## Optional: Virtual Environment

Recommended for isolated dependency management:

### Create Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Deactivate When Done
```bash
deactivate
```

---

## GPU Acceleration (Optional)

For faster text detection on systems with NVIDIA GPUs:

### 1. Install CUDA Toolkit
- Download from: https://developer.nvidia.com/cuda-downloads
- Follow platform-specific installation instructions

### 2. Install GPU-enabled PyTorch
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 3. Verify GPU Support
```python
import torch
print(torch.cuda.is_available())  # Should print True
```

EasyOCR will automatically use GPU if available.

---

## Troubleshooting

### "No module named 'tkinter'"

**Linux:**
```bash
sudo apt install python3-tk
```

**macOS (Homebrew):**
```bash
brew install python-tk@3.11
```

**Windows:**
Reinstall Python from python.org with "tcl/tk and IDLE" option checked.

---

### "pip: command not found"

**macOS/Linux:**
```bash
python3 -m ensurepip --upgrade
```

**Windows:**
```cmd
python -m ensurepip --upgrade
```

---

### "Permission denied" during pip install

**macOS/Linux:**
```bash
pip3 install --user -r requirements.txt
```

**Or use virtual environment (recommended)**

---

### EasyOCR model download fails

1. Check internet connection
2. Manually download models from: https://github.com/JaidedAI/EasyOCR
3. Place in `~/.EasyOCR/model/` directory

---

### Application won't start

1. Verify Python version: `python3 --version` (must be 3.8+)
2. Run verification script: `python3 verify_install.py`
3. Check for error messages in terminal
4. Ensure all dependencies installed: `pip3 list`

---

## Uninstallation

### Remove Application
```bash
# Simply delete the image_editor directory
rm -rf image_editor
```

### Remove Dependencies
```bash
pip3 uninstall Pillow opencv-python easyocr fonttools numpy scipy
```

### Remove EasyOCR Models
```bash
# macOS/Linux
rm -rf ~/.EasyOCR

# Windows
rmdir /s %USERPROFILE%\.EasyOCR
```

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8 | 3.11+ |
| RAM | 2 GB | 4 GB |
| Disk Space | 500 MB | 1 GB |
| Display | 1280x720 | 1400x800+ |
| OS | Win 10, macOS 10.14, Ubuntu 18.04 | Latest versions |

---

## Next Steps

After successful installation:

1. Read the [README.md](README.md) for feature overview
2. Run the application: `python3 main.py`
3. Try the example workflow:
   - Upload an image
   - Adjust brightness/contrast
   - Detect and replace text
   - Export to Desktop

---

## Support

For issues not covered here:
1. Check the [README.md](README.md) Troubleshooting section
2. Verify all dependencies are installed correctly
3. Check Python version compatibility
4. Review error messages carefully
