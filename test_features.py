#!/usr/bin/env python3
"""Test script for text detection and manipulation features."""
import sys
from PIL import Image, ImageDraw, ImageFont

def create_test_image():
    """Create a simple test image with text."""
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Hello World", fill='black', font=font)
    draw.text((50, 120), "Test Image", fill='blue', font=font)
    
    return img

def test_text_detection():
    """Test text detection functionality."""
    print("Testing text detection...")
    
    try:
        from editor.text_editor import detect_all_text
        
        img = create_test_image()
        blocks = detect_all_text(img)
        
        print(f"✓ Detected {len(blocks)} text blocks")
        for block in blocks:
            print(f"  - '{block.text}' at ({block.x}, {block.y}) "
                  f"size: {block.width}x{block.height} "
                  f"conf: {block.conf:.2f}")
        
        return len(blocks) > 0
    except Exception as e:
        print(f"✗ Text detection failed: {e}")
        return False

def test_text_replacement():
    """Test photorealistic text replacement functionality."""
    print("\nTesting photorealistic text replacement...")
    
    try:
        from editor.text_editor import detect_all_text
        from editor.inpainting import professional_replace_text
        from utils.font_matcher import match_font
        
        img = create_test_image()
        blocks = detect_all_text(img)
        
        if not blocks:
            print("✗ No text blocks to replace")
            return False
        
        font_path = match_font()
        new_img = professional_replace_text(img, blocks[0], "REPLACED", font_path, (255, 0, 0))
        
        print(f"✓ Photorealistic text replacement successful")
        return True
    except Exception as e:
        print(f"✗ Text replacement failed: {e}")
        return False

def test_text_deletion():
    """Test photorealistic text deletion functionality."""
    print("\nTesting photorealistic text deletion...")
    
    try:
        from editor.text_editor import detect_all_text
        from editor.inpainting import professional_delete_text
        
        img = create_test_image()
        blocks = detect_all_text(img)
        
        if not blocks:
            print("✗ No text blocks to delete")
            return False
        
        new_img = professional_delete_text(img, blocks[0])
        
        print(f"✓ Photorealistic text deletion successful")
        return True
    except Exception as e:
        print(f"✗ Text deletion failed: {e}")
        return False

def main():
    """Run all tests."""
    print("PyImageEditor Text Feature Tests")
    print("=" * 50)
    
    results = []
    
    # Test 1: Text Detection
    results.append(("Text Detection", test_text_detection()))
    
    # Test 2: Text Replacement
    results.append(("Text Replacement", test_text_replacement()))
    
    # Test 3: Text Deletion
    results.append(("Text Deletion", test_text_deletion()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("-" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("-" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        print("\nNote: First run may take longer due to OCR model download.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
