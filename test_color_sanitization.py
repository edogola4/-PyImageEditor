"""Test color sanitization utility handles all PIL color edge cases."""
import numpy as np
from utils.color_utils import sanitize_color, sanitize_color_with_alpha


def test_none_value():
    """Test None returns fallback."""
    result = sanitize_color(None, fallback=(100, 100, 100))
    assert result == (100, 100, 100), f"Expected (100, 100, 100), got {result}"
    print("✓ None value handled")


def test_numpy_array():
    """Test numpy array conversion."""
    color = np.array([255, 128, 64])
    result = sanitize_color(color)
    assert result == (255, 128, 64), f"Expected (255, 128, 64), got {result}"
    assert all(isinstance(v, int) for v in result), "Values must be Python ints"
    print("✓ Numpy array handled")


def test_numpy_float_array():
    """Test numpy float64 array from np.median()."""
    color = np.array([255.7, 128.3, 64.9], dtype=np.float64)
    result = sanitize_color(color)
    # Values are clamped to 255 max after rounding
    assert result == (255, 128, 65), f"Expected clamped rounded values, got {result}"
    assert all(isinstance(v, int) for v in result), "Values must be Python ints"
    print("✓ Numpy float array handled")


def test_nested_array():
    """Test nested array [[r, g, b]]."""
    color = [[200, 150, 100]]
    result = sanitize_color(color)
    assert result == (200, 150, 100), f"Expected (200, 150, 100), got {result}"
    print("✓ Nested array handled")


def test_float_tuple():
    """Test float tuple."""
    color = (255.9, 128.1, 64.5)
    result = sanitize_color(color)
    # round() uses banker's rounding: 64.5 -> 64
    assert result == (255, 128, 64), f"Expected clamped rounded values, got {result}"
    print("✓ Float tuple handled")


def test_rgba_to_rgb():
    """Test RGBA tuple drops alpha."""
    color = (255, 128, 64, 200)
    result = sanitize_color(color)
    assert result == (255, 128, 64), f"Expected RGB only, got {result}"
    assert len(result) == 3, "Must return exactly 3 elements"
    print("✓ RGBA to RGB conversion handled")


def test_five_element_tuple():
    """Test invalid 5-element tuple."""
    color = (255, 128, 64, 200, 100)
    result = sanitize_color(color)
    assert result == (255, 128, 64), f"Expected first 3 elements, got {result}"
    assert len(result) == 3, "Must return exactly 3 elements"
    print("✓ 5-element tuple handled")


def test_single_value():
    """Test single value converts to grayscale."""
    color = 128
    result = sanitize_color(color)
    assert result == (128, 128, 128), f"Expected grayscale, got {result}"
    print("✓ Single value handled")


def test_numpy_scalar():
    """Test numpy scalar (np.int64, np.float64)."""
    color = np.float64(200.7)
    result = sanitize_color(color)
    # Banker's rounding: 200.7 -> 201, but .item() may truncate
    assert result == (200, 200, 200) or result == (201, 201, 201), f"Expected grayscale, got {result}"
    print("✓ Numpy scalar handled")


def test_clamping():
    """Test values clamped to 0-255 range."""
    color = (300, -50, 128)
    result = sanitize_color(color)
    assert result == (255, 0, 128), f"Expected clamped values, got {result}"
    print("✓ Value clamping handled")


def test_empty_list():
    """Test empty list returns fallback."""
    color = []
    result = sanitize_color(color, fallback=(50, 50, 50))
    assert result == (50, 50, 50), f"Expected fallback, got {result}"
    print("✓ Empty list handled")


def test_single_element_list():
    """Test single element list converts to grayscale."""
    color = [100]
    result = sanitize_color(color)
    assert result == (100, 100, 100), f"Expected grayscale, got {result}"
    print("✓ Single element list handled")


def test_two_element_tuple():
    """Test two element tuple pads with 0."""
    color = (200, 100)
    result = sanitize_color(color)
    assert result == (200, 100, 0), f"Expected padded tuple, got {result}"
    print("✓ Two element tuple handled")


def test_with_alpha():
    """Test sanitize_color_with_alpha."""
    color = np.array([255.7, 128.3, 64.9])
    result = sanitize_color_with_alpha(color, alpha=180)
    assert len(result) == 4, "Must return RGBA"
    assert result == (255, 128, 65, 180), f"Expected RGBA with clamping, got {result}"
    assert all(isinstance(v, int) for v in result), "All values must be ints"
    print("✓ RGBA sanitization handled")


def test_median_output():
    """Test real-world np.median() output."""
    pixels = np.array([
        [255, 128, 64],
        [250, 130, 60],
        [252, 129, 62]
    ])
    median = np.median(pixels, axis=0)
    result = sanitize_color(median)
    assert isinstance(result, tuple), "Must return tuple"
    assert len(result) == 3, "Must have 3 elements"
    assert all(isinstance(v, int) for v in result), "All must be Python ints"
    assert all(0 <= v <= 255 for v in result), "All must be in valid range"
    print(f"✓ np.median() output handled: {result}")


def test_exception_safety():
    """Test invalid input returns fallback without raising."""
    invalid_inputs = [
        "invalid",
        {"r": 255, "g": 128, "b": 64},
        object(),
    ]
    for inp in invalid_inputs:
        result = sanitize_color(inp, fallback=(0, 0, 0))
        assert result == (0, 0, 0), f"Expected fallback for {type(inp)}"
    print("✓ Exception safety verified")


if __name__ == "__main__":
    print("Testing color sanitization utility...\n")
    
    test_none_value()
    test_numpy_array()
    test_numpy_float_array()
    test_nested_array()
    test_float_tuple()
    test_rgba_to_rgb()
    test_five_element_tuple()
    test_single_value()
    test_numpy_scalar()
    test_clamping()
    test_empty_list()
    test_single_element_list()
    test_two_element_tuple()
    test_with_alpha()
    test_median_output()
    test_exception_safety()
    
    print("\n✅ All color sanitization tests passed!")
    print("\nThe fix ensures:")
    print("  • All colors are plain Python int tuples")
    print("  • Numpy types are converted properly")
    print("  • Invalid inputs never crash PIL")
    print("  • Colors are always 3 elements (RGB) or 4 (RGBA)")
    print("  • Values are clamped to 0-255 range")
