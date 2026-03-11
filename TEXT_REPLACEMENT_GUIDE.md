# Text Selection & Replacement Feature

## Overview

The Text Selection & Replacement feature allows users to automatically detect text in images using OCR (Optical Character Recognition) and replace it with new text while maintaining the original styling and background.

## Features

### 1. Automatic Text Detection
- Uses Tesseract OCR to detect all text blocks in the image
- Extracts text content, position, size, and confidence score
- Only includes text with confidence > 40%
- Displays all detected text in an interactive list

### 2. Interactive Selection
- Click any text block in the list to select it
- Selected text is highlighted with a yellow dashed rectangle on the canvas
- Shows text position and content in the status label
- Keyboard navigation with Escape to deselect

### 3. Smart Text Replacement
- **Background Inpainting**: Automatically samples and fills the background color
- **Font Size Matching**: Estimates original font size from bounding box
- **Auto-scaling**: Reduces font size if replacement text is longer
- **Color Detection**: Automatically detects the original text color
- **Blur Blending**: Applies subtle blur to blend edges seamlessly

### 4. Batch Replacement
- Replace all occurrences of matching text at once
- Case-insensitive matching
- Single undo operation for batch replacements

## User Interface

### Text Select & Replace Panel

Located in the sidebar below other editing controls:

```
┌─────────────────────────────────────────┐
│  TEXT SELECT & REPLACE                  │
│                                         │
│  [🔍 Detect Text in Image]              │
│                                         │
│  Detected text blocks:                  │
│  ┌───────────────────────────────────┐  │
│  │ #1: "Hello World" (94%)           │  │
│  │ #2: "Sale 50% OFF" (87%)          │  │
│  │ #3: "Buy Now" (91%)               │  │
│  └───────────────────────────────────┘  │
│                                         │
│  Selected: "Hello World" at (120, 45)   │
│                                         │
│  Replace with:                          │
│  [____________________________]         │
│                                         │
│  Font Color: [Choose Color]             │
│                                         │
│  [✏️ Replace Selected Text]             │
│  [🔄 Replace All Occurrences]           │
└─────────────────────────────────────────┘
```

## Workflow

### Basic Text Replacement

1. **Load an image** with text
2. **Click "🔍 Detect Text in Image"** or press `Ctrl+F`
3. **Wait for detection** - a dialog will show how many blocks were found
4. **Select a text block** from the list by clicking it
5. **See the highlight** - yellow rectangle appears on the edited canvas
6. **Enter replacement text** in the "Replace with" field
7. **Optionally change color** by clicking "Choose Color"
8. **Click "✏️ Replace Selected Text"** or press `Enter`
9. **View the result** - text is replaced instantly
10. **Use Undo (Ctrl+Z)** if needed

### Replace All Occurrences

1. Follow steps 1-6 above
2. **Click "🔄 Replace All Occurrences"**
3. **Confirm** the replacement in the dialog
4. **All matching text** is replaced in one operation

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Open text detection and scan image |
| `Enter` | Replace selected text (when replacement field focused) |
| `Escape` | Deselect current text block |
| `Ctrl+Z` | Undo text replacement |
| `Ctrl+Y` | Redo text replacement |

## Technical Details

### Text Detection Algorithm

1. **OCR Processing**: Uses `pytesseract.image_to_data()` with detailed output
2. **Confidence Filtering**: Only includes blocks with confidence > 40%
3. **Bounding Box Extraction**: Gets precise x, y, width, height for each block
4. **Font Size Estimation**: Calculates from bounding box height (height × 0.8)

### Background Inpainting

1. **Border Sampling**: Samples pixels from expanded region border
2. **Color Averaging**: Calculates average RGB color
3. **Rectangle Fill**: Fills text region with background color
4. **Gaussian Blur**: Applies 1px blur for seamless blending

### Text Rendering

1. **Font Matching**: Uses detected or user-selected font
2. **Size Calculation**: Fits text within original width
3. **Auto-scaling**: Reduces size by 10% if text is too long
4. **Color Application**: Uses detected or user-selected color
5. **Position Preservation**: Renders at exact original coordinates

### Color Detection

