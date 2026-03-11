#!/usr/bin/env python3
"""Test script to verify text replacement matches original properties."""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from editor.text_editor import TextBlock, extract_text_properties
from editor.inpainting import professional_replace_text


def create_test_image_with_text(text="HELLO", color=(255, 0, 0), bg_color=(255, 255, 255), size=(400, 200)):
    """Create a test image with colored text."""
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    except:
        font = ImageFont.load_default()
    
    # Draw text in center
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    draw.text((x, y), text, fill=color, font=font)
    
    return img, x, y, text_width, text_height


def test_color_detection():
    """Test that color detection works correctly."""
    print("=" * 60)
    print("TEST 1: Color Detection")
    print("=" * 60)
    
    test_cases = [
        ("White text on black", (255, 255, 255), (0, 0, 0)),
        ("Black text on white", (0, 0, 0), (255, 255, 255)),
        ("Red text on white", (255, 0, 0), (255, 255, 255)),
        ("Blue text on yellow", (0, 0, 255), (255, 255, 0)),
    ]
    
    for name, text_color, bg_color in test_cases:
        print(f"\n{name}:")
        print(f"  Expected text color: RGB{text_color}")
        
        img, x, y, w, h = create_test_image_with_text("TEST", text_color, bg_color)
        
        # Create TextBlock
        block = TextBlock(
            text="TEST",
            x=x,
            y=y,
            width=w,
            height=h,
            conf=1.0,
            font_size_estimate=60,
            block_id=0
        )
        
        # Extract properties
        props = extract_text_properties(img, block)
        detected_color = props['color']
        
        print(f"  Detected text color: RGB{detected_color}")
        
        # Check if colors are close (within 30 units per channel)
        color_diff = sum(abs(a - b) for a, b in zip(text_color, detected_color))
        if color_diff < 90:  # 30 per channel * 3 channels
            print(f"  ✓ PASS - Color match (diff: {color_diff})")
        else:
            print(f"  ✗ FAIL - Color mismatch (diff: {color_diff})")


def test_replacement_preserves_color():
    """Test that replacement text uses the same color as original."""
    print("\n" + "=" * 60)
    print("TEST 2: Replacement Color Preservation")
    print("=" * 60)
    
    # Create image with red text
    original_color = (200, 50, 50)
    bg_color = (240, 240, 240)
    
    print(f"\nOriginal text color: RGB{original_color}")
    
    img, x, y, w, h = create_test_image_with_text("HELLO", original_color, bg_color)
    
    # Create TextBlock
    block = TextBlock(
        text="HELLO",
        x=x,
        y=y,
        width=w,
        height=h,
        conf=1.0,
        font_size_estimate=60,
        block_id=0
    )
    
    # Replace text WITHOUT specifying color (should auto-detect)
    replaced_img = professional_replace_text(img, block, "WORLD", font_path=None, color=None)
    
    # Sample the replaced text color
    replaced_region = replaced_img.crop((x, y, x + w, y + h))
    np_region = np.array(replaced_region)
    
    # Find non-background pixels
    bg_np = np.array(bg_color)
    pixels = np_region.reshape(-1, 3)
    text_pixels = [p for p in pixels if np.sum(np.abs(p - bg_np)) > 30]
    
    if text_pixels:
        detected_replacement_color = tuple(int(x) for x in np.median(text_pixels, axis=0))
        print(f"Replacement text color: RGB{detected_replacement_color}")
        
        color_diff = sum(abs(a - b) for a, b in zip(original_color, detected_replacement_color))
        if color_diff < 90:
            print(f"✓ PASS - Replacement matches original (diff: {color_diff})")
        else:
            print(f"✗ FAIL - Replacement doesn't match (diff: {color_diff})")
    else:
        print("✗ FAIL - Could not detect replacement text")
    
    # Save test images
    img.save("/tmp/test_original.png")
    replaced_img.save("/tmp/test_replaced.png")
    print("\nTest images saved to /tmp/test_original.png and /tmp/test_replaced.png")


def test_manual_override():
    """Test that manual color override still works."""
    print("\n" + "=" * 60)
    print("TEST 3: Manual Color Override")
    print("=" * 60)
    
    original_color = (255, 0, 0)
    override_color = (0, 255, 0)
    bg_color = (255, 255, 255)
    
    print(f"\nOriginal text color: RGB{original_color}")
    print(f"Override color: RGB{override_color}")
    
    img, x, y, w, h = create_test_image_with_text("TEST", original_color, bg_color)
    
    block = TextBlock(
        text="TEST",
        x=x,
        y=y,
        width=w,
        height=h,
        conf=1.0,
        font_size_estimate=60,
        block_id=0
    )
    
    # Replace with manual color override
    replaced_img = professional_replace_text(img, block, "PASS", font_path=None, color=override_color)
    
    # Sample the replaced text color
    replaced_region = replaced_img.crop((x, y, x + w, y + h))
    np_region = np.array(replaced_region)
    
    bg_np = np.array(bg_color)
    pixels = np_region.reshape(-1, 3)
    text_pixels = [p for p in pixels if np.sum(np.abs(p - bg_np)) > 30]
    
    if text_pixels:
        detected_color = tuple(int(x) for x in np.median(text_pixels, axis=0))
        print(f"Replacement text color: RGB{detected_color}")
        
        color_diff = sum(abs(a - b) for a, b in zip(override_color, detected_color))
        if color_diff < 90:
            print(f"✓ PASS - Manual override works (diff: {color_diff})")
        else:
            print(f"✗ FAIL - Manual override failed (diff: {color_diff})")
    else:
        print("✗ FAIL - Could not detect replacement text")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TEXT REPLACEMENT COLOR MATCHING TEST SUITE")
    print("=" * 60)
    
    try:
        test_color_detection()
        test_replacement_preserves_color()
        test_manual_override()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED WITH ERROR:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
