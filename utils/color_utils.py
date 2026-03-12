"""Color sanitization utilities for PIL compatibility."""


def sanitize_color(color, fallback=(0, 0, 0)) -> tuple:
    """
    Converts ANY color value into a valid PIL-compatible
    tuple of exactly 3 plain Python ints (R, G, B).
    
    Handles: numpy arrays, numpy scalars, float tuples,
    lists, None values, wrong-length tuples, nested arrays.
    
    Never raises — always returns a valid color.
    """
    try:
        if color is None:
            return fallback

        # Convert numpy arrays and matrices to list first
        if hasattr(color, 'tolist'):
            color = color.tolist()

        # Flatten if nested e.g. [[r, g, b]] or array of arrays
        if isinstance(color, (list, tuple)):
            # Unwrap single-element nesting
            while (isinstance(color, (list, tuple)) and
                   len(color) == 1 and
                   isinstance(color[0], (list, tuple))):
                color = color[0]

        # Convert to flat list of numbers
        if isinstance(color, (list, tuple)):
            flat = []
            for v in color:
                if hasattr(v, 'item'):
                    flat.append(v.item())  # numpy scalar to python
                elif isinstance(v, float):
                    flat.append(int(round(v)))
                elif isinstance(v, int):
                    flat.append(v)
                else:
                    flat.append(int(v))
        elif hasattr(color, 'item'):
            # Single numpy scalar — treat as grayscale
            v = int(color.item())
            return (v, v, v)
        elif isinstance(color, (int, float)):
            v = int(color)
            return (v, v, v)
        else:
            return fallback

        # Clamp all values to valid 0-255 range
        flat = [max(0, min(255, int(v))) for v in flat]

        # Normalize to exactly 3 elements (RGB)
        if len(flat) == 0:
            return fallback
        elif len(flat) == 1:
            return (flat[0], flat[0], flat[0])
        elif len(flat) == 2:
            return (flat[0], flat[1], 0)
        elif len(flat) == 3:
            return (flat[0], flat[1], flat[2])
        elif len(flat) >= 4:
            # Drop alpha — PIL ImageDraw needs RGB not RGBA
            # for fill color in most draw operations
            return (flat[0], flat[1], flat[2])

    except Exception:
        return fallback


def sanitize_color_with_alpha(
    color, alpha=255, fallback=(0, 0, 0, 255)
) -> tuple:
    """
    Same as sanitize_color but returns RGBA tuple
    for use with RGBA image compositing.
    """
    rgb = sanitize_color(color, fallback=(0, 0, 0))
    a = max(0, min(255, int(alpha)))
    return (rgb[0], rgb[1], rgb[2], a)


def rgb_to_hex(rgb: tuple) -> str:
    """
    Convert RGB tuple to hex color string.
    
    Args:
        rgb: RGB tuple (r, g, b)
    
    Returns:
        Hex color string like '#FF0000'
    """
    rgb = sanitize_color(rgb, fallback=(0, 0, 0))
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
