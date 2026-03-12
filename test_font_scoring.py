"""Debug font matching to see scoring."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from utils.font_classifier import FontStyleClassifier
import os
import platform


def test_font_scoring():
    """Test font scoring with debug output."""
    
    # Create a simple script-style text image
    img = Image.new('RGB', (400, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    font_path = '/System/Library/Fonts/Supplemental/Brush Script.ttf'
    try:
        font = ImageFont.truetype(font_path, 48)
        draw.text((20, 30), "Cursive Text", fill=(0, 0, 0), font=font)
    except:
        print("Could not load test font")
        return
    
    # Extract region
    region = img.crop((10, 20, 390, 80))
    region_array = np.array(region)
    
    # Classify
    classifier = FontStyleClassifier(region_array, 60)
    style_class = classifier.classify()
    
    print(f"Detected style: {style_class}")
    print("\nScanning fonts and scoring...\n")
    
    # Get font directories
    system = platform.system()
    if system == 'Darwin':
        search_dirs = [
            '/System/Library/Fonts/',
            '/Library/Fonts/',
            os.path.expanduser('~/Library/Fonts/'),
        ]
    else:
        search_dirs = []
    
    # Scan fonts
    all_fonts = []
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if f.lower().endswith(('.ttf', '.otf', '.ttc')):
                    all_fonts.append(os.path.join(root, f))
    
    print(f"Found {len(all_fonts)} total fonts")
    
    # Test loading and score
    valid_fonts = []
    for fp in all_fonts[:100]:  # Test first 100
        try:
            ImageFont.truetype(fp, 20)
            valid_fonts.append(fp)
        except:
            continue
    
    print(f"Valid fonts: {len(valid_fonts)}")
    
    # Score each font
    style_keywords = {
        FontStyleClassifier.SCRIPT: [
            'script', 'cursive', 'italic', 'handwriting',
            'calligraph', 'hand', 'brush', 'write',
        ],
    }
    
    def score_font(fp: str) -> float:
        name = os.path.basename(fp).lower()
        score = 0.0
        
        # Match style class
        for kw in style_keywords.get(style_class, []):
            if kw in name:
                score += 5.0
                break
        
        return score
    
    # Score and sort
    scored = [(fp, score_font(fp)) for fp in valid_fonts]
    scored.sort(key=lambda x: x[1], reverse=True)
    
    # Show top 10
    print("\nTop 10 scored fonts:")
    for fp, score in scored[:10]:
        name = os.path.basename(fp)
        print(f"  {score:5.1f} - {name}")
    
    # Check if Brush Script is in the list
    print("\nLooking for 'Brush Script'...")
    for fp, score in scored:
        if 'brush' in os.path.basename(fp).lower():
            print(f"  Found: {os.path.basename(fp)} with score {score}")


if __name__ == "__main__":
    test_font_scoring()
