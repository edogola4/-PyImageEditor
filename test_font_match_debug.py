"""Debug font matching with full output."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from utils.font_classifier import FontStyleClassifier
from utils.font_matcher import find_matching_font
import os


# Create test image with script font
img = Image.new('RGB', (400, 100), color=(255, 255, 255))
draw = ImageDraw.Draw(img)

font_path = '/System/Library/Fonts/Supplemental/Brush Script.ttf'
font = ImageFont.truetype(font_path, 48)
draw.text((20, 30), "Cursive Text", fill=(0, 0, 0), font=font)

# Extract region
region = img.crop((10, 20, 390, 80))
region_array = np.array(region)

# Classify
classifier = FontStyleClassifier(region_array, 60)
style_class = classifier.classify()

print(f"Detected style: {style_class}")
print(f"\nCalling find_matching_font...")

# Call with debug
matched = find_matching_font(region_array, 60, False, False)
print(f"\nMatched font: {matched}")
print(f"Basename: {os.path.basename(matched)}")
