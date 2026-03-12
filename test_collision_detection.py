"""Test collision detection in text erasure."""
from PIL import Image, ImageDraw, ImageFont
from editor.text_editor import TextBlock, erase_text_region
import numpy as np


# Create test image with two lines of text
img = Image.new('RGB', (400, 200), color=(255, 255, 255))
draw = ImageDraw.Draw(img)

# Draw two lines of text close together
font = ImageFont.load_default()
draw.text((20, 50), "First line of text", fill=(0, 0, 0), font=font)
draw.text((20, 80), "Second line of text", fill=(0, 0, 0), font=font)

img.save('/tmp/test_collision_before.png')
print("Created test image: /tmp/test_collision_before.png")

# Create mock text blocks for the two lines
block1 = TextBlock(
    text="First line of text",
    x=20,
    y=50,
    width=150,
    height=20,
    conf=0.9,
    font_size_estimate=12,
    block_id=0
)

block2 = TextBlock(
    text="Second line of text",
    x=20,
    y=80,
    width=160,
    height=20,
    conf=0.9,
    font_size_estimate=12,
    block_id=1
)

all_blocks = [block1, block2]

print("\nTest 1: Erase first line WITHOUT collision detection")
print("  (using padding=6, no all_blocks)")
img_no_collision = erase_text_region(img, block1, padding=6, all_blocks=None)
img_no_collision.save('/tmp/test_collision_no_detection.png')
print("  Saved: /tmp/test_collision_no_detection.png")

# Check if second line was damaged
region2_no_collision = np.array(img_no_collision.crop((20, 80, 180, 100)))
damaged = np.mean(region2_no_collision) > 250  # If mostly white, it was erased
print(f"  Second line damaged: {damaged}")

print("\nTest 2: Erase first line WITH collision detection")
print("  (using padding=2, with all_blocks)")
img_with_collision = erase_text_region(img, block1, padding=2, all_blocks=all_blocks)
img_with_collision.save('/tmp/test_collision_with_detection.png')
print("  Saved: /tmp/test_collision_with_detection.png")

# Check if second line is preserved
region2_with_collision = np.array(img_with_collision.crop((20, 80, 180, 100)))
preserved = np.mean(region2_with_collision) < 250  # If not white, it's preserved
print(f"  Second line preserved: {preserved}")

print("\n" + "="*60)
if damaged and preserved:
    print("✅ Collision detection WORKS!")
    print("   - Without detection: nearby text was damaged")
    print("   - With detection: nearby text was preserved")
else:
    print("⚠️  Results unclear - check images manually")
    print(f"   - Without detection damaged: {damaged}")
    print(f"   - With detection preserved: {preserved}")
print("="*60)

print("\nCheck the images:")
print("  /tmp/test_collision_before.png - Original")
print("  /tmp/test_collision_no_detection.png - Without collision detection")
print("  /tmp/test_collision_with_detection.png - With collision detection")
