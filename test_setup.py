"""Test script to verify all modules and dependencies."""
import sys

def test_imports():
    """Test all required imports."""
    print("Testing imports...")
    
    tests = [
        ("PIL (Pillow)", lambda: __import__('PIL')),
        ("cv2 (OpenCV)", lambda: __import__('cv2')),
        ("numpy", lambda: __import__('numpy')),
        ("tkinter", lambda: __import__('tkinter')),
        ("pytesseract", lambda: __import__('pytesseract')),
        ("fonttools", lambda: __import__('fontTools')),
    ]
    
    failed = []
    for name, test_func in tests:
        try:
            test_func()
            print(f"  ✓ {name}")
        except ImportError as e:
            print(f"  ✗ {name}: {e}")
            failed.append(name)
    
    print()
    
    if failed:
        print(f"Failed imports: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def test_modules():
    """Test all project modules."""
    print("Testing project modules...")
    
    modules = [
        "editor.history",
        "editor.image_ops",
        "editor.filters",
        "editor.shapes",
        "editor.text_overlay",
        "utils.file_handler",
        "utils.font_matcher",
        "ui.toolbar",
        "ui.sidebar",
        "ui.canvas",
        "ui.metadata_panel",
        "app"
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except Exception as e:
            print(f"  ✗ {module}: {e}")
            failed.append(module)
    
    print()
    
    if failed:
        print(f"Failed modules: {', '.join(failed)}")
        return False
    
    return True


def test_tesseract():
    """Test Tesseract OCR availability."""
    print("Testing Tesseract OCR...")
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"  ✓ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"  ⚠ Tesseract not available: {e}")
        print("  Font detection will use fallback fonts")
        return True  # Not critical


def main():
    """Run all tests."""
    print("=" * 50)
    print("PyImageEditor - Dependency Test")
    print("=" * 50)
    print()
    
    results = [
        test_imports(),
        test_modules(),
        test_tesseract()
    ]
    
    print()
    print("=" * 50)
    
    if all(results[:2]):  # First two are critical
        print("✓ All tests passed! Ready to run.")
        print()
        print("Launch the application with:")
        print("  python main.py")
        print("  or")
        print("  ./start.sh (Unix/Mac)")
        print("  start.bat (Windows)")
        return 0
    else:
        print("✗ Some tests failed. Please fix dependencies.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
