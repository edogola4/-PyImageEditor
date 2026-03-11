# PyImageEditor

A complete desktop image editing application built with Python and Tkinter.

## Features

### Core Capabilities
- **Multi-format Support**: JPEG, PNG, WEBP, BMP, TIFF, GIF (including animated GIF first frame)
- **Live Preview**: Side-by-side original vs edited image display
- **Undo/Redo**: 10-step history with Ctrl+Z and Ctrl+Y shortcuts
- **Export**: Save in original or custom format with quality preservation

### Image Adjustments
- Brightness (0-200%, default 100%)
- Contrast (0-200%, default 100%)
- Saturation (0-200%, default 100%)
- Sharpness (0-200%, default 100%)

### Transform Operations
- Crop (via coordinate input)
- Flip horizontal/vertical
- Rotate by custom degrees
- Resize with aspect ratio lock option

### Filters
- Grayscale
- Sepia tone
- Gaussian blur
- Sharpen
- Edge detection (Canny algorithm)
- Emboss

### Drawing Tools
- Shapes: Rectangle, Circle, Line
- Customizable color and thickness (1-20px)
- Text overlay with automatic font detection and matching

### Text Selection, Replacement & Deletion
- **Photorealistic Editing**: Edits are completely undetectable to the human eye
- **Smart Background Reconstruction**: Automatically detects solid, gradient, or textured backgrounds
- **Intelligent Inpainting**: Uses OpenCV TELEA algorithm for complex textures
- **Professional Text Rendering**: 4x resolution anti-aliasing for smooth edges
- **Style Matching**: Detects and preserves bold, italic, shadows, and outlines
- **Grain Matching**: Preserves film grain and noise patterns
- **Brightness Matching**: Edited regions match surrounding lighting conditions
- Automatic text detection using EasyOCR (no Tesseract required)
- Interactive text block selection with visual highlighting
- Replace individual text blocks or all occurrences
- Delete text blocks with seamless background reconstruction
- Automatic font color detection
- Batch operations (replace all / delete all)
- Real-time preview of changes

### Smart Font Matching
- Automatically matches closest available system font
- Fallback to default fonts if no match found
- Font size auto-adjustment to fit original text bounds

## Installation

### Quick Install

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Verify installation
python3 verify_install.py

