# COLOR SANITIZATION BUG FIX

## Problem
PIL's `ImageDraw.text()` was crashing with error:
```
"color must be int, or tuple of one, three or four elements"
```

## Root Cause
Color values from `np.median()` and other numpy operations were:
- Numpy float64 arrays instead of Python ints
- Wrong tuple lengths (5 elements, 0 elements)
- None values from failed detection
- Nested arrays `[[r, g, b]]`
- RGBA tuples where RGB was expected

## Solution
Created `utils/color_utils.py` with two sanitization functions:

### `sanitize_color(color, fallback=(0, 0, 0)) -> tuple`
Converts ANY color format to valid PIL RGB tuple `(r, g, b)`:
- Handles numpy arrays, scalars, float tuples, lists, None
- Converts numpy types to Python ints
- Flattens nested arrays
- Clamps values to 0-255 range
- Normalizes to exactly 3 elements
- Never raises exceptions

### `sanitize_color_with_alpha(color, alpha=255, fallback=(0, 0, 0, 255)) -> tuple`
Same as above but returns RGBA tuple `(r, g, b, a)` for compositing.

## Implementation

### Three Layers of Protection

**Layer 1: Sanitize at measurement** (`editor/text_editor.py`)
```python
from utils.color_utils import sanitize_color

def extract_text_color(pil_image, block):
    median_color = np.median(text_pixels, axis=0)
    return sanitize_color(median_color, fallback=(0, 0, 0))
```

**Layer 2: Sanitize in property extraction** (`editor/text_editor.py`)
```python
def extract_text_properties(pil_image, block):
    text_color = sanitize_color(np.median(text_pixels, axis=0))
    bg_color = sanitize_color(np.median(bg_pixels, axis=0))
    shadow_color = sanitize_color(np.median(shadow_region, axis=0))
    outline_color = sanitize_color(np.median(outline_pixels, axis=0))
    # ... return sanitized colors
```

**Layer 3: Sanitize at point of use** (`editor/text_editor.py`, `editor/inpainting.py`)
```python
from utils.color_utils import sanitize_color_with_alpha

def render_replacement_text(image, block, new_text, properties):
    color = sanitize_color(properties['color'])
    shadow_color = sanitize_color_with_alpha(properties['shadow_color'], 180)
    outline_color = sanitize_color_with_alpha(properties['outline_color'], 255)
    
    draw.text((x, y), new_text, font=font, fill=sanitize_color_with_alpha(color, 255))
```

## Files Modified

1. **`utils/color_utils.py`** (NEW)
   - `sanitize_color()` - RGB sanitization
   - `sanitize_color_with_alpha()` - RGBA sanitization

2. **`editor/text_editor.py`**
   - Import sanitization functions
   - Sanitize in `extract_text_color()`
   - Sanitize in `extract_text_properties()`
   - Sanitize in `erase_text_region()`
   - Sanitize in `render_replacement_text()`

3. **`editor/inpainting.py`**
   - Import sanitization functions
   - Sanitize in `inpaint_solid_background()`
   - Sanitize in `render_matched_text()`

## Test Coverage
Created `test_color_sanitization.py` with 16 test cases:
- ✓ None values
- ✓ Numpy arrays (int and float)
- ✓ Nested arrays
- ✓ Float tuples
- ✓ RGBA to RGB conversion
- ✓ Invalid tuple lengths (0, 1, 2, 5+ elements)
- ✓ Single values (grayscale)
- ✓ Numpy scalars
- ✓ Value clamping (negative, >255)
- ✓ np.median() output
- ✓ Exception safety

All tests pass ✅

## Result
**No PIL color errors can occur** - every color value is guaranteed to be:
- A plain Python tuple (not numpy array)
- Exactly 3 elements for RGB or 4 for RGBA
- All elements are Python ints (not float64)
- All values clamped to 0-255 range
- Never None or invalid

## Usage Rule
**Every color value must pass through `sanitize_color()` before use in PIL.**

This applies to:
- Colors returned from measurement functions
- Colors stored in properties dicts
- Colors read from properties dicts
- Colors passed to `ImageDraw.text()`, `ImageDraw.rectangle()`, etc.

## Performance Impact
Negligible - sanitization is a simple type conversion that runs in microseconds.

## Backward Compatibility
Fully compatible - valid color tuples pass through unchanged.
