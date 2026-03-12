"""Test font style classifier with sample text."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from utils.font_classifier import FontStyleClassifier
from utils.font_matcher import find_matching_font
import os


def create_test_image(text, font_path, font_size, style_name):
    """Create a test image with text in specific font."""
    # Create white background
    img = Image.new('RGB', (400, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        print(f"Could not load font: {font_path}")
        return None
    
    # Draw black text
    draw.text((20, 30), text, fill=(0, 0, 0), font=font)
    
    # Save for inspection
    img.save(f"/tmp/test_{style_name}.png")
    print(f"Created test image: /tmp/test_{style_name}.png")
    
    return img


def test_classifier():
    """Test the font classifier on different font styles."""
    
    # Test fonts (macOS paths)
    test_cases = [
        {
            'name': 'Script/Cursive',
            'font': '/System/Library/Fonts/Supplemental/Brush Script.ttf',
            'text': 'Didas Mbarushimana',
            'expected': 'script'
        },
        {
            'name': 'Sans-serif',
            'font': '/System/Library/Fonts/Helvetica.ttc',
            'text': 'Brandon Ogola',
            'expected': 'sans'
        },
        {
            'name': 'Serif',
            'font': '/System/Library/Fonts/Supplemental/Times New Roman.ttf',
            'text': 'Times Roman Text',
            'expected': 'serif'
        }
    ]
    
    print("=" * 60)
    print("FONT STYLE CLASSIFIER TEST")
    print("=" * 60)
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        print(f"  Font: {test['font']}")
        print(f"  Expected: {test['expected']}")
        
        if not os.path.exists(test['font']):
            print(f"  ❌ Font file not found, skipping")
            continue
        
        # Create test image
        img = create_test_image(test['text'], test['font'], 48, test['name'].replace('/', '_'))
        if img is None:
            continue
        
        # Extract text region (crop to text area)
        region = img.crop((10, 20, 390, 80))
        region_array = np.array(region)
        
        # Classify
        classifier = FontStyleClassifier(region_array, 60)
        detected_style = classifier.classify()
        
        # Find matching font
        matched_font = find_matching_font(region_array, 60, False, False)
        matched_name = os.path.basename(matched_font) if matched_font != "default" else "default"
        
        # Results
        match_symbol = "✅" if detected_style == test['expected'] else "❌"
        print(f"  {match_symbol} Detected: {detected_style}")
        print(f"  Matched font: {matched_name}")
    
    print("\n" + "=" * 60)
    print("Test complete! Check /tmp/test_*.png to see generated images")
    print("=" * 60)


if __name__ == "__main__":
    test_classifier()
