#!/usr/bin/env python3
"""Check Tesseract installation and provide guidance."""

import sys
import subprocess
import platform

def check_tesseract():
    """Check if Tesseract is installed and accessible."""
    print("Checking Tesseract OCR installation...\n")
    
    # Check if tesseract command exists
    try:
        result = subprocess.run(
            ['tesseract', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✓ Tesseract found: {version}")
            return True
    except FileNotFoundError:
        print("✗ Tesseract command not found in PATH")
    except subprocess.TimeoutExpired:
        print("✗ Tesseract command timed out")
    except Exception as e:
        print(f"✗ Error checking tesseract: {e}")
    
    return False

def check_pytesseract():
    """Check if pytesseract can find Tesseract."""
    print("\nChecking pytesseract integration...\n")
    
    try:
        import pytesseract
        print("✓ pytesseract module installed")
        
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✓ pytesseract can access Tesseract: {version}")
            return True
        except Exception as e:
            print(f"✗ pytesseract cannot access Tesseract: {e}")
            return False
    except ImportError:
        print("✗ pytesseract module not installed")
        print("  Install with: pip3 install pytesseract")
        return False

def provide_installation_guide():
    """Provide OS-specific installation instructions."""
    os_name = platform.system()
    
    print("\n" + "="*60)
    print("INSTALLATION GUIDE")
    print("="*60 + "\n")
    
    if os_name == "Darwin":  # macOS
        print("macOS Installation Options:\n")
        print("Option 1 - Homebrew (most common, may take 5-10 minutes):")
        print("  brew install tesseract")
        print()
        print("Option 2 - Conda (faster if you use Anaconda):")
        print("  conda install -c conda-forge tesseract")
        print()
        print("Option 3 - MacPorts:")
        print("  sudo port install tesseract")
        print()
        print("Option 4 - Direct Download:")
        print("  https://github.com/tesseract-ocr/tesseract/releases")
        print()
        print("After installation, restart your terminal and run:")
        print("  tesseract --version")
        
    elif os_name == "Linux":
        print("Linux Installation:\n")
        print("Ubuntu/Debian:")
        print("  sudo apt update")
        print("  sudo apt install tesseract-ocr")
        print()
        print("Fedora:")
        print("  sudo dnf install tesseract")
        print()
        print("Arch:")
        print("  sudo pacman -S tesseract")
        
    elif os_name == "Windows":
        print("Windows Installation:\n")
        print("1. Download installer from:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print()
        print("2. Run the installer")
        print()
        print("3. Add to PATH:")
        print("   - Default location: C:\\Program Files\\Tesseract-OCR")
        print("   - Add to System Environment Variables")
        print()
        print("4. Restart your terminal/IDE")
    
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60 + "\n")
    print("After installation, verify with:")
    print("  tesseract --version")
    print()
    print("Then run this script again:")
    print("  python3 check_tesseract.py")
    print()

def check_common_locations():
    """Check common Tesseract installation locations."""
    print("\nChecking common installation locations...\n")
    
    import os
    
    common_paths = [
        '/usr/local/bin/tesseract',
        '/usr/bin/tesseract',
        '/opt/homebrew/bin/tesseract',
        '/opt/local/bin/tesseract',
        'C:\\Program Files\\Tesseract-OCR\\tesseract.exe',
        'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe',
    ]
    
    found = []
    for path in common_paths:
        if os.path.exists(path):
            print(f"✓ Found at: {path}")
            found.append(path)
    
    if not found:
        print("✗ Not found in common locations")
    
    return found

def suggest_path_fix(paths):
    """Suggest how to add Tesseract to PATH."""
    if not paths:
        return
    
    print("\n" + "="*60)
    print("PATH FIX")
    print("="*60 + "\n")
    print("Tesseract is installed but not in your PATH.")
    print(f"Found at: {paths[0]}\n")
    
    os_name = platform.system()
    
    if os_name == "Darwin":  # macOS
        shell_config = "~/.zshrc"  # or ~/.bash_profile
        print(f"Add to {shell_config}:")
        print(f'  export PATH="{os.path.dirname(paths[0])}:$PATH"')
        print()
        print("Then reload:")
        print(f"  source {shell_config}")
    
    elif os_name == "Linux":
        print("Add to ~/.bashrc or ~/.zshrc:")
        print(f'  export PATH="{os.path.dirname(paths[0])}:$PATH"')
        print()
        print("Then reload:")
        print("  source ~/.bashrc")
    
    elif os_name == "Windows":
        print("Add to System Environment Variables:")
        print("1. Search for 'Environment Variables' in Start Menu")
        print("2. Edit 'Path' variable")
        print(f"3. Add: {os.path.dirname(paths[0])}")
        print("4. Restart terminal/IDE")

def main():
    """Main check function."""
    print("="*60)
    print("TESSERACT OCR INSTALLATION CHECKER")
    print("="*60 + "\n")
    
    tesseract_found = check_tesseract()
    pytesseract_ok = check_pytesseract()
    
    if tesseract_found and pytesseract_ok:
        print("\n" + "="*60)
        print("✓ SUCCESS - Tesseract is properly installed!")
        print("="*60)
        print("\nYou can now use the text replacement feature.")
        print("Run: python3 main.py")
        return 0
    
    # Check if installed but not in PATH
    if not tesseract_found:
        paths = check_common_locations()
        if paths:
            suggest_path_fix(paths)
        else:
            provide_installation_guide()
    
    print("\n" + "="*60)
    print("✗ Tesseract is not properly configured")
    print("="*60)
    print("\nFollow the instructions above to install Tesseract.")
    print("The text replacement feature requires Tesseract OCR.")
    print("\nAll other features of PyImageEditor work without it:")
    print("  • Image adjustments (brightness, contrast, etc.)")
    print("  • Filters (grayscale, sepia, blur, etc.)")
    print("  • Shapes and drawing")
    print("  • Manual text overlay")
    print("  • Crop, rotate, resize, flip")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
