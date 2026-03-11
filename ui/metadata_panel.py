"""Metadata panel UI component."""
import tkinter as tk
from tkinter import ttk
from utils.file_handler import format_file_size


class MetadataPanel:
    """Display image metadata information."""
    
    def __init__(self, parent):
        """Initialize metadata panel."""
        self.frame = ttk.Frame(parent, relief=tk.RIDGE, borderwidth=2)
        self.label = ttk.Label(self.frame, text="No image loaded", 
                               font=('Arial', 10), anchor=tk.W)
        self.label.pack(padx=10, pady=5, fill=tk.X)
    
    def update(self, metadata: dict) -> None:
        """Update metadata display."""
        text = (f"{metadata['filename']} | "
                f"{metadata['width']}x{metadata['height']} | "
                f"{metadata['format']} | "
                f"{format_file_size(metadata['file_size'])}")
        self.label.config(text=text)
    
    def clear(self) -> None:
        """Clear metadata display."""
        self.label.config(text="No image loaded")
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
