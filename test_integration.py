#!/usr/bin/env python3
"""Integration test for PyImageEditor - Tests all core functionality."""

import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
        import numpy as np
        from editor import image_ops, filters, shapes
        from editor.text_overlay import add_text, detect_and_match_font
        from editor.history import HistoryManager
        from utils.file_handler import open_image, save_image, format_file_size
        from utils.font_matcher import get_system_fonts, match_font
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_image_operations():
    """Test image manipulation operations."""
    print("\nTesting image operations...")
    try:
        from PIL import Image
        from editor import image_ops
        
        # Create test image
        img = Image.new('RGB', (100, 100), color='red')
        
        # Test brightness
        result = image_ops.brightness(img, 1.5)
        assert result.size == (100, 100), "Brightness failed"
        
        # Test contrast
        result = image_ops.contrast(img, 1.2)
        assert result.size == (100, 100), "Contrast failed"
        
        # Test saturation
        result = image_ops.saturation(img, 0.8)
        assert result.size == (100, 100), "Saturation failed"
        
        # Test sharpness
        result = image_ops.sharpness(img, 1.5)
        assert result.size == (100, 100), "Sharpness failed"
        
        # Test flip
        result = image_ops.flip_horizontal(img)
        assert result.size == (100, 100), "Flip horizontal failed"
        
        result = image_ops.flip_vertical(img)
        assert result.size == (100, 100), "Flip vertical failed"
        
        # Test rotate
        result = image_ops.rotate(img, 45)
        assert result.size[0] > 0 and result.size[1] > 0, "Rotate failed"
        
        # Test resize
        result = image_ops.resize(img, 50, 50, lock_aspect=False)
        assert result.size == (50, 50), "Resize failed"
        
        # Test crop
        result = image_ops.crop(img, 10, 10, 90, 90)
        assert result.size == (80, 80), "Crop failed"
        
        print("✓ All image operations working")
        return True
    except Exception as e:
        print(f"✗ Image operations failed: {e}")
        return False

def test_filters():
    """Test filter operations."""
    print("\nTesting filters...")
    try:
        from PIL import Image
        from editor import filters
        
        img = Image.new('RGB', (100, 100), color='blue')
        
        # Test grayscale
        result = filters.to_grayscale(img)
        assert result.mode == 'RGB', "Grayscale failed"
        
        # Test sepia
        result = filters.to_sepia(img)
        assert result.size == (100, 100), "Sepia failed"
        
        # Test blur
        result = filters.apply_blur(img)
        assert result.size == (100, 100), "Blur failed"
        
        # Test sharpen
        result = filters.apply_sharpen(img)
        assert result.size == (100, 100), "Sharpen failed"
        
        # Test edge detection
        result = filters.edge_detection(img)
        assert result.size == (100, 100), "Edge detection failed"
        
        # Test emboss
        result = filters.emboss(img)
        assert result.size == (100, 100), "Emboss failed"
        
        print("✓ All filters working")
        return True
    except Exception as e:
        print(f"✗ Filters failed: {e}")
        return False

def test_shapes():
    """Test shape drawing."""
    print("\nTesting shapes...")
    try:
        from PIL import Image
        from editor import shapes
        
        img = Image.new('RGB', (200, 200), color='white')
        
        # Test rectangle
        result = shapes.draw_rectangle(img, 10, 10, 50, 50, (255, 0, 0), 2)
        assert result.size == (200, 200), "Rectangle failed"
        
        # Test circle
        result = shapes.draw_circle(img, 100, 100, 30, (0, 255, 0), 2)
        assert result.size == (200, 200), "Circle failed"
        
        # Test line
        result = shapes.draw_line(img, 0, 0, 200, 200, (0, 0, 255), 2)
        assert result.size == (200, 200), "Line failed"
        
        print("✓ All shapes working")
        return True
    except Exception as e:
        print(f"✗ Shapes failed: {e}")
        return False

def test_text_overlay():
    """Test text overlay."""
    print("\nTesting text overlay...")
    try:
        from PIL import Image
        from editor.text_overlay import add_text
        
        img = Image.new('RGB', (200, 200), color='white')
        result = add_text(img, "Test", 50, 50, None, 20, (0, 0, 0))
        assert result.size == (200, 200), "Text overlay failed"
        
        print("✓ Text overlay working")
        return True
    except Exception as e:
        print(f"✗ Text overlay failed: {e}")
        return False

def test_history():
    """Test history manager."""
    print("\nTesting history manager...")
    try:
        from PIL import Image
        from editor.history import HistoryManager
        
        history = HistoryManager()
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='blue')
        
        history.initialize(img1)
        assert history.can_undo() == False, "Initial undo check failed"
        
        history.push(img2)
        assert history.can_undo() == True, "Undo availability failed"
        
        result = history.undo()
        assert result is not None, "Undo failed"
        assert history.can_redo() == True, "Redo availability failed"
        
        result = history.redo()
        assert result is not None, "Redo failed"
        
        print("✓ History manager working")
        return True
    except Exception as e:
        print(f"✗ History manager failed: {e}")
        return False

def test_file_handler():
    """Test file handling."""
    print("\nTesting file handler...")
    try:
        from PIL import Image
        from utils.file_handler import save_image, format_file_size
        import tempfile
        
        img = Image.new('RGB', (100, 100), color='green')
        
        # Test save
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        save_image(img, temp_path, (72, 72))
        assert os.path.exists(temp_path), "Save failed"
        os.remove(temp_path)
        
        # Test format_file_size
        assert format_file_size(1024) == "1.0 KB", "File size format failed"
        assert format_file_size(1024*1024) == "1.0 MB", "File size format failed"
        
        print("✓ File handler working")
        return True
    except Exception as e:
        print(f"✗ File handler failed: {e}")
        return False

def test_font_matcher():
    """Test font matcher."""
    print("\nTesting font matcher...")
    try:
        from utils.font_matcher import get_system_fonts, match_font
        
        fonts = get_system_fonts()
        print(f"  Found {len(fonts)} system fonts")
        
        matched = match_font()
        assert matched is not None, "Font matching failed"
        
        print("✓ Font matcher working")
        return True
    except Exception as e:
        print(f"✗ Font matcher failed: {e}")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("PyImageEditor Integration Test")
    print("="*60)
    
    tests = [
        test_imports,
        test_image_operations,
        test_filters,
        test_shapes,
        test_text_overlay,
        test_history,
        test_file_handler,
        test_font_matcher
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("="*60)
    
    if all(results):
        print("\n✓ All tests passed! Application is ready to use.")
        print("\nRun the application with: python3 main.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
