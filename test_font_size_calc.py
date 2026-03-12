"""Test font size calculation accuracy."""
from PIL import Image, ImageDraw, ImageFont
from editor.text_editor import calculate_font_size
from dataclasses import dataclass


@dataclass
class MockBlock:
    text: str
    x: int
    y: int
    width: int
    height: int
    conf: float = 0.9
    font_size_estimate: int = 0
    block_id: int = 0


# Test with different fonts and sizes
test_cases = [
    {
        'font': '/System/Library/Fonts/Supplemental/Brush Script.ttf',
        'text': 'Test Text',
        'target_height': 48
    },
    {
        'font': '/System/Library/Fonts/Helvetica.ttc',
        'text': 'Hello World',
        'target_height': 32
    },
    {
        'font': '/System/Library/Fonts/Supplemental/Times New Roman.ttf',
        'text': 'Sample',
        'target_height': 64
    }
]

print("Testing font size calculation accuracy:\n")

for test in test_cases:
    font_path = test['font']
    text = test['text']
    target_height = test['target_height']
    
    # Create mock block
    block = MockBlock(
        text=text,
        x=0,
        y=0,
        width=200,
        height=target_height
    )
    
    # Calculate font size
    calculated_size = calculate_font_size(block, None, font_path, text)
    
    # Verify by rendering
    try:
        font = ImageFont.truetype(font_path, calculated_size)
        temp_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(temp_img)
        bbox = draw.textbbox((0, 0), text, font=font)
        actual_height = bbox[3] - bbox[1]
        
        error = abs(actual_height - target_height)
        error_pct = (error / target_height) * 100
        
        status = "✅" if error_pct < 10 else "⚠️" if error_pct < 20 else "❌"
        
        print(f"{status} {font_path.split('/')[-1]}")
        print(f"   Text: '{text}'")
        print(f"   Target height: {target_height}px")
        print(f"   Calculated size: {calculated_size}pt")
        print(f"   Actual height: {actual_height}px")
        print(f"   Error: {error}px ({error_pct:.1f}%)")
        print()
        
    except Exception as e:
        print(f"❌ {font_path.split('/')[-1]}")
        print(f"   Error: {e}")
        print()

print("Test complete!")
