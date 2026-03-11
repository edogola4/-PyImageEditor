"""Color utility functions for text replacement."""


def rgb_to_hex(rgb: tuple) -> str:
    """Convert RGB tuple to hex string."""
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def colors_are_similar(c1: tuple, c2: tuple, threshold=30) -> bool:
    """Check if two colors are similar within threshold."""
    return sum(abs(a-b) for a, b in zip(c1, c2)) < threshold


def get_contrasting_color(bg_color: tuple) -> tuple:
    """Get contrasting color (black or white) for given background."""
    luminance = 0.299*bg_color[0] + 0.587*bg_color[1] + 0.114*bg_color[2]
    return (0, 0, 0) if luminance > 128 else (255, 255, 255)
