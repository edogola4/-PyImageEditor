# Quick Start Guide

Get started with PyImageEditor in 5 minutes!

## Installation (One-Time Setup)

```bash
# 1. Navigate to the project directory
cd image_editor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
python3 verify_install.py
```

## Launch the Application

```bash
python3 main.py
```

## Your First Edit

### 1. Load an Image
- Click **"Upload Image"** button
- Select any image file (JPEG, PNG, WEBP, BMP, TIFF, GIF)
- Image appears in split view: Original (left) | Edited (right)

### 2. Make Basic Adjustments
Use the sliders in the left sidebar:
- **Brightness**: Make image lighter/darker
- **Contrast**: Adjust difference between light and dark
- **Saturation**: Control color intensity
- **Sharpness**: Make edges more/less defined

Changes appear instantly in the preview!

### 3. Apply a Filter
Scroll down to the **Filters** section and click any button:
- **Grayscale**: Convert to black & white
- **Sepia**: Vintage photo effect
- **Blur**: Soften the image
- **Sharpen**: Enhance details
- **Edge Detect**: Outline detection
- **Emboss**: 3D relief effect

### 4. Save Your Work
- Click **"💾 Save As..."** to choose location and format
- Or click **"⬇️ Export to Desktop"** for quick save

## Text Detection & Editing

### Find and Replace Text in Images

1. **Detect Text**
   - Click **"🔍 Detect Text in Image"**
   - Wait for OCR to scan (first run downloads model ~80MB)
   - All detected text appears in the list

2. **Select Text Block**
   - Click any text block in the list
   - Selected text highlights in yellow on the canvas

3. **Replace Text**
   - Type new text in the "Replace with" field
   - Click **"■ Auto-detect"** to match original color
   - Or click **"🎨 Pick Color"** to choose custom color
   - Click **"✏️ Replace Selected"**

4. **Delete Text**
   - Select a text block
   - Click **"🗑️ Delete Selected"**
   - Text is cleanly removed with background inpainting

5. **Batch Operations**
   - **"🔄 Replace All"**: Replace all matching text at once
   - **"🗑️ Delete All"**: Remove all detected text

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo last change |
| `Ctrl+Y` | Redo last undone change |
| `Ctrl+F` | Open text detection |
| `Ctrl+S` | Save image |
| `Ctrl+E` | Export to Desktop |
| `Delete` | Delete selected text block |
| `Escape` | Clear text selection |

## Transform Operations

### Crop
1. Click **"Crop"** in the Transform section
2. Enter coordinates: Left, Top, Right, Bottom
3. Image is cropped to the specified region

### Flip
- **Horizontal**: Mirror left-to-right
- **Vertical**: Mirror top-to-bottom

### Rotate
1. Click **"Rotate"**
2. Enter degrees (positive = clockwise, negative = counter-clockwise)
3. Image rotates around center

### Resize
1. Enter new width and height
2. Check **"Lock Aspect Ratio"** to maintain proportions
3. Click **"Resize"**

## Drawing Tools

### Add Shapes
1. Select shape type: Rectangle, Circle, or Line
2. Click **"Choose Color"**
3. Adjust thickness (1-20 pixels)
4. Click **"Draw Shape"**
5. Enter coordinates when prompted

### Add Text
1. Adjust font size (10-100)
2. Click **"Choose Color"**
3. Click **"Add Text"**
4. Enter text and position

## Tips & Tricks

### Undo/Redo
- Up to 10 steps of history
- Use `Ctrl+Z` to undo mistakes
- Use `Ctrl+Y` to redo if you undo too much

### Non-Destructive Editing
- Adjustment sliders don't modify the base image
- Only filters, transforms, and drawing operations are permanent
- Reset sliders to 100 to see original adjustments

### Text Detection Tips
- Works best on clear, high-contrast text
- First detection is slower (model loading)
- Subsequent detections are faster
- Increase contrast before detection for better results

### Export Formats
- **JPEG**: Best for photos (smaller file size)
- **PNG**: Best for graphics with transparency
- **WEBP**: Modern format (good compression)
- **BMP**: Uncompressed (large files)
- **TIFF**: Professional/archival use

## Common Workflows

### Photo Enhancement
1. Upload photo
2. Adjust brightness and contrast
3. Increase saturation slightly
4. Apply sharpen filter
5. Export to Desktop

### Remove Watermark Text
1. Upload image
2. Press `Ctrl+F` to detect text
3. Select watermark text block
4. Click "🗑️ Delete Selected"
5. Save image

### Create Meme
1. Upload image
2. Adjust brightness/contrast for visibility
3. Add text at top and bottom
4. Choose white text with black outline
5. Export to Desktop

### Batch Text Replacement
1. Upload image with repeated text
2. Detect text with `Ctrl+F`
3. Select one instance of the text
4. Enter replacement text
5. Click "🔄 Replace All"
6. All instances replaced at once

## Troubleshooting

### Text Detection Not Working
- **First run**: Wait for model download (~80MB)
- **No text found**: Try increasing contrast first
- **Low confidence**: Text may be too small or blurry

### Application Slow
- **Large images**: Consider resizing first
- **First text detection**: Model loading takes time
- **Multiple operations**: Use undo instead of reloading

### Can't Save Image
- Check you have write permissions to the destination
- Ensure filename doesn't contain invalid characters
- Try exporting to Desktop instead

## Next Steps

- Read the full [README.md](README.md) for complete feature list
- Check [INSTALL.md](INSTALL.md) for advanced installation options
- Experiment with different filters and adjustments
- Try combining multiple operations for creative effects

## Need Help?

1. Run verification: `python3 verify_install.py`
2. Check the Troubleshooting section in [README.md](README.md)
3. Review error messages in the terminal
4. Ensure all dependencies are installed

---

**Happy Editing! 🎨**