# 3. Run the application
python3 main.py
```

Note: EasyOCR will download language models (~80MB) on first run.

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- Pillow (image processing)
- opencv-python (advanced filters)
- easyocr (text detection - no external binaries needed)
- fonttools (font matching)
- numpy (array operations)
- scipy (scientific computing)

Note: `tkinter` is usually built-in with Python. If not available:
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **macOS**: Included with Python from python.org
- **Windows**: Included with standard Python installation

### 2. Verify Installation

```bash
python3 verify_install.py
```

This will check all dependencies and confirm the installation is complete.

## Usage

### Running the Application

```bash
cd image_editor
python main.py
```

### Basic Workflow

1. **Upload Image**: Click "Upload Image" button and select a file
2. **Edit**: Use sidebar controls to adjust, transform, filter, or draw
3. **Preview**: View changes in real-time on the right panel
4. **Undo/Redo**: Use buttons or Ctrl+Z / Ctrl+Y
5. **Save**: Click "Save As" to export in your chosen format

### Keyboard Shortcuts

- `Ctrl+Z`: Undo
- `Ctrl+Y`: Redo
- `Ctrl+F`: Detect text in image
- `Ctrl+S`: Save image
- `Ctrl+E`: Export to Desktop
- `Delete`: Delete selected text block
- `Escape`: Clear text selection

### Adjustment Sliders

All adjustment sliders work in real-time:
- Move slider to see immediate preview
- Changes are non-destructive until you apply a filter or transform
- Reset by moving sliders back to 100

### Applying Filters

Filters are applied immediately and added to history:
- Click any filter button in the Filters section
- Use Undo to revert if needed

### Drawing Shapes

1. Select shape type (Rectangle, Circle, or Line)
2. Click "Choose Color" to pick a color
3. Adjust thickness slider (1-20px)
4. Click "Draw Shape"
5. Enter coordinates in the dialog prompts

### Adding Text

1. Adjust font size slider (10-100)
2. Click "Choose Color" for text color
3. Click "Add Text"
4. Enter text in the dialog
5. Enter X and Y coordinates for text position

The application automatically detects fonts in your image and matches the closest system font.

### Finding, Replacing & Deleting Text

1. Click "🔍 Detect Text in Image" to scan for text (first run downloads OCR model)
2. Select a text block from the list
3. The selected text will be highlighted in yellow on the canvas
4. Enter replacement text in the "Replace with" field (or leave empty to delete)
5. Choose color: "■ Auto-detect" or "🎨 Pick Color"
6. Click "✏️ Replace Selected" to replace just that block
7. Click "🗑️ Delete Selected" to remove the text
8. Click "🔄 Replace All" to replace all matching text
9. Click "🗑️ Delete All" to remove all detected text

**Keyboard Shortcuts:**
- `Ctrl+F`: Open text detection panel and scan for text
- `Enter`: Replace selected text (when replacement field is focused)
- `Delete`: Delete selected text block
- `Escape`: Deselect current text block

### Saving & Exporting Images

**Save As (Ctrl+S):**
1. Click "💾 Save As..." button
2. Choose file format (JPEG, PNG, WEBP, BMP, TIFF)
3. Enter filename and location
4. Image is saved with original DPI and quality settings

**Quick Export (Ctrl+E):**
1. Click "⬇️ Export to Desktop" button
2. Image is automatically saved to Desktop with timestamp
3. Format: `{original_name}_edited_{timestamp}.{ext}`

## Project Structure

```
image_editor/
├── main.py                  # Entry point
├── app.py                   # Main application window
├── editor/
│   ├── __init__.py
│   ├── image_ops.py         # Image manipulation functions
│   ├── filters.py           # Filter operations
│   ├── shapes.py            # Shape drawing
│   ├── text_overlay.py      # Text overlay with font detection
│   ├── text_editor.py       # Text detection and replacement
│   └── history.py           # Undo/redo manager
├── ui/
│   ├── __init__.py
│   ├── toolbar.py           # Top toolbar
│   ├── sidebar.py           # Left control panel
│   ├── canvas.py            # Image preview canvas
│   ├── metadata_panel.py    # Image info display
│   └── text_select_panel.py # Text selection and replacement UI
├── utils/
│   ├── __init__.py
│   ├── file_handler.py      # File I/O operations
│   ├── font_matcher.py      # Font detection and matching
│   └── ocr_engine.py        # EasyOCR singleton manager
```

## Technical Details

### Image Processing
- **PIL/Pillow**: Core image manipulation
- **OpenCV**: Advanced filters (edge detection)
- **NumPy**: Array operations for custom filters

### OCR Engine
- **EasyOCR**: Deep learning-based text detection (no external binaries)
- **GPU acceleration**: Optional (falls back to CPU)
- **Language support**: English (expandable to 80+ languages)

### UI Framework
- **Tkinter**: Native Python GUI framework
- **ttk**: Themed widgets for modern appearance

### Quality Preservation
- JPEG: 95% quality, optimized
- PNG: Lossless with optimization
- DPI metadata preserved from original

## Troubleshooting

### First Run: OCR Model Download
- EasyOCR downloads language models (~80MB) on first text detection
- Progress shown in terminal
- Models cached for future use
- Requires internet connection for initial download

### "No module named 'cv2'" Error
```bash
pip install opencv-python
```

### "No module named 'PIL'" Error
```bash
pip install Pillow
```

### "No module named 'easyocr'" Error
```bash
pip install easyocr
```

### Text Detection Slow
- First detection is slower (model loading)
- Subsequent detections are faster (model cached in memory)
- Large images take longer to process
- Consider resizing very large images first

### Image Not Loading
- Verify file format is supported
- Check file is not corrupted
- Ensure sufficient memory for large images

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: 2GB minimum (4GB recommended for large images)
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Display**: 1400x800 minimum resolution

## License

This project is provided as-is for educational and personal use.

## Contributing

This is a complete, standalone application. Feel free to extend with additional features:
- Batch processing
- Custom filter creation
- Layer support
- Advanced selection tools
- Plugin system
