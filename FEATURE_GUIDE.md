# PyImageEditor - Complete Feature Guide

## 🎯 What's New: Interactive Text Selection, Replacement & Deletion

### Key Highlights
- ✅ **No External Dependencies**: Uses EasyOCR (pure Python, no Tesseract binary)
- ✅ **Visual Selection**: Click text blocks to highlight them on canvas
- ✅ **Smart Deletion**: Intelligent background inpainting removes text cleanly
- ✅ **Batch Operations**: Replace or delete all matching text at once
- ✅ **Auto Color Detection**: Automatically matches original text color
- ✅ **Real-time Preview**: See changes instantly before saving

---

## 📦 Installation (2 Minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify installation
python3 verify_install.py

# 3. Launch application
python3 main.py
```

**First Run Note**: EasyOCR downloads language models (~80MB) on first text detection. This is a one-time download.

---

## 🔤 Text Editing Features

### 1. Detect Text in Image
**Button**: 🔍 Detect Text in Image  
**Shortcut**: `Ctrl+F`

**What it does**:
- Scans image using EasyOCR deep learning model
- Detects text with 40%+ confidence
- Shows all detected blocks in a list with confidence scores
- Estimates font size from bounding box height

**Example Output**:
```
#  │ Detected Text    │ Confidence
1  │ "Hello World"    │ 94%
2  │ "Sale 50% OFF"   │ 87%
3  │ "Buy Now"        │ 91%
```

---

### 2. Select Text Block
**Action**: Click any text in the list

**What happens**:
- Selected text highlights in yellow on canvas
- Shows "Selected: [text]" label
- Auto-detects text color from the region
- Enables replacement/deletion buttons

---

### 3. Replace Text
**Button**: ✏️ Replace Selected  
**Shortcut**: `Enter` (when replacement field focused)

**Steps**:
1. Select a text block from list
2. Type new text in "Replace with" field
3. Choose color:
   - **■ Auto-detect**: Uses detected color from original
   - **🎨 Pick Color**: Choose custom RGB color
4. Click "✏️ Replace Selected"

**Smart Features**:
- Font size auto-adjusts to fit original bounds
- Minimum font size: 8pt (warns if reached)
- Background intelligently inpainted before replacement
- Undo/Redo supported

---

### 4. Delete Text
**Button**: 🗑️ Delete Selected  
**Shortcut**: `Delete` key

**Steps**:
1. Select a text block from list
2. Click "🗑️ Delete Selected"
3. Confirm deletion in dialog
4. Text removed with smart background fill

**How it works**:
- Samples background color from 4 edges (top, bottom, left, right)
- Fills text region with most common edge color
- Applies subtle Gaussian blur for smooth blending
- Result: Clean removal without obvious artifacts

---

### 5. Replace All Matching
**Button**: 🔄 Replace All

**Steps**:
1. Select one instance of the text to replace
2. Enter replacement text
3. Click "🔄 Replace All"
4. Confirms count and replaces all matches (case-insensitive)

**Example**:
- Original: "SALE" appears 5 times
- Select any "SALE" block
- Replace with: "SOLD"
- Result: All 5 instances become "SOLD"

---

### 6. Delete All Text
**Button**: 🗑️ Delete All

**Steps**:
1. Detect text in image
2. Click "🗑️ Delete All"
3. Confirm deletion of all blocks
4. All text removed in single operation

**Use Cases**:
- Remove watermarks
- Clean up memes
- Prepare images for re-captioning
- Remove all text overlays

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Detect text in image |
| `Ctrl+Z` | Undo last change |
| `Ctrl+Y` | Redo last undone change |
| `Ctrl+S` | Save image (with dialog) |
| `Ctrl+E` | Export to Desktop (quick save) |
| `Enter` | Replace selected text |
| `Delete` | Delete selected text block |
| `Escape` | Clear text selection |

---

## 💾 Save & Export Options

### Save As (Ctrl+S)
**Button**: 💾 Save As...

**Features**:
- Choose save location
- Select format: PNG, JPEG, WEBP, BMP, TIFF
- Auto-suggests: `edited_{original_filename}`
- Preserves original DPI metadata
- Quality settings:
  - JPEG: 95% quality, optimized
  - PNG: Lossless with compression

---

### Export to Desktop (Ctrl+E)
**Button**: ⬇️ Export to Desktop

**Features**:
- One-click save to Desktop
- Auto-generated filename: `{name}_edited_{timestamp}.{ext}`
- Uses original format
- Preserves DPI and quality
- Shows success notification with filename

**Example**:
- Original: `photo.jpg`
- Exported: `photo_edited_20240115_143022.jpg`

---

## 🎨 Complete Feature Set

### Image Adjustments (Real-time)
- **Brightness**: 0-200% (default 100%)
- **Contrast**: 0-200% (default 100%)
- **Saturation**: 0-200% (default 100%)
- **Sharpness**: 0-200% (default 100%)

### Filters (One-click)
- Grayscale
- Sepia tone
- Gaussian blur
- Sharpen
- Edge detection (Canny)
- Emboss

### Transform Operations
- **Crop**: Coordinate-based selection
- **Flip**: Horizontal/Vertical
- **Rotate**: Custom degrees
- **Resize**: With aspect ratio lock

### Drawing Tools
- **Shapes**: Rectangle, Circle, Line
- **Customization**: Color picker, thickness (1-20px)
- **Text Overlay**: Custom font size (10-100), color, position

### History Management
- **Undo/Redo**: 10-step history
- **Shortcuts**: Ctrl+Z / Ctrl+Y
- **Smart Reset**: Adjustments reset on transform

---

## 🔧 Technical Details

### OCR Engine
- **Library**: EasyOCR 1.7.0+
- **Model**: CRAFT (detection) + CRNN (recognition)
- **Accuracy**: 40%+ confidence threshold
- **Speed**: ~2-5 seconds per image (after model load)
- **GPU**: Auto-detected, falls back to CPU
- **Languages**: English (expandable to 80+)

### Text Manipulation Algorithms

**Erasure Algorithm**:
1. Expand bounding box by 6px padding
2. Sample background from edge strips
3. Fill with most common edge color
4. Apply Gaussian blur (radius=1)
5. Paste back to image

**Color Detection Algorithm**:
1. Crop center 50% of text block
2. Find most common color (background)
3. Filter pixels >30 RGB distance from background
4. Return most common remaining color (text)
5. Fallback: black (0,0,0)

**Font Sizing Algorithm**:
1. Start with estimated size (height × 0.8)
2. Measure rendered text width
3. If exceeds block width, reduce by 1pt
4. Repeat until fits or reaches 8pt minimum
5. Render at final size

---

## 📊 Supported Formats

### Input Formats
- JPEG/JPG
- PNG (with transparency)
- WEBP
- BMP
- TIFF
- GIF (first frame only)

### Output Formats
- PNG (lossless, optimized)
- JPEG (95% quality)
- WEBP (modern compression)
- BMP (uncompressed)
- TIFF (professional)

---

## 🎯 Common Workflows

### Remove Watermark
1. Upload image
2. Press `Ctrl+F` to detect text
3. Select watermark text block
4. Click "🗑️ Delete Selected"
5. Press `Ctrl+E` to export

### Replace Product Price
1. Upload product image
2. Detect text
3. Select price text (e.g., "$99")
4. Replace with new price (e.g., "$79")
5. Click "✏️ Replace Selected"
6. Save image

### Batch Text Update
1. Upload image with repeated text
2. Detect all text
3. Select one instance
4. Enter new text
5. Click "🔄 Replace All"
6. All instances updated at once

### Create Clean Template
1. Upload image with text
2. Detect all text
3. Click "🗑️ Delete All"
4. Confirm deletion
5. Add new text with drawing tools
6. Export final image

---

## 🐛 Troubleshooting

### Text Detection Issues

**Problem**: No text detected  
**Solutions**:
- Increase contrast before detection
- Ensure text is clear and readable
- Check text size (very small text may not detect)
- Try different image formats

**Problem**: Low confidence scores  
**Solutions**:
- Increase image resolution
- Improve lighting/contrast
- Remove noise with filters first
- Use sharpen filter before detection

**Problem**: First detection very slow  
**Explanation**: Normal - EasyOCR loads model (~2GB RAM)  
**Solution**: Subsequent detections are much faster

---

### Replacement Issues

**Problem**: Replacement text too small  
**Solutions**:
- Original text block may be too small
- Manually add text with drawing tools instead
- Increase image resolution before editing

**Problem**: Color doesn't match  
**Solutions**:
- Use "🎨 Pick Color" for manual selection
- Adjust image contrast before detection
- Sample color from original text manually

**Problem**: Background not clean after deletion  
**Solutions**:
- Works best on solid/simple backgrounds
- Complex backgrounds may show artifacts
- Use clone stamp tool in advanced editor for complex cases

---

### Installation Issues

**Problem**: "No module named 'easyocr'"  
**Solution**: `pip install easyocr`

**Problem**: "No module named 'cv2'"  
**Solution**: `pip install opencv-python`

**Problem**: Model download fails  
**Solutions**:
- Check internet connection
- Retry detection (auto-retries)
- Manually download from EasyOCR GitHub

**Problem**: "No module named 'tkinter'"  
**Solutions**:
- Linux: `sudo apt install python3-tk`
- macOS: Included with python.org Python
- Windows: Reinstall Python with tcl/tk option

---

## 📈 Performance Tips

1. **First Detection**: Takes 10-30 seconds (model loading)
2. **Subsequent Detections**: 2-5 seconds per image
3. **Large Images**: Consider resizing before detection
4. **Batch Operations**: Use "Replace All" instead of individual replacements
5. **GPU Acceleration**: Install CUDA for 2-3x speedup (optional)

---

## 🎓 Best Practices

### For Best Detection Results
- Use high-resolution images (300+ DPI)
- Ensure good contrast between text and background
- Avoid heavily compressed JPEGs
- Clean images work better than noisy ones

### For Best Replacement Results
- Match font size to original when possible
- Use auto-detect color for consistency
- Preview changes before saving
- Use undo if result isn't perfect

### For Best Deletion Results
- Works best on solid backgrounds
- Increase padding for cleaner edges
- Use blur filters after deletion if needed
- Consider manual touch-up for complex backgrounds

---

## 📚 Additional Resources

- **README.md**: Complete feature overview
- **INSTALL.md**: Detailed installation guide
- **QUICKSTART.md**: 5-minute getting started
- **IMPLEMENTATION.md**: Technical implementation details

---

## 🚀 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│  PyImageEditor - Quick Reference                        │
├─────────────────────────────────────────────────────────┤
│  LAUNCH:        python3 main.py                         │
│  VERIFY:        python3 verify_install.py               │
│  TEST:          python3 test_features.py                │
├─────────────────────────────────────────────────────────┤
│  TEXT OPERATIONS:                                       │
│    Ctrl+F       Detect text                             │
│    Enter        Replace selected                        │
│    Delete       Delete selected                         │
│    Escape       Clear selection                         │
├─────────────────────────────────────────────────────────┤
│  EDITING:                                               │
│    Ctrl+Z       Undo                                    │
│    Ctrl+Y       Redo                                    │
│    Ctrl+S       Save As                                 │
│    Ctrl+E       Export to Desktop                       │
├─────────────────────────────────────────────────────────┤
│  WORKFLOW:                                              │
│    1. Upload image                                      │
│    2. Detect text (Ctrl+F)                              │
│    3. Select block from list                            │
│    4. Replace or delete                                 │
│    5. Export (Ctrl+E)                                   │
└─────────────────────────────────────────────────────────┘
```

---

**Version**: 2.0 with Interactive Text Editing  
**Last Updated**: January 2024  
**License**: Educational and Personal Use

**Happy Editing! 🎨✨**