1. **Center Region Sampling**: Samples middle 50% of bounding box
2. **Pixel Analysis**: Counts color frequency
3. **Most Common Color**: Returns the dominant non-background color
4. **RGB Tuple**: Returns as (R, G, B) for PIL compatibility

## Error Handling

### No Text Detected
- **Message**: "No text found in image. Try adjusting contrast first."
- **Suggestion**: Use contrast/brightness adjustments before detection

### Tesseract Not Installed
- **Message**: Shows installation instructions for each OS
- **Behavior**: Panel is disabled gracefully
- **Instructions**: Provides links and commands

### Empty Replacement
- **Confirmation**: "Replace with empty string? This will erase the text."
- **Behavior**: Requires user confirmation before proceeding

### Small Text Warning
- **Threshold**: Font size < 8 pixels
- **Message**: "Text may be too small to replace accurately"
- **Behavior**: Warns but allows replacement

## File Structure

### New Files

```
editor/text_editor.py          # Core text replacement logic
  - TextBlock dataclass
  - detect_all_text()
  - detect_text_color()
  - get_background_color()
  - erase_text_region()
  - render_replacement_text()
  - replace_text_in_image()
  - replace_all_matching()

ui/text_select_panel.py        # UI panel
  - TextSelectPanel class
  - Listbox for text blocks
  - Replacement controls
  - Event handlers
```

### Modified Files

```
app.py                         # Integration
  - Added text panel callbacks
  - Added Ctrl+F shortcut
  - Added text replacement methods

ui/canvas.py                   # Highlighting
  - Added highlight_text_block()
  - Added clear_highlight()
  - Added scale factor tracking
```

## Dependencies

- **pytesseract**: OCR text detection
- **Tesseract OCR**: System binary for OCR
- **PIL/Pillow**: Image manipulation
- **NumPy**: Color analysis and array operations
- **tkinter**: UI components

## Limitations

1. **OCR Accuracy**: Depends on image quality and text clarity
2. **Font Matching**: May not perfectly match original font
3. **Complex Backgrounds**: Works best with solid or simple backgrounds
4. **Rotated Text**: Best results with horizontal text
5. **Small Text**: Text smaller than 8px may not replace accurately

## Best Practices

1. **High Quality Images**: Use clear, high-resolution images
2. **Good Contrast**: Ensure text has good contrast with background
3. **Horizontal Text**: Works best with non-rotated text
4. **Simple Backgrounds**: Solid or gradient backgrounds work best
5. **Test First**: Try on a single block before replacing all

## Future Enhancements

Possible improvements for future versions:

- [ ] Visual text selection by clicking on canvas
- [ ] Font style detection (bold, italic)
- [ ] Multi-line text support
- [ ] Curved text replacement
- [ ] Advanced background reconstruction
- [ ] Custom OCR language selection
- [ ] Text search and filter
- [ ] Export replacement history

## Troubleshooting

### Text Not Detected
- Increase image contrast
- Ensure text is clear and readable
- Check Tesseract is installed correctly
- Try with different image formats

### Poor Replacement Quality
- Adjust font color manually
- Try different font sizes
- Use images with simpler backgrounds
- Increase image resolution

### Tesseract Errors
- Verify installation: `tesseract --version`
- Check PATH environment variable
- Reinstall Tesseract if needed
- Restart application after installation

## Examples

### Use Case 1: Product Label Update
- Detect text on product packaging
- Replace product name or price
- Maintain original styling
- Export updated image

### Use Case 2: Meme Text Replacement
- Detect meme text
- Replace with custom text
- Keep original font style
- Share updated meme

### Use Case 3: Sign Translation
- Detect text on signs
- Replace with translated text
- Preserve background
- Export localized version

## Performance

- **Detection Speed**: 1-3 seconds for typical images
- **Replacement Speed**: Instant (<100ms per block)
- **Memory Usage**: Minimal overhead
- **Undo History**: Included in standard 10-step history

## Conclusion

The Text Selection & Replacement feature provides a powerful, user-friendly way to edit text in images without manual pixel editing. It combines OCR technology with smart image processing to deliver professional results with minimal effort.
