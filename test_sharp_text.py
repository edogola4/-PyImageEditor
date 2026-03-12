#!/usr/bin/env python3
"""Test that replaced text is sharp and filters work correctly."""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from editor.text_editor import detect_all_text, replace_text_in_image, apply_filter_to_text_region

def create_test_image():
    """Create test image with sharp text."""
    img = Image.new('RGB', (600, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 48)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 75), "HELLO WORLD", fill='black', font=font)
    return img

def measure_sharpness(image, block):
    """Measure text sharpness using edge detection."""
    x1 = max(0, block.x)
    y1 = max(0, block.y)
    x2 = min(image.width, block.x + block.width)
    y2 = min(image.height, block.y + block.height)
    
    region = image.crop((x1, y1, x2, y2))
    gray = np.array(region.convert('L'))
    
    # Calculate gradient magnitude (edge strength)
    gy, gx = np.gradient(gray.astype(float))
    edge_strength = np.sqrt(gx**2 + gy**2)
    
    # Sharp text has high edge strength
    return np.mean(edge_strength)

def test_text_sharpness():
    """Test that replaced text is sharp, not blurry."""
    print("=" * 60)
    print("TEST: Text Sharpness After Replacement")
    print("=" * 60)
    
    # Create original image
    original = create_test_image()
    
    # Detect text
    blocks = detect_all_text(original)
    if not blocks:
        print("❌ FAIL: No text detected")
        return False
    
    block = blocks[0]
    print(f"✓ Detected text: '{block.text}'")
    
    # Measure original sharpness
    original_sharpness = measure_sharpness(original, block)
    print(f"  Original sharpness: {original_sharpness:.2f}")
    
    # Replace text
    replaced = replace_text_in_image(original, block, "REPLACED", "default", (0, 0, 0))
    
    # Measure replaced sharpness
    replaced_sharpness = measure_sharpness(replaced, block)
    print(f"  Replaced sharpness: {replaced_sharpness:.2f}")
    
    # Calculate sharpness ratio
    ratio = replaced_sharpness / original_sharpness
    print(f"  Sharpness ratio: {ratio:.2%}")
    
    # Text should maintain at least 70% of original sharpness
    if ratio >= 0.70:
        print(f"✅ PASS: Text is sharp (ratio: {ratio:.2%})")
        return True
    else:
        print(f"❌ FAIL: Text is blurry (ratio: {ratio:.2%}, expected >= 70%)")
        return False

def test_filter_effectiveness():
    """Test that filters actually modify the text region."""
    print("\n" + "=" * 60)
    print("TEST: Filter Effectiveness on Text")
    print("=" * 60)
    
    # Create original image
    original = create_test_image()
    
    # Detect text
    blocks = detect_all_text(original)
    if not blocks:
        print("❌ FAIL: No text detected")
        return False
    
    block = blocks[0]
    
    # Test different filters
    filters = [
        ('grayscale', 1.0),
        ('blur', 2.0),
        ('sharpen', 1.5),
        ('invert', 1.0)
    ]
    
    all_passed = True
    
    for filter_name, intensity in filters:
        try:
            # Apply filter
            filtered = apply_filter_to_text_region(original, block, filter_name, intensity)
            
            # Extract text regions
            x1, y1 = max(0, block.x), max(0, block.y)
            x2 = min(original.width, block.x + block.width)
            y2 = min(original.height, block.y + block.height)
            
            orig_region = np.array(original.crop((x1, y1, x2, y2)))
            filt_region = np.array(filtered.crop((x1, y1, x2, y2)))
            
            # Calculate difference
            diff = np.abs(orig_region.astype(float) - filt_region.astype(float))
            avg_diff = np.mean(diff)
            
            # Filter should cause noticeable change (avg diff > 5)
            if avg_diff > 5.0:
                print(f"  ✅ {filter_name:12s}: Effective (diff: {avg_diff:.2f})")
            else:
                print(f"  ❌ {filter_name:12s}: No effect (diff: {avg_diff:.2f})")
                all_passed = False
                
        except Exception as e:
            print(f"  ❌ {filter_name:12s}: Error - {e}")
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: All filters work correctly")
    else:
        print("\n❌ FAIL: Some filters don't work")
    
    return all_passed

def test_color_accuracy():
    """Test that replaced text matches original color."""
    print("\n" + "=" * 60)
    print("TEST: Color Accuracy")
    print("=" * 60)
    
    # Create image with colored text
    img = Image.new('RGB', (600, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 48)
    except:
        font = ImageFont.load_default()
    
    # Draw red text
    draw.text((50, 75), "RED TEXT", fill=(255, 0, 0), font=font)
    
    # Detect and replace
    blocks = detect_all_text(img)
    if not blocks:
        print("❌ FAIL: No text detected")
        return False
    
    block = blocks[0]
    
    # Replace with auto-detected color
    replaced = replace_text_in_image(img, block, "REPLACED", "default", (0, 0, 0))
    
    # Sample color from replaced text center
    cx = block.x + block.width // 2
    cy = block.y + block.height // 2
    
    replaced_color = replaced.getpixel((cx, cy))
    print(f"  Original color: (255, 0, 0)")
    print(f"  Replaced color: {replaced_color}")
    
    # Check if red channel is dominant
    r, g, b = replaced_color
    if r > 200 and g < 100 and b < 100:
        print("✅ PASS: Color matches original (red)")
        return True
    else:
        print("❌ FAIL: Color doesn't match")
        return False

def test_font_size_accuracy():
    """Test that replaced text matches original size."""
    print("\n" + "=" * 60)
    print("TEST: Font Size Accuracy")
    print("=" * 60)
    
    original = create_test_image()
    blocks = detect_all_text(original)
    
    if not blocks:
        print("❌ FAIL: No text detected")
        return False
    
    block = blocks[0]
    original_height = block.height
    
    print(f"  Original text height: {original_height}px")
    
    # Replace text
    replaced = replace_text_in_image(original, block, "REPLACED", "default", (0, 0, 0))
    
    # Detect replaced text
    replaced_blocks = detect_all_text(replaced)
    
    if not replaced_blocks:
        print("❌ FAIL: Replaced text not detected")
        return False
    
    replaced_block = replaced_blocks[0]
    replaced_height = replaced_block.height
    
    print(f"  Replaced text height: {replaced_height}px")
    
    # Height should be within 20% of original
    ratio = replaced_height / original_height
    print(f"  Size ratio: {ratio:.2%}")
    
    if 0.80 <= ratio <= 1.20:
        print("✅ PASS: Font size matches original")
        return True
    else:
        print("❌ FAIL: Font size doesn't match")
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SHARP TEXT & FILTER VERIFICATION")
    print("=" * 60 + "\n")
    
    results = []
    
    results.append(("Text Sharpness", test_text_sharpness()))
    results.append(("Filter Effectiveness", test_filter_effectiveness()))
    results.append(("Color Accuracy", test_color_accuracy()))
    results.append(("Font Size Accuracy", test_font_size_accuracy()))
    
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
        print("\n🎉 All tests passed! Text is sharp and filters work!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
