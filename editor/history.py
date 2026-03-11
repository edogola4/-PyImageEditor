"""History manager for undo/redo functionality."""
from typing import Optional
from PIL import Image


class HistoryManager:
    """Manages undo/redo history with a maximum of 10 steps."""
    
    def __init__(self, max_history: int = 10):
        """Initialize history manager with maximum history size."""
        self.max_history = max_history
        self.history: list[Image.Image] = []
        self.redo_stack: list[Image.Image] = []
    
    def push(self, image: Image.Image) -> None:
        """Add current state to history and clear redo stack."""
        self.history.append(image.copy())
        if len(self.history) > self.max_history:
            self.history.pop(0)
        self.redo_stack.clear()
    
    def undo(self) -> Optional[Image.Image]:
        """Pop from history stack, push to redo stack, return previous image."""
        if len(self.history) < 2:
            return None
        current = self.history.pop()
        self.redo_stack.append(current)
        return self.history[-1].copy()
    
    def redo(self) -> Optional[Image.Image]:
        """Pop from redo stack, return next image."""
        if not self.redo_stack:
            return None
        next_image = self.redo_stack.pop()
        self.history.append(next_image)
        return next_image.copy()
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.history) > 1
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0
    
    def clear(self) -> None:
        """Clear all history."""
        self.history.clear()
        self.redo_stack.clear()
    
    def initialize(self, image: Image.Image) -> None:
        """Initialize history with first image."""
        self.clear()
        self.history.append(image.copy())
