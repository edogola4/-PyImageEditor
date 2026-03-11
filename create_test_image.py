#!/usr/bin/env python3
"""Generate a test image for PyImageEditor."""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Create a colorful test image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background
    for y in range(height):
        r = int(255 * (y / height))
        g = int(150 * (1 - y / height))
        b = int(200 * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Draw some shapes
    draw.rectangle([50, 50, 250, 200], outline='white', width=5)
    draw.ellipse([300, 50, 500, 200], outline='yellow', width=5)
    draw.line([550, 50, 750, 200], fill='white', width=5)
    
    # Add text
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    except:
        font = ImageFont.load_default()
    
    draw.text((width//2 - 200, height//2 - 50), "PyImageEditor", fill='white', font=font)
    draw.text((width//2 - 150, height//2 + 50), "Test Image", fill='white', font=font)
    
    # Save the image
    output_path = os.path.join(os.path.dirname(__file__), 'test_image.png')
    img.save(output_path, 'PNG')
    
    print(f"✓ Test image created: {output_path}")
    print("\nYou can now:")
    print("1. Run the application: python3 main.py")
    print("2. Click 'Upload Image' and select test_image.png")
    print("3. Try all the editing features!")
    
except ImportError as e:
    print(f"Error: {e}")
    print("\nPlease install dependencies first:")
    print("pip install -r requirements.txt")
except Exception as e:
    print(f"Error creating test image: {e}")
