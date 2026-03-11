"""Canvas UI component for image preview."""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from typing import Optional


class ImageCanvas:
    """Display original and edited images side by side."""
    
    def __init__(self, parent):
        """Initialize canvas."""
        self.frame = ttk.Frame(parent)
        
        # Labels
        label_frame = ttk.Frame(self.frame)
        label_frame.pack(fill=tk.X)
        ttk.Label(label_frame, text="Original", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, expand=True)
        ttk.Label(label_frame, text="Edited", font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, expand=True)
        
        # Canvas
        self.canvas = tk.Canvas(self.frame, bg='#d0d0d0')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', self._on_resize)
        
        self.original_photo = None
        self.edited_photo = None
        self.original_image = None
        self.edited_image = None
        self.highlight_rect = None
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
    
    def _on_resize(self, event):
        """Handle canvas resize event."""
        if self.original_image:
            self.update_images(self.original_image, self.edited_image)
    
    def update_images(self, original: Optional[Image.Image], 
                     edited: Optional[Image.Image]) -> None:
        """Update canvas with original and edited images."""
        self.canvas.delete("all")
        self.highlight_rect = None
        
        if original is None:
            return
        
        self.original_image = original
        self.edited_image = edited
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            width, height = 1000, 600
        
        half_width = width // 2
        
        # Display original
        orig_resized = self._resize_to_fit(original, half_width - 20, height - 20)
        self.original_photo = ImageTk.PhotoImage(orig_resized)
        x_orig = (half_width - orig_resized.width) // 2
        y_orig = (height - orig_resized.height) // 2
        self.canvas.create_image(x_orig, y_orig, anchor=tk.NW, image=self.original_photo)
        
        # Display edited
        if edited:
            edit_resized = self._resize_to_fit(edited, half_width - 20, height - 20)
            self.edited_photo = ImageTk.PhotoImage(edit_resized)
            x_edit = half_width + (half_width - edit_resized.width) // 2
            y_edit = (height - edit_resized.height) // 2
            self.canvas.create_image(x_edit, y_edit, anchor=tk.NW, image=self.edited_photo)
            
            self.scale_factor = edit_resized.width / edited.width
            self.offset_x = x_edit
            self.offset_y = y_edit
        
        # Divider line
        self.canvas.create_line(half_width, 0, half_width, height, fill='black', width=2)
    
    def _resize_to_fit(self, image: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """Resize image to fit within max dimensions while preserving aspect ratio."""
        img_copy = image.copy()
        img_copy.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        return img_copy
    
    def highlight_text_block(self, block):
        """Highlight a text block on the edited side of canvas."""
        if self.highlight_rect:
            self.canvas.delete(self.highlight_rect)
        
        if not self.edited_image or self.scale_factor == 0:
            return
        
        x1 = int(block.x * self.scale_factor) + self.offset_x
        y1 = int(block.y * self.scale_factor) + self.offset_y
        x2 = int((block.x + block.width) * self.scale_factor) + self.offset_x
        y2 = int((block.y + block.height) * self.scale_factor) + self.offset_y
        
        self.highlight_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='yellow',
            width=2,
            dash=(4, 2)
        )
    
    def clear_highlight(self):
        """Clear text block highlight."""
        if self.highlight_rect:
            self.canvas.delete(self.highlight_rect)
            self.highlight_rect = None
    
    def highlight_text_block(self, block):
        """Highlight a text block on the edited side of canvas."""
        if self.highlight_rect:
            self.canvas.delete(self.highlight_rect)
        
        if not self.edited_image or self.scale_factor == 0:
            return
        
        x1 = int(block.x * self.scale_factor) + self.offset_x
        y1 = int(block.y * self.scale_factor) + self.offset_y
        x2 = int((block.x + block.width) * self.scale_factor) + self.offset_x
        y2 = int((block.y + block.height) * self.scale_factor) + self.offset_y
        
        self.highlight_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='yellow',
            width=2,
            dash=(4, 2)
        )
    
    def clear_highlight(self):
        """Clear text block highlight."""
        if self.highlight_rect:
            self.canvas.delete(self.highlight_rect)
            self.highlight_rect = None
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
