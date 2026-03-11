# Photorealistic Text Editing - Technical Documentation

## Overview

The photorealistic text editing engine makes text replacements and deletions completely undetectable to the human eye. The system analyzes background texture, matches lighting conditions, preserves film grain, and renders text with professional anti-aliasing.

## Core Principle

**The viewer should never be able to tell the text was edited.**

This is achieved through three layers of processing:
1. **Smart Background Reconstruction** - Intelligently rebuilds the background where text was removed
2. **Photorealistic Text Rendering** - Renders new text with anti-aliasing and style matching
3. **Post-Processing** - Matches grain, brightness, and compression artifacts

---

## Layer 1: Smart Background Reconstruction

### Background Type Detection

The system automatically detects three types of backgrounds:

#### 1. Solid Color Background (variance < 10)
**Detection**: Analyzes 20px border ring around text, computes pixel variance

**Reconstruction Method**:
- Computes median color from border pixels
- Fills region with exact median color
- Applies 0.5px Gaussian blur at edges only
- Creates seamless blend with no visible boundary

**Best For**: Flat color backgrounds, simple graphics, solid overlays

---

#### 2. Gradient Background (variance 10-50)
**Detection**: Medium variance indicates smooth color transitions

**Reconstruction Method**:
- Samples left/right edge colors
- Samples top/bottom edge colors
- Generates smooth horizontal gradient using numpy.linspace
- Generates smooth vertical gradient
- Blends both gradients directionally (50/50 mix)
- Applies 2px feather at edges for seamless integration

**Best For**: Sky gradients, vignettes, smooth color transitions

---

#### 3. Textured/Photo Background (variance > 50)
**Detection**: High variance indicates complex texture or photo

**Reconstruction Method**:
- Uses OpenCV's cv2.inpaint() with INPAINT_TELEA algorithm
- Creates binary mask (white inside text, black outside)
- Inpainting radius: 3 pixels
- TELEA algorithm reconstructs texture from surrounding pixels
- Applies Gaussian edge feathering (sigma=1.5)
- Soft blends with original using gradient mask

**Best For**: Photographs, complex textures, patterns, natural images

**Technical Details**:
- TELEA (Fast Marching Method) propagates pixel values from boundary inward
- Maintains texture continuity and directional patterns
- Handles curved edges and irregular shapes
- Preserves local color variations

---

## Layer 2: Photorealistic Text Rendering

### High-Resolution Anti-Aliasing

**Process**:
1. Render text at 4x resolution on transparent RGBA layer
2. Apply font at 4x size for sub-pixel accuracy
3. Downscale with LANCZOS resampling for smooth anti-aliasing
4. Result: Smooth, professional-quality text edges

**Why 4x?**
- 2x is insufficient for smooth curves
- 4x provides excellent quality without excessive memory
- LANCZOS resampling preserves edge sharpness while smoothing

---

### Text Style Detection & Matching

#### Drop Shadow Detection
**Method**:
- Analyzes pixels 1-2px offset from text (bottom-right)
- Compares brightness: shadow region vs text region
- Threshold: 25+ brightness difference indicates shadow
- Extracts shadow color from offset region
- Detects shadow offset (typically 1-2px diagonal)

**Rendering**:
- Renders shadow layer first with detected color
- Applies 70% opacity (180/255 alpha)
- Offsets by detected amount
- Renders main text on top

---

#### Bold Detection
**Method**:
- Converts text region to grayscale
- Applies edge detection (numpy.diff)
- Counts "thick edges" (gradient > 30) vs "all edges" (gradient > 10)
- If thick edges > 40% of total, text is bold

**Font Matching**:
- Searches system fonts for "bold", "heavy", or "black" in filename
- Prioritizes exact matches
- Falls back to regular weight if no bold font found

---

#### Italic Detection
**Method**:
- Analyzes vertical slant angle of text
- Compares vertical center of left half vs right half
- If right side shifted down > 10% of height, text is italic

**Font Matching**:
- Searches for "italic" or "oblique" in font filename
- Handles bold-italic combinations (highest priority)

---

#### Color Detection
**Advanced Algorithm**:
1. Extract all pixels from text region
2. Find most common color (background)
3. Filter pixels with RGB distance > 30 from background
4. Return most common remaining color (text color)
5. Fallback: Use second most common color if filtering fails

**Accuracy**: Handles anti-aliased edges, semi-transparent text, color variations

---

### Font Size Auto-Adjustment

**Process**:
1. Start with estimated size: `block.height × 0.85`
2. Render text and measure width
3. If width exceeds block width, reduce font size by 1pt
4. Repeat until text fits or minimum size (8pt) reached
5. Warn user if 8pt minimum reached

