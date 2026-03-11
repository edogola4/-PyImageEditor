"""Sidebar UI component with editing controls."""
import tkinter as tk
from tkinter import ttk, colorchooser, simpledialog
from typing import Callable


class Sidebar:
    """Sidebar with all editing controls."""
    
    def __init__(self, parent, callbacks: dict):
        """Initialize sidebar with editing controls."""
        self.callbacks = callbacks
        self.shape_color = (0, 0, 0)
        self.text_color = (0, 0, 0)
        
        # Main scrollable frame
        canvas = tk.Canvas(parent, width=250)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        self.frame = ttk.Frame(canvas)
        
        self.frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._create_adjustments()
        self._create_transform()
        self._create_filters()
        self._create_shapes()
        self._create_text()
        
        self.disable_all()
    
    def _create_adjustments(self):
        """Create adjustment sliders."""
        frame = ttk.LabelFrame(self.frame, text="Adjustments", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.brightness_var = tk.IntVar(value=100)
        self.contrast_var = tk.IntVar(value=100)
        self.saturation_var = tk.IntVar(value=100)
        self.sharpness_var = tk.IntVar(value=100)
        
        for label, var in [("Brightness", self.brightness_var), ("Contrast", self.contrast_var),
                           ("Saturation", self.saturation_var), ("Sharpness", self.sharpness_var)]:
            ttk.Label(frame, text=label).pack(anchor=tk.W)
            ttk.Scale(frame, from_=0, to=200, variable=var, 
                     command=lambda v: self.callbacks['adjust']()).pack(fill=tk.X)
    
    def _create_transform(self):
        """Create transform controls."""
        frame = ttk.LabelFrame(self.frame, text="Transform", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(frame, text="Crop", command=self._crop_image).pack(fill=tk.X, pady=2)
        
        ttk.Button(frame, text="Flip Horizontal", 
                  command=lambda: self.callbacks['flip']('h')).pack(fill=tk.X, pady=2)
        ttk.Button(frame, text="Flip Vertical", 
                  command=lambda: self.callbacks['flip']('v')).pack(fill=tk.X, pady=2)
        
        rotate_frame = ttk.Frame(frame)
        rotate_frame.pack(fill=tk.X, pady=2)
        ttk.Label(rotate_frame, text="Rotate:").pack(side=tk.LEFT)
        self.rotate_var = tk.IntVar(value=0)
        ttk.Entry(rotate_frame, textvariable=self.rotate_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Button(rotate_frame, text="Apply", 
                  command=lambda: self.callbacks['rotate'](self.rotate_var.get())).pack(side=tk.LEFT)
        
        resize_frame = ttk.Frame(frame)
        resize_frame.pack(fill=tk.X, pady=2)
        ttk.Label(resize_frame, text="W:").pack(side=tk.LEFT)
        self.width_var = tk.IntVar(value=800)
        ttk.Entry(resize_frame, textvariable=self.width_var, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(resize_frame, text="H:").pack(side=tk.LEFT)
        self.height_var = tk.IntVar(value=600)
        ttk.Entry(resize_frame, textvariable=self.height_var, width=5).pack(side=tk.LEFT, padx=2)
        
        self.lock_aspect_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Lock Aspect", variable=self.lock_aspect_var).pack(anchor=tk.W)
        ttk.Button(frame, text="Resize", 
                  command=lambda: self.callbacks['resize'](
                      self.width_var.get(), self.height_var.get(), 
                      self.lock_aspect_var.get())).pack(fill=tk.X, pady=2)
    
    def _create_filters(self):
        """Create filter buttons."""
        frame = ttk.LabelFrame(self.frame, text="Filters", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        filters = ["Grayscale", "Sepia", "Blur", "Sharpen", "Edge Detect", "Emboss"]
        for f in filters:
            ttk.Button(frame, text=f, 
                      command=lambda filter_name=f: self.callbacks['filter'](filter_name)).pack(fill=tk.X, pady=2)
    
    def _create_shapes(self):
        """Create shape drawing controls."""
        frame = ttk.LabelFrame(self.frame, text="Shapes", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.shape_var = tk.StringVar(value="rectangle")
        for shape in ["rectangle", "circle", "line"]:
            ttk.Radiobutton(frame, text=shape.capitalize(), variable=self.shape_var, 
                           value=shape).pack(anchor=tk.W)
        
        ttk.Button(frame, text="Choose Color", command=self._choose_shape_color).pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text="Thickness:").pack(anchor=tk.W)
        self.thickness_var = tk.IntVar(value=3)
        ttk.Scale(frame, from_=1, to=20, variable=self.thickness_var).pack(fill=tk.X)
        
        ttk.Button(frame, text="Draw Shape", command=self._draw_shape).pack(fill=tk.X, pady=2)
    
    def _create_text(self):
        """Create text overlay controls."""
        frame = ttk.LabelFrame(self.frame, text="Text Overlay", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame, text="Font Size:").pack(anchor=tk.W)
        self.font_size_var = tk.IntVar(value=24)
        ttk.Scale(frame, from_=10, to=100, variable=self.font_size_var).pack(fill=tk.X)
        
        ttk.Button(frame, text="Choose Color", command=self._choose_text_color).pack(fill=tk.X, pady=2)
        ttk.Button(frame, text="Add Text", command=self._add_text).pack(fill=tk.X, pady=2)
    
    def _choose_shape_color(self):
        """Open color picker for shape color."""
        color = colorchooser.askcolor(title="Choose Shape Color")
        if color[0]:
            self.shape_color = tuple(int(c) for c in color[0])
    
    def _choose_text_color(self):
        """Open color picker for text color."""
        color = colorchooser.askcolor(title="Choose Text Color")
        if color[0]:
            self.text_color = tuple(int(c) for c in color[0])
    
    def _draw_shape(self):
        """Trigger shape drawing."""
        shape_type = self.shape_var.get()
        thickness = self.thickness_var.get()
        self.callbacks['shape'](shape_type, self.shape_color, thickness)
    
    def _add_text(self):
        """Trigger text overlay."""
        text = simpledialog.askstring("Add Text", "Enter text:")
        if text:
            self.callbacks['text'](text, self.font_size_var.get(), self.text_color)
    
    def _crop_image(self):
        """Trigger crop operation."""
        left = simpledialog.askinteger("Crop", "Left (X1):")
        if left is None: return
        top = simpledialog.askinteger("Crop", "Top (Y1):")
        if top is None: return
        right = simpledialog.askinteger("Crop", "Right (X2):")
        if right is None: return
        bottom = simpledialog.askinteger("Crop", "Bottom (Y2):")
        if bottom is None: return
        self.callbacks['crop'](left, top, right, bottom)
    
    def get_adjustment_values(self):
        """Get current adjustment slider values."""
        return {
            'brightness': self.brightness_var.get() / 100.0,
            'contrast': self.contrast_var.get() / 100.0,
            'saturation': self.saturation_var.get() / 100.0,
            'sharpness': self.sharpness_var.get() / 100.0
        }
    
    def reset_adjustments(self):
        """Reset all adjustment sliders to default."""
        self.brightness_var.set(100)
        self.contrast_var.set(100)
        self.saturation_var.set(100)
        self.sharpness_var.set(100)
    
    def update_resize_defaults(self, width: int, height: int):
        """Update resize input defaults."""
        self.width_var.set(width)
        self.height_var.set(height)
    
    def enable_all(self):
        """Enable all controls."""
        for child in self.frame.winfo_children():
            self._enable_widget(child)
    
    def disable_all(self):
        """Disable all controls."""
        for child in self.frame.winfo_children():
            self._disable_widget(child)
    
    def _enable_widget(self, widget):
        """Recursively enable widget and children."""
        try:
            widget.configure(state=tk.NORMAL)
        except:
            pass
        for child in widget.winfo_children():
            self._enable_widget(child)
    
    def _disable_widget(self, widget):
        """Recursively disable widget and children."""
        try:
            widget.configure(state=tk.DISABLED)
        except:
            pass
        for child in widget.winfo_children():
            self._disable_widget(child)
