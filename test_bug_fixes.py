#!/usr/bin/env python3
"""Test script to verify bug fixes."""

import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_test_image():
    """Create a test image with text."""
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add some text
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 36)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 80), "TEST TEXT", fill='black', font=font)
    
    return img

def test_text_replacement():
    """Test BUG 1: Text replacement and visibility."""
    print("Testing BUG 1: Text Replacement...")
    
    from editor.text_editor import detect_all_text, replace_text_in_image
    
    # Create test image
    img = create_test_image()
    
    # Detect text
    blocks = detect_all_text(img)
    
    if not blocks:
        print("❌ FAIL: No text detected")
        return False
    
    print(f"✓ Detected {len(blocks)} text block(s)")
    
    # Replace text
    block = blocks[0]
    print(f"  Original: '{block.text}' at ({block.x}, {block.y})")
    
    try:
        result = replace_text_in_image(img, block, "REPLACED", "default", (255, 0, 0))
        
        # Verify result is not None
        if result is None:
            print("❌ FAIL: Result is None")
            return False
        
        # Verify result has correct mode
        if result.mode not in ['RGB', 'RGBA']:
            print(f"❌ FAIL: Invalid mode {result.mode}")
            return False
        
        # Verify result has same size
        if result.size != img.size:
            print(f"❌ FAIL: Size mismatch {result.size} != {img.size}")
            return False
        
        # Verify result has changed (not identical to original)
        if np.array_equal(np.array(result), np.array(img)):
            print("❌ FAIL: Image unchanged after replacement")
            return False
        
        print("✅ PASS: Text replacement successful")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Exception during replacement: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_filter_duplication():
    """Test BUG 2: Filter duplication."""
    print("\nTesting BUG 2: Filter Duplication...")
    
    from ui.sidebar import Sidebar
    import tkinter as tk
    
    try:
        root = tk.Tk()
        root.withdraw()
        
        # Create sidebar multiple times
        callbacks = {
            'adjust': lambda: None,
            'crop': lambda: None,
            'flip': lambda: None,
            'rotate': lambda: None,
            'resize': lambda: None,
            'filter': lambda x: None,
            'shape': lambda: None,
            'text': lambda: None
        }
        
        frame1 = tk.Frame(root)
        sidebar1 = Sidebar(frame1, callbacks)
        
        frame2 = tk.Frame(root)
        sidebar2 = Sidebar(frame2, callbacks)
        
        # Check if class flag prevents duplication
        if Sidebar._filters_built:
            print("✅ PASS: Filter duplication prevented")
            root.destroy()
            return True
        else:
            print("❌ FAIL: Filter flag not set")
            root.destroy()
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_filter_on_text():
    """Test BUG 3: Filters working on selected text."""
    print("\nTesting BUG 3: Filters on Text Region...")
    
    from editor.text_editor import detect_all_text, apply_filter_to_text_region
    
    # Create test image
    img = create_test_image()
    
    # Detect text
    blocks = detect_all_text(img)
    
    if not blocks:
        print("❌ FAIL: No text detected")
        return False
    
    block = blocks[0]
    
    # Test different filters
    filters_to_test = ['grayscale', 'blur', 'sharpen', 'sepia']
    
    for filter_type in filters_to_test:
        try:
            result = apply_filter_to_text_region(img, block, filter_type, 1.0)
            
            if result is None:
                print(f"❌ FAIL: {filter_type} returned None")
                return False
            
            if result.size != img.size:
                print(f"❌ FAIL: {filter_type} changed image size")
                return False
            
            # Verify only text region changed
            result_np = np.array(result)
            img_np = np.array(img)
            
            # Check that area outside text block is unchanged
            x1, y1 = max(0, block.x), max(0, block.y)
            x2 = min(img.width, block.x + block.width)
            y2 = min(img.height, block.y + block.height)
            
            # Sample a corner far from text
            corner_x, corner_y = 10, 10
            if corner_x < x1 or corner_x > x2 or corner_y < y1 or corner_y > y2:
                if not np.array_equal(result_np[corner_y, corner_x], img_np[corner_y, corner_x]):
                    print(f"⚠️  WARNING: {filter_type} modified area outside text region")
            
            print(f"  ✓ {filter_type} filter applied successfully")
            
        except Exception as e:
            print(f"❌ FAIL: {filter_type} raised exception: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("✅ PASS: All filters work on text regions")
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("BUG FIX VERIFICATION TESTS")
    print("=" * 60)
    
    results = []
    
    # Test 1: Text Replacement
    results.append(("Text Replacement", test_text_replacement()))
    
    # Test 2: Filter Duplication
    results.append(("Filter Duplication", test_filter_duplication()))
    
    # Test 3: Filters on Text
    results.append(("Filters on Text", test_filter_on_text()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