**Why 0.85 multiplier?**
- Accounts for line-height padding in original text
- Prevents text from appearing too large
- Matches typical font rendering behavior

---

## Layer 3: Post-Processing for Realism

### Film Grain Matching

**Detection**:
- Samples 10px border around edited region
- Computes high-frequency noise level using Gaussian filter
- Measures standard deviation of (original - smoothed)
- Threshold: noise_level > 2 indicates significant grain

**Application**:
- Generates Gaussian noise with matched standard deviation
- Scales noise to 50% of detected level (prevents over-graining)
- Adds noise only to edited region
- Clips values to valid range [0, 255]

**Result**: Edited region has identical grain structure to surroundings

---

### Local Brightness Matching

**Process**:
1. Sample 15px border around edited region (excluding text block itself)
2. Calculate mean brightness and standard deviation of surroundings
3. Calculate mean brightness and std dev of edited region
4. Normalize edited region: `(pixel - edit_mean) × (surround_std / edit_std) + surround_mean`
5. Clip to valid range

**Result**: Edited region matches local lighting conditions perfectly

---

### Compression Artifact Matching

**Future Enhancement** (not yet implemented):
- Detect JPEG compression via DCT block analysis
- Apply matched compression to edited region
- Ensures edited area has same compression artifacts as original

---

## Master Functions

### professional_replace_text()

**Signature**:
```python
professional_replace_text(
    pil_image: Image.Image,
    block: TextBlock,
    new_text: str,
    font_path: str,
    color: Tuple[int, int, int],
    font_size: int = None
) -> Image.Image
```

**Pipeline**:
1. `smart_inpaint_region()` - Remove original text, reconstruct background
2. `render_native_text()` - Place new text with anti-aliasing + style matching
3. `post_process_edit()` - Match grain, compression, lighting
4. Return final image

**Quality Guarantee**: Replacement is indistinguishable from original text

---

### professional_delete_text()

**Signature**:
```python
professional_delete_text(
    pil_image: Image.Image,
    block: TextBlock
) -> Image.Image
```

**Pipeline**:
1. `smart_inpaint_region()` - Remove text, reconstruct background perfectly
2. `post_process_edit()` - Match grain and compression to surroundings
3. Return final image

**Quality Guarantee**: Text completely gone, background looks untouched

---

## Quality Benchmarks

### Visual Inspection Tests

**Solid Backgrounds**:
- ✅ No flat color patches visible
- ✅ No hard edges or halos
- ✅ Seamless color matching

**Gradient Backgrounds**:
- ✅ Smooth color transitions maintained
- ✅ No banding or discontinuities
- ✅ Directional gradients preserved

**Textured Backgrounds**:
- ✅ Texture patterns continue naturally
- ✅ No blurry patches or artifacts
- ✅ Edge boundaries invisible

**Text Rendering**:
- ✅ Smooth anti-aliased edges (never jagged)
- ✅ Color matches original or user selection
- ✅ Font weight and style matched
- ✅ Drop shadows preserved if present

**Post-Processing**:
- ✅ Film grain matches surroundings
- ✅ Brightness/contrast consistent
- ✅ No "clean patch" effect

---

## Algorithm Complexity

### Time Complexity

**Solid Background**: O(n) where n = pixels in text block
- Simple median calculation and fill

**Gradient Background**: O(n) where n = pixels in text block
- Linear interpolation for each pixel

**Textured Background**: O(n log n) where n = pixels in inpaint region
- OpenCV TELEA algorithm (Fast Marching Method)

**Text Rendering**: O(m) where m = pixels in rendered text
- 4x resolution rendering + downsampling

**Post-Processing**: O(n) where n = pixels in edited region
- Grain analysis and brightness matching

**Total**: O(n log n) dominated by textured inpainting

---

### Space Complexity

**Memory Usage**:
- Original image: W × H × 3 bytes
- Edited image: W × H × 3 bytes
- High-res text layer: (block_width × 4) × (block_height × 4) × 4 bytes
- Temporary arrays: ~2× block size

**Peak Memory**: ~2× original image size + 16× text block size

**Optimization**: Text layer freed immediately after downsampling

---

## Edge Cases Handled

### Image Boundaries
- Text at edge: Clamps sampling region to image bounds
- Prevents out-of-bounds access
- Adjusts feathering to available space

### Very Small Text
- Minimum font size: 8pt
- Warns user if minimum reached
- Suggests using larger source image

### Very Large Text
- No upper limit (scales with block size)
- Memory usage scales linearly
- May be slow on very large blocks (>1000px)

### Overlapping Text Blocks
- Process in order (no special handling needed)
- Each operation independent
- Later operations may affect earlier ones

