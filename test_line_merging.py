#!/usr/bin/env python3
"""Test script to verify line merging functionality."""

from editor.text_editor import TextBlock
from utils.line_merger import merge_into_lines


def test_line_merging():
    """Test that words on the same line are merged correctly."""
    
    print("=" * 60)
    print("LINE MERGING TEST")
    print("=" * 60)
    
    # Simulate EasyOCR detecting "January 1 to 31" as 4 separate words
    word_blocks = [
        TextBlock(
            text="January",
            x=50,
            y=120,
            width=80,
            height=22,
            conf=0.94,
            font_size_estimate=18,
            block_id=0
        ),
        TextBlock(
            text="1",
            x=138,
            y=122,
            width=12,
            height=20,
            conf=0.91,
            font_size_estimate=16,
            block_id=1
        ),
        TextBlock(
            text="to",
            x=158,
            y=121,
            width=20,
            height=20,
            conf=0.88,
            font_size_estimate=16,
            block_id=2
        ),
        TextBlock(
            text="31",
            x=186,
            y=120,
            width=24,
            height=22,
            conf=0.93,
            font_size_estimate=18,
            block_id=3
        )
    ]
    
    print("\nBEFORE MERGING (word-level blocks):")
    print("-" * 60)
    for block in word_blocks:
        print(f"  Block {block.block_id}: '{block.text}' at y={block.y}, h={block.height}, conf={block.conf:.2f}")
    
    # Merge into lines
    merged_blocks = merge_into_lines(word_blocks)
    
    print("\nAFTER MERGING (line-level blocks):")
    print("-" * 60)
    for block in merged_blocks:
        print(f"  Block {block.block_id}: '{block.text}'")
        print(f"    Position: x={block.x}, y={block.y}")
        print(f"    Size: w={block.width}, h={block.height}")
        print(f"    Confidence: {block.conf:.2f}")
        print(f"    Font size: {block.font_size_estimate}")
        print(f"    Constituent blocks: {len(block.constituent_blocks)}")
    
    # Verify results
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    assert len(merged_blocks) == 1, f"Expected 1 merged block, got {len(merged_blocks)}"
    merged = merged_blocks[0]
    
    assert merged.text == "January 1 to 31", f"Expected 'January 1 to 31', got '{merged.text}'"
    assert merged.x == 50, f"Expected x=50, got x={merged.x}"
    assert merged.y == 120, f"Expected y=120, got y={merged.y}"
    assert merged.width == 160, f"Expected width=160, got width={merged.width}"
    assert merged.height == 22, f"Expected height=22, got height={merged.height}"
    assert len(merged.constituent_blocks) == 4, f"Expected 4 constituent blocks, got {len(merged.constituent_blocks)}"
    
    print("✅ All assertions passed!")
    print("✅ Words on same line successfully merged into single block")
    print("✅ Bounding box correctly encompasses all words")
    print("✅ Text correctly joined with spaces")
    
    return True


def test_multiple_lines():
    """Test that words on different lines stay separate."""
    
    print("\n" + "=" * 60)
    print("MULTIPLE LINES TEST")
    print("=" * 60)
    
    # Simulate two separate lines
    word_blocks = [
        # Line 1: "Hello World"
        TextBlock(text="Hello", x=50, y=100, width=60, height=20, conf=0.95, font_size_estimate=16, block_id=0),
        TextBlock(text="World", x=120, y=102, width=60, height=18, conf=0.93, font_size_estimate=15, block_id=1),
        # Line 2: "Goodbye Friend" (y=150, clearly different line)
        TextBlock(text="Goodbye", x=50, y=150, width=80, height=22, conf=0.94, font_size_estimate=18, block_id=2),
        TextBlock(text="Friend", x=140, y=151, width=70, height=21, conf=0.92, font_size_estimate=17, block_id=3),
    ]
    
    print("\nBEFORE MERGING:")
    print("-" * 60)
    for block in word_blocks:
        print(f"  '{block.text}' at y={block.y}")
    
    merged_blocks = merge_into_lines(word_blocks)
    
    print("\nAFTER MERGING:")
    print("-" * 60)
    for block in merged_blocks:
        print(f"  Line {block.block_id}: '{block.text}' (y={block.y})")
    
    # Verify
    assert len(merged_blocks) == 2, f"Expected 2 lines, got {len(merged_blocks)}"
    assert merged_blocks[0].text == "Hello World", f"Line 1 should be 'Hello World', got '{merged_blocks[0].text}'"
    assert merged_blocks[1].text == "Goodbye Friend", f"Line 2 should be 'Goodbye Friend', got '{merged_blocks[1].text}'"
    
    print("\n✅ Multiple lines correctly kept separate")
    print("✅ Each line merged independently")
    
    return True


if __name__ == "__main__":
    try:
        test_line_merging()
        test_multiple_lines()
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe line merging fix is working correctly.")
        print("Words on the same visual line are now merged into single blocks.")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
