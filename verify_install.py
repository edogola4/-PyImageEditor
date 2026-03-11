#!/usr/bin/env python3
"""Verify installation of PyImageEditor dependencies."""
import sys

def check_module(module_name, import_name=None):
    """Check if a module is installed."""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        print(f"✓ {module_name} installed")
        return True
    except ImportError:
        print(f"✗ {module_name} NOT installed")
        return False

def main():
    """Run installation verification."""
    print("PyImageEditor Installation Verification")
    print("=" * 50)
    
    all_ok = True
    
    # Check Python version
    print(f"\nPython version: {sys.version}")
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ required")
        all_ok = False
    else:
        print("✓ Python version OK")
    
    print("\nChecking dependencies:")
    print("-" * 50)
    
    # Core dependencies
    all_ok &= check_module("Pillow", "PIL")
    all_ok &= check_module("opencv-python", "cv2")
    all_ok &= check_module("easyocr")
    all_ok &= check_module("fonttools")
    all_ok &= check_module("numpy")
    all_ok &= check_module("scipy")
    
    # Tkinter (usually built-in)
    try:
        import tkinter
        print("✓ tkinter installed")
    except ImportError:
        print("✗ tkinter NOT installed")
        print("  Install with: sudo apt-get install python3-tk (Linux)")
        all_ok = False
    
    print("\n" + "=" * 50)
    
    if all_ok:
        print("✓ All dependencies installed successfully!")
        print("\nYou can now run the application:")
        print("  python3 main.py")
        return 0
    else:
        print("✗ Some dependencies are missing")
        print("\nInstall missing dependencies with:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