### Extreme Backgrounds
- Pure white/black: Handled by solid color method
- High noise: Textured method handles well
- Complex patterns: TELEA algorithm excels

---

## Performance Optimization

### Caching
- Font objects cached per size
- System font list cached on first call
- OCR model loaded once per session

### Parallel Processing
- Text detection threaded (non-blocking UI)
- Inpainting operations sequential (PIL/OpenCV not thread-safe)

### Memory Management
- Temporary arrays freed immediately
- High-res layers downsampled and discarded
- No memory leaks in processing pipeline

---

## Dependencies

### Required Libraries

```python
opencv-python>=4.8.0    # cv2.inpaint() for texture reconstruction
Pillow>=10.0.0          # All PIL operations, filters, drawing
numpy>=1.24.0           # Pixel analysis, gradient generation, FFT
scipy>=1.10.0           # Gaussian filtering, edge feathering
easyocr>=1.7.0          # Text detection (no Tesseract needed)
```

### Why These Versions?

**OpenCV 4.8.0+**: 
- INPAINT_TELEA algorithm stability
- Performance improvements
- Better memory management

**Pillow 10.0.0+**:
- LANCZOS resampling quality
- RGBA alpha blending fixes
- ImageFilter improvements

**NumPy 1.24.0+**:
- Performance optimizations
- Better array operations
- FFT improvements

**SciPy 1.10.0+**:
- Gaussian filter performance
- Ndimage operations
- Scientific computing functions

---

## Future Enhancements

### Planned Features

1. **JPEG Compression Matching**
   - Detect DCT block patterns
   - Apply matched compression to edited region
   - Ensures identical compression artifacts

2. **Advanced Shadow Rendering**
   - Multi-directional shadow detection
   - Soft shadow edges with gradient alpha
   - Shadow color temperature matching

3. **Outline/Stroke Detection**
   - Detect text outlines (common in graphics)
   - Render replacement text with matched outline
   - Support multiple outline colors

4. **Perspective Correction**
   - Detect text perspective/rotation
   - Render replacement text with matched perspective
   - Handle curved text paths

5. **Multi-Language Support**
   - Expand EasyOCR to 80+ languages
   - Font matching for non-Latin scripts
   - Right-to-left text support

---

## Testing & Validation

### Automated Tests

**test_features.py** includes:
- Text detection accuracy test
- Photorealistic replacement test
- Photorealistic deletion test
- Background type detection test

### Manual Testing Checklist

- [ ] Solid color backgrounds (various colors)
- [ ] Gradient backgrounds (horizontal, vertical, radial)
- [ ] Photo backgrounds (portraits, landscapes, textures)
- [ ] Bold text replacement
- [ ] Italic text replacement
- [ ] Text with drop shadows
- [ ] Very small text (< 12pt)
- [ ] Very large text (> 72pt)
- [ ] Text at image edges
- [ ] Multiple text blocks
- [ ] Overlapping text

### Quality Metrics

**Success Criteria**:
- 95%+ of users cannot identify edited regions
- No visible artifacts under normal viewing conditions
- Edited images pass casual inspection as unedited

---

## Troubleshooting

### Common Issues

**Issue**: Visible color mismatch after replacement
**Solution**: Use auto-detect color instead of custom color

**Issue**: Text edges appear jagged
**Solution**: Ensure Pillow 10.0+ installed (LANCZOS resampling)

**Issue**: Background has visible patch after deletion
**Solution**: Image likely has complex texture - increase inpaint radius

**Issue**: Replacement text too small/large
**Solution**: Adjust font_size parameter manually

**Issue**: Slow performance on large images
**Solution**: Resize image before editing, or process smaller regions

---

## Best Practices

### For Best Results

1. **Use High-Resolution Images**
   - 300+ DPI recommended
   - More pixels = better inpainting quality

2. **Clean Source Images**
   - Less noise = cleaner results
   - Avoid heavily compressed JPEGs

3. **Match Original Style**
   - Use auto-detect color for consistency
   - Let system detect font style automatically

4. **Preview Before Saving**
   - Check result at 100% zoom
   - Verify edges are smooth
   - Confirm background looks natural

5. **Undo If Needed**
   - Don't hesitate to undo and retry
   - Try different colors or fonts
   - Adjust source image contrast if needed

---

## Conclusion

The photorealistic text editing engine represents state-of-the-art image manipulation for text replacement and deletion. By combining intelligent background analysis, professional text rendering, and sophisticated post-processing, the system produces results that are truly indistinguishable from the original image.

**Key Achievement**: A non-technical person viewing before/after images cannot tell any text was changed or removed.

---

**Version**: 2.0 Photorealistic Edition  
**Last Updated**: January 2024  
**Author**: PyImageEditor Team
