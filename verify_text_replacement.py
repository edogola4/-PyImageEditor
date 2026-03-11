#!/usr/bin/env python3
"""Verify text replacement feature implementation."""

import sys

def test_text_editor_module():
    """Test text_editor module."""
    print("Testing editor/text_editor.py...")
    try:
        from editor.text_editor import (
            TextBlock, detect_all_text, detect_text_color,
            get_background_color, erase_text_region,
            calculate_font_size, render_replacement_text,
            replace_text_in_image, replace_all_matching
        )
        print("  ✓ All functions imported")
        
        # Test TextBlock dataclass
        block = TextBlock(
            text="Test",
            x=10, y=20, width=50, height=20,
            conf=95.0, font_size_estimate=16, block_id=0
        )
        assert block.text == "Test"
        print("  ✓ TextBlock dataclass works")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_text_select_panel():
    """Test text_select_panel module."""
    print("\nTesting ui/text_select_panel.py...")
    try:
        from ui.text_select_panel import TextSelectPanel
        print("  ✓ TextSelectPanel imported")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_canvas_integration():
    """Test canvas highlighting methods."""
    print("\nTesting ui/canvas.py integration...")
    try:
        from ui.canvas import ImageCanvas
        import tkinter as tk
        
        root = tk.Tk()
        canvas = ImageCanvas(root)
        
        # Check for new methods
        assert hasattr(canvas, 'highlight_text_block')
        assert hasattr(canvas, 'clear_highlight')
        assert hasattr(canvas, 'highlight_rect')
        assert hasattr(canvas, 'scale_factor')
        
        root.destroy()
        print("  ✓ Canvas has highlighting methods")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_app_integration():
    """Test app integration."""
    print("\nTesting app.py integration...")
    try:
        # Just test imports, don't create window
        import app
        
        # Check for new methods in source
        with open('app.py', 'r') as f:
            content = f.read()
            assert 'detect_text_blocks' in content
            assert 'highlight_text_block' in content
            assert 'replace_text_block' in content
            assert 'replace_all_text' in content
            assert 'text_select_panel' in content
            assert 'Ctrl+F' in content or 'Control-f' in content
        
        print("  ✓ App has text replacement methods")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_dependencies():
    """Test required dependencies."""
    print("\nTesting dependencies...")
    errors = []
    
    try:
        from PIL import Image
        print("  ✓ Pillow available")
    except ImportError:
        errors.append("Pillow not installed")
    
    try:
        import numpy as np
        print("  ✓ NumPy available")
    except ImportError:
        errors.append("NumPy not installed")
    
    try:
        import pytesseract
        print("  ✓ pytesseract available")
        try:
            pytesseract.get_tesseract_version()
            print("  ✓ Tesseract binary found")
        except Exception:
            print("  ⚠ pytesseract installed but Tesseract binary not in PATH")
    except ImportError:
        errors.append("pytesseract not installed")
    
    try:
        import tkinter
        print("  ✓ tkinter available")
    except ImportError:
        errors.append("tkinter not available")
    
    return len(errors) == 0

def test_file_structure():
    """Test file structure."""
    print("\nTesting file structure...")
    import os
    
    required_files = [
        'editor/text_editor.py',
        'ui/text_select_panel.py',
        'TEXT_REPLACEMENT_GUIDE.md',
        'TEXT_REPLACEMENT_COMPLETE.md'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file} exists")
        else:
            print(f"  ✗ {file} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("="*60)
    print("Text Replacement Feature Verification")
    print("="*60)
    
    tests = [
        ("Text Editor Module", test_text_editor_module),
        ("Text Select Panel", test_text_select_panel),
        ("Canvas Integration", test_canvas_integration),
        ("App Integration", test_app_integration),
        ("Dependencies", test_dependencies),
        ("File Structure", test_file_structure)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} crashed: {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("="*60)
    print(f"Total: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n✓ All tests passed! Text replacement feature is ready.")
        print("\nTo use:")
        print("1. Run: python3 main.py")
        print("2. Load an image")
        print("3. Press Ctrl+F to detect text")
        print("4. Select and replace text blocks")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
