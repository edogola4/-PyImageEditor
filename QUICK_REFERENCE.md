# PyImageEditor - Quick Reference

## Installation (One-Time Setup)

```bash
pip install -r requirements.txt
brew install tesseract  # macOS
# OR: sudo apt install tesseract-ocr  # Linux
```

## Launch Application

```bash
python3 main.py
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo   |
| `Ctrl+Y` | Redo   |

## Workflow

1. **Upload** → Click "Upload Image"
2. **Edit** → Use sidebar controls
3. **Preview** → See changes in real-time
4. **Save** → Click "Save As"

## Adjustments (Real-Time Sliders)

- **Brightness**: 0-200% (default: 100%)
- **Contrast**: 0-200% (default: 100%)
- **Saturation**: 0-200% (default: 100%)
- **Sharpness**: 0-200% (default: 100%)

*Move sliders to see instant preview. Reset to 100 to restore.*

## Transform Operations

| Operation | How To |
|-----------|--------|
| **Crop** | Click "Crop" → Enter coordinates (left, top, right, bottom) |
| **Flip Horizontal** | Click "Flip Horizontal" button |
| **Flip Vertical** | Click "Flip Vertical" button |
| **Rotate** | Enter degrees → Click "Apply" |
| **Resize** | Enter W/H → Check/uncheck "Lock Aspect" → Click "Resize" |

## Filters (One-Click Apply)

- Grayscale
- Sepia
- Blur
- Sharpen
- Edge Detect
- Emboss

*Click any filter button to apply immediately.*

## Drawing Shapes

1. Select shape type (Rectangle/Circle/Line)
2. Click "Choose Color"
3. Adjust thickness (1-20px)
4. Click "Draw Shape"
5. Enter coordinates when prompted

## Adding Text

1. Adjust font size (10-100)
2. Click "Choose Color"
3. Click "Add Text"
4. Enter text
5. Enter X, Y position

## Supported Formats

**Input**: JPEG, PNG, WEBP, BMP, TIFF, GIF
**Output**: JPEG, PNG, WEBP, BMP, TIFF

## Tips

- **Undo/Redo**: Up to 10 steps
- **Non-Destructive**: Adjustments don't modify original until you apply a filter/transform
- **Quality**: JPEG saved at 95% quality, PNG lossless
- **DPI**: Original DPI metadata preserved
- **Large Images**: May take longer to process

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Tesseract not found" | Install Tesseract OCR (see Installation) |
| "No module named..." | Run: `pip install -r requirements.txt` |
| Image won't load | Check format is supported, file not corrupted |
| Slow performance | Try smaller image or close other applications |

## Quick Test

```bash
# Generate test image
python3 create_test_image.py

# Verify installation
python3 verify_install.py
```

## File Locations

- **Config**: `~/.aws/amazonq/prompts/` (if using saved prompts)
- **Test Image**: `image_editor/test_image.png`
- **Logs**: Terminal output

## Common Coordinate Examples

### Crop
- **Center crop**: Calculate (width-new_width)/2, (height-new_height)/2
- **Top-left quarter**: 0, 0, width/2, height/2

### Shapes
- **Rectangle**: x1=100, y1=100, x2=300, y2=200
- **Circle**: cx=400, cy=300, radius=50
- **Line**: x1=0, y1=0, x2=800, y2=600 (diagonal)

### Text
- **Top-left**: x=50, y=50
- **Center**: x=width/2, y=height/2
- **Bottom-right**: x=width-200, y=height-50

## Performance Tips

1. **Large Images**: Resize before applying multiple filters
2. **Multiple Edits**: Use adjustments (non-destructive) before filters
3. **Undo/Redo**: Limited to 10 steps to save memory
4. **Save Often**: Export intermediate versions for complex edits

## Need Help?

1. Check `INSTALL.md` for detailed setup
2. Run `python3 verify_install.py` to check dependencies
3. Check `README.md` for full documentation
4. Review `COMPLETION_SUMMARY.md` for feature list

---

**Version**: 1.0  
**Python**: 3.8+  
**License**: Educational/Personal Use
