"""Line merging algorithm for grouping word-level OCR results into logical lines."""
import numpy as np


def merge_into_lines(blocks: list) -> list:
    """
    Groups individual word-level TextBlocks into logical line-level TextBlocks
    based on vertical overlap.
    
    Two blocks belong to the same line if their vertical ranges overlap
    significantly regardless of horizontal gap.
    """
    if not blocks:
        return []
    
    # Sort by vertical center, then horizontal position
    def vertical_center(b):
        return b.y + b.height / 2
    
    sorted_blocks = sorted(blocks, key=lambda b: (vertical_center(b), b.x))
    
    # Group blocks into lines using vertical overlap detection
    lines = []
    current_line = [sorted_blocks[0]]
    
    for block in sorted_blocks[1:]:
        if _belongs_to_same_line(block, current_line):
            current_line.append(block)
        else:
            current_line.sort(key=lambda b: b.x)
            lines.append(current_line)
            current_line = [block]
    
    # Don't forget the last line
    if current_line:
        current_line.sort(key=lambda b: b.x)
        lines.append(current_line)
    
    # Merge each line group into a single TextBlock
    merged_blocks = []
    for new_id, line_group in enumerate(lines):
        merged = _merge_line_group(line_group, new_id)
        merged_blocks.append(merged)
    
    return merged_blocks


def _belongs_to_same_line(block, current_line: list) -> bool:
    """
    Returns True if block is on the same visual line as blocks in current_line.
    
    Uses vertical overlap ratio - two blocks are on the same line if their
    vertical ranges overlap by more than 50% of the smaller block's height.
    """
    # Get the vertical span of the current line group
    line_y_top = min(b.y for b in current_line)
    line_y_bottom = max(b.y + b.height for b in current_line)
    line_height = line_y_bottom - line_y_top
    
    # Get this block's vertical span
    block_y_top = block.y
    block_y_bottom = block.y + block.height
    
    # Calculate vertical overlap
    overlap_top = max(line_y_top, block_y_top)
    overlap_bottom = min(line_y_bottom, block_y_bottom)
    overlap = max(0, overlap_bottom - overlap_top)
    
    # Overlap ratio relative to smaller height
    smaller_height = min(line_height, block.height)
    if smaller_height == 0:
        return False
    
    overlap_ratio = overlap / smaller_height
    
    # Threshold: 50% vertical overlap = same line
    return overlap_ratio >= 0.50


def _merge_line_group(line_group: list, new_id: int):
    """
    Merges a list of word-level TextBlocks that are on the same visual line
    into a single TextBlock.
    
    The merged block:
    - text: words joined with single space in left-to-right order
    - x, y: top-left corner of the combined bounding box
    - width: from leftmost x to rightmost x+width
    - height: from topmost y to bottommost y+height
    - conf: average confidence of all merged blocks
    - font_size_estimate: max of all individual estimates (tallest text)
    - block_id: new sequential id
    - constituent_blocks: original blocks stored for reference
    """
    from editor.text_editor import TextBlock
    
    # Bounding box that contains all blocks in the line
    x1 = min(b.x for b in line_group)
    y1 = min(b.y for b in line_group)
    x2 = max(b.x + b.width for b in line_group)
    y2 = max(b.y + b.height for b in line_group)
    
    # Join text left to right
    merged_text = " ".join(b.text for b in line_group)
    
    # Average confidence
    avg_conf = float(np.mean([b.conf for b in line_group]))
    
    # Use MAX font size (tallest text in the line)
    max_font = max(b.font_size_estimate for b in line_group)
    
    merged = TextBlock(
        text=merged_text,
        x=x1,
        y=y1,
        width=x2 - x1,
        height=y2 - y1,
        conf=avg_conf,
        font_size_estimate=max_font,
        block_id=new_id,
        constituent_blocks=line_group
    )
    
    return merged
