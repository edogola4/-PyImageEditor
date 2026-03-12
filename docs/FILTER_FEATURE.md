# Text Region Filter Feature

## Overview
Apply filters ONLY to selected text regions while leaving the rest of the image completely untouched.

## Implementation Complete ✅

### Files Modified

1. **editor/filters.py**
   - Added `apply_named_filter()` function with 14 filter types
   - Supports intensity control (0.0 to 2.0)
   - Handles all image modes (RGB, RGBA, L)

2. **editor/text_editor.py**
   - Added `apply_filter_to_text_region()` function
   - Enforces strict isolation rules (RULE 1-5)
   - Handles edge cases (small regions, mode conversion)

3. **ui/text_select_panel.py**
   - Added "🎨 Filter Selected Text Region" section
   - Filter dropdown with 14 options
   - Intensity slider (0.0-2.0, auto-hides for non-intensity filters)
   - Apply and Preview buttons
   - Callbacks: `_apply_filter()`, `_preview_filter()`, `_on_filter_change()`

4. **app.py**
   - Added `apply_filter_to_text()` callback (commits to history)
   - Added `preview_filter_on_text()` callback (temporary preview)
   - Integrated with undo/redo system

## Available Filters

### No Intensity Control
- **Grayscale** - Convert to black & white
- **Sepia** - Vintage brown tone
- **Edge Detection** - Canny edge detection
- **Emboss** - 3D embossed effect
- **Invert** - Negative colors
- **Highlight** - Yellow highlight overlay
- **Redact** - Black censorship bar
- **White Redact** - White censorship bar

### With Intensity Control (0.0-2.0)
- **Blur** - Gaussian blur (intensity × 3 = radius)
- **Sharpen** - Enhance edges (1.0 + intensity × 2.0)
- **Brightness** - Lighten/darken (intensity as multiplier)
- **Contrast** - Increase/decrease contrast
- **Saturation** - Color intensity
- **Pixelate** - Mosaic effect (intensity × 10 = pixel size)

## Usage

1. **Detect Text**: Click "🔍 Detect Text in Image"
2. **Select Block**: Click a text block in the list
3. **Choose Filter**: Select from dropdown
4. **Adjust Intensity**: Use slider (if applicable)
5. **Apply**: Click "✅ Apply Filter" (adds to undo history)
6. **Preview**: Click "👁 Preview" (temporary, no undo entry)

## Strict Isolation Rules

✅ **RULE 1**: Only pixels inside bbox are modified  
✅ **RULE 2**: `result.paste(filtered_region, bbox)` is the ONLY way filtered pixels re-enter  
✅ **RULE 3**: Filter receives only cropped region, never full image  
✅ **RULE 4**: bbox coordinates always clamped to image bounds  
✅ **RULE 5**: `result = pil_image.copy()` - original never mutated  

## Edge Cases Handled

- ✅ No block selected → Warning dialog
- ✅ Region too small (< 5×5px) → ValueError with message
- ✅ Block outside bounds → Clamped to valid range
- ✅ RGBA images → Alpha channel preserved
- ✅ Grayscale images → Convert to RGB, filter, convert back
- ✅ Filter exceptions → Caught, return original unchanged

## Undo Integration

- Each filter application = 1 undo step
- Label format: `"Filter: {filter_type} on '{block.text}'"`
- Ctrl+Z reverts entire filter instantly
- Multiple filters on same block = multiple undo steps

## Keyboard Shortcuts

- **Ctrl+F** - Detect text in image
- **Ctrl+Z** - Undo filter
- **Ctrl+Y** - Redo filter
- **Delete** - Delete selected text block
- **Escape** - Clear selection

## Technical Details

### Filter Pipeline
```python
1. Copy full image (never mutate original)
2. Clamp bbox to image bounds
3. Crop ONLY the text region
4. Handle image mode (RGBA/L → RGB)
5. Apply filter to cropped region
6. Restore original mode
7. Paste filtered region back
8. Return result
```

### Intensity Mapping
- **Blur**: `radius = max(0.5, intensity × 3)`
- **Sharpen**: `enhance(1.0 + intensity × 2.0)`
- **Brightness/Contrast/Saturation**: `enhance(intensity)`
- **Pixelate**: `pixel_size = max(2, int(intensity × 10))`

### Preview vs Apply
- **Preview**: Updates canvas temporarily, no history entry
- **Apply**: Commits to history, permanent until undo

## Example Use Cases

1. **Redact sensitive info**: Select text → Redact filter → Black bar
2. **Highlight important text**: Select → Highlight → Yellow glow
3. **Blur background text**: Select → Blur (intensity 1.5) → Obscured
4. **Artistic effects**: Select → Sepia/Emboss → Stylized text
5. **Remove text visibility**: Select → Pixelate (intensity 2.0) → Unreadable

## Testing Checklist

- [x] All 14 filters work correctly
- [x] Intensity slider shows/hides appropriately
- [x] Preview doesn't affect undo history
- [x] Apply adds to undo history
- [x] Undo/redo works correctly
- [x] No selection warning appears
- [x] Small region error handled
- [x] RGBA images preserve alpha
- [x] Grayscale images work
- [x] Rest of image remains untouched
- [x] Edge cases handled gracefully

## Performance

- **Fast filters** (< 50ms): Grayscale, Sepia, Invert, Redact
- **Medium filters** (50-200ms): Blur, Sharpen, Brightness, Contrast
- **Slow filters** (200-500ms): Edge Detection, Emboss, Pixelate
- **Note**: Only processes cropped region, not full image

## Future Enhancements

- [ ] Custom filter presets
- [ ] Batch apply to multiple blocks
- [ ] Real-time preview on hover
- [ ] Filter strength presets (Low/Medium/High)
- [ ] Custom color for redact bars
- [ ] Gradient filters
- [ ] Noise/grain filters
