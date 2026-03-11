"""Toolbar UI component."""
import tkinter as tk
from tkinter import ttk
from typing import Callable


class Toolbar:
    """Toolbar with main action buttons."""
    
    def __init__(self, parent, upload_callback: Callable, save_callback: Callable,
                 undo_callback: Callable, redo_callback: Callable, export_callback: Callable = None):
        """Initialize toolbar with action callbacks."""
        self.frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        
        self.upload_btn = ttk.Button(self.frame, text="Upload Image", command=upload_callback)
        self.upload_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Separator(self.frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        self.undo_btn = ttk.Button(self.frame, text="↩ Undo", command=undo_callback, state=tk.DISABLED)
        self.undo_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.redo_btn = ttk.Button(self.frame, text="↪ Redo", command=redo_callback, state=tk.DISABLED)
        self.redo_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Separator(self.frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        self.save_btn = ttk.Button(self.frame, text="💾 Save As...", command=save_callback, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        if export_callback:
            self.export_btn = ttk.Button(self.frame, text="⬇️ Export to Desktop", command=export_callback, state=tk.DISABLED)
            self.export_btn.pack(side=tk.LEFT, padx=5, pady=5)
        else:
            self.export_btn = None
    
    def enable_editing(self) -> None:
        """Enable editing buttons."""
        self.save_btn.config(state=tk.NORMAL)
        if self.export_btn:
            self.export_btn.config(state=tk.NORMAL)
    
    def disable_editing(self) -> None:
        """Disable editing buttons."""
        self.save_btn.config(state=tk.DISABLED)
        if self.export_btn:
            self.export_btn.config(state=tk.DISABLED)
        self.undo_btn.config(state=tk.DISABLED)
        self.redo_btn.config(state=tk.DISABLED)
    
    def update_undo_redo(self, can_undo: bool, can_redo: bool) -> None:
        """Update undo/redo button states."""
        self.undo_btn.config(state=tk.NORMAL if can_undo else tk.DISABLED)
        self.redo_btn.config(state=tk.NORMAL if can_redo else tk.DISABLED)
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
