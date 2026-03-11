"""Main application window and logic."""
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image
from typing import Optional

from ui.toolbar import Toolbar
from ui.sidebar import Sidebar
from ui.canvas import ImageCanvas
from ui.metadata_panel import MetadataPanel
from ui.text_select_panel import TextSelectPanel
from editor.history import HistoryManager
from editor import image_ops, filters, shapes
from editor.text_overlay import add_text, detect_and_match_font
from editor.text_editor import (
    detect_all_text, detect_text_color
)

# Try to import photorealistic functions, fall back to basic if not available
try:
    from editor.inpainting import (
        professional_replace_text, professional_delete_text
    )
    PHOTOREALISTIC_AVAILABLE = True
except ImportError:
    from editor.text_editor import (
        replace_text_in_image as professional_replace_text,
        delete_text_region as professional_delete_text
    )
    PHOTOREALISTIC_AVAILABLE = False
    print("Note: Running without photorealistic features (opencv-python not installed)")
from utils.file_handler import open_image, save_image


class ImageEditorApp:
    """Main image editor application."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the application."""
        self.root = root
        self.root.title("PyImageEditor")
        self.root.geometry("1400x800")
        
        self.original_image: Optional[Image.Image] = None
        self.current_image: Optional[Image.Image] = None
        self.base_image: Optional[Image.Image] = None
        self.metadata: Optional[dict] = None
        self.history = HistoryManager()
        self.matched_font: Optional[str] = None
        
        self.original_filename = None
        self.original_filepath = None
        self.original_format = None
        
        self._setup_ui()
        self._bind_shortcuts()
    
    def _setup_ui(self):
        """Setup UI components."""
        # Toolbar
        self.toolbar = Toolbar(
            self.root,
            upload_callback=self.upload_image,
            save_callback=self.save_image,
            undo_callback=self.undo,
            redo_callback=self.redo,
            export_callback=self.export_to_desktop
        )
        self.toolbar.pack(fill=tk.X)
        
        # Main content area
        content = tk.Frame(self.root)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        sidebar_frame = tk.Frame(content, width=250)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        callbacks = {
            'adjust': self.apply_adjustments,
            'crop': self.crop_image,
            'flip': self.flip_image,
            'rotate': self.rotate_image,
            'resize': self.resize_image,
            'filter': self.apply_filter,
            'shape': self.draw_shape,
            'text': self.add_text_overlay
        }
        self.sidebar = Sidebar(sidebar_frame, callbacks)
        
        # Text selection panel
        text_callbacks = {
            'detect': self.detect_text_blocks,
            'highlight': self.highlight_text_block,
            'clear_highlight': self.clear_text_highlight,
            'detect_color': self.detect_block_color,
            'extract_properties': self.extract_text_properties,
            'replace': self.replace_text_block,
            'replace_all': self.replace_all_text,
            'delete': self.delete_text_block,
            'delete_all': self.delete_all_text
        }
        self.text_panel = TextSelectPanel(sidebar_frame, text_callbacks)
        
        # Canvas and metadata
        right_frame = tk.Frame(content)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = ImageCanvas(right_frame)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.metadata_panel = MetadataPanel(right_frame)
        self.metadata_panel.pack(fill=tk.X)
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-f>', lambda e: self._trigger_text_detection())
        self.root.bind('<Control-s>', lambda e: self.save_image())
        self.root.bind('<Control-e>', lambda e: self.export_to_desktop())
    
    def _trigger_text_detection(self):
        """Trigger text detection via Ctrl+F."""
        if self.current_image:
            self.text_panel._detect_text()
    
    def upload_image(self):
        """Open file dialog and load image."""
        filetypes = [
            ("All Images", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.gif"),
            ("JPEG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("WEBP", "*.webp"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tiff"),
            ("GIF", "*.gif")
        ]
        
        filepath = filedialog.askopenfilename(title="Select Image", filetypes=filetypes)
        if not filepath:
            return
        
        try:
            img, metadata = open_image(filepath)
            self.original_image = img
            self.current_image = img.copy()
            self.base_image = img.copy()
            self.metadata = metadata
            self.original_filename = filepath.split('/')[-1]
            self.original_filepath = filepath
            self.original_format = img.format or 'PNG'
            
            self.history.initialize(img)
            self.sidebar.reset_adjustments()
            self.sidebar.update_resize_defaults(img.width, img.height)
            self.sidebar.enable_all()
            self.text_panel.enable()
            self.toolbar.enable_editing()
            
            # Detect font
            self.matched_font = detect_and_match_font(img)
            
            self.metadata_panel.update(metadata)
            self.update_canvas()
            self.update_undo_redo_buttons()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def save_image(self):
        """Save current image to file."""
        if self.current_image is None:
            return
        
        default_ext = f".{self.original_format.lower()}" if self.original_format else ".png"
        initial_file = f"edited_{self.original_filename}" if self.original_filename else "edited_image"
        
        filetypes = [
            ("PNG Image", "*.png"),
            ("JPEG Image", "*.jpg"),
            ("WEBP Image", "*.webp"),
            ("BMP Image", "*.bmp"),
            ("TIFF Image", "*.tiff")
        ]
        
        filepath = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=default_ext,
            initialfile=initial_file,
            filetypes=filetypes
        )
        
        if not filepath:
            return
        
        try:
            dpi = self.metadata.get('dpi', (72, 72)) if self.metadata else (72, 72)
            save_image(self.current_image, filepath, dpi)
            messagebox.showinfo("Saved", f"Image saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def export_to_desktop(self):
        """Quick export to Desktop with auto-generated filename."""
        if self.current_image is None:
            return
        
        import os
        from datetime import datetime
        
        desktop = os.path.expanduser("~/Desktop")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        base_name = self.original_filename.rsplit('.', 1)[0] if self.original_filename else "image"
        ext = self.original_format.lower() if self.original_format else "png"
        filename = f"{base_name}_edited_{timestamp}.{ext}"
        filepath = os.path.join(desktop, filename)
        
        try:
            dpi = self.metadata.get('dpi', (72, 72)) if self.metadata else (72, 72)
            save_image(self.current_image, filepath, dpi)
            messagebox.showinfo("Exported", f"Saved to Desktop:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def apply_adjustments(self):
        """Apply all adjustment sliders to base image."""
        if self.base_image is None:
            return
        
        values = self.sidebar.get_adjustment_values()
        img = self.base_image.copy()
        
        img = image_ops.brightness(img, values['brightness'])
        img = image_ops.contrast(img, values['contrast'])
        img = image_ops.saturation(img, values['saturation'])
        img = image_ops.sharpness(img, values['sharpness'])
        
        self.current_image = img
        self.update_canvas()
    
    def crop_image(self, left: int, top: int, right: int, bottom: int):
        """Crop image to specified coordinates."""
        if self.current_image is None:
            return
        
        try:
            img = image_ops.crop(self.current_image, left, top, right, bottom)
            self.commit_change(img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to crop: {str(e)}")
    
    def flip_image(self, direction: str):
        """Flip image horizontally or vertically."""
        if self.current_image is None:
            return
        
        if direction == 'h':
            img = image_ops.flip_horizontal(self.current_image)
        else:
            img = image_ops.flip_vertical(self.current_image)
        
        self.commit_change(img)
    
    def rotate_image(self, degrees: int):
        """Rotate image by specified degrees."""
        if self.current_image is None:
            return
        
        try:
            img = image_ops.rotate(self.current_image, degrees)
            self.commit_change(img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rotate: {str(e)}")
    
    def resize_image(self, width: int, height: int, lock_aspect: bool):
        """Resize image to specified dimensions."""
        if self.current_image is None:
            return
        
        try:
            img = self.current_image.copy()
            img = image_ops.resize(img, width, height, lock_aspect)
            self.commit_change(img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to resize: {str(e)}")
    
    def apply_filter(self, filter_name: str):
        """Apply selected filter to image."""
        if self.current_image is None:
            return
        
        try:
            filter_map = {
                "Grayscale": filters.to_grayscale,
                "Sepia": filters.to_sepia,
                "Blur": filters.apply_blur,
                "Sharpen": filters.apply_sharpen,
                "Edge Detect": filters.edge_detection,
                "Emboss": filters.emboss
            }
            
            img = filter_map[filter_name](self.current_image)
            self.commit_change(img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filter: {str(e)}")
    
    def draw_shape(self, shape_type: str, color: tuple, thickness: int):
        """Draw shape on image."""
        if self.current_image is None:
            return
        
        try:
            w, h = self.current_image.size
            
            if shape_type == "rectangle":
                x1 = simpledialog.askinteger("Rectangle", f"X1 (0-{w}):", minvalue=0, maxvalue=w)
                if x1 is None: return
                y1 = simpledialog.askinteger("Rectangle", f"Y1 (0-{h}):", minvalue=0, maxvalue=h)
                if y1 is None: return
                x2 = simpledialog.askinteger("Rectangle", f"X2 (0-{w}):", minvalue=0, maxvalue=w)
                if x2 is None: return
                y2 = simpledialog.askinteger("Rectangle", f"Y2 (0-{h}):", minvalue=0, maxvalue=h)
                if y2 is None: return
                img = shapes.draw_rectangle(self.current_image, x1, y1, x2, y2, color, thickness)
            
            elif shape_type == "circle":
                cx = simpledialog.askinteger("Circle", f"Center X (0-{w}):", minvalue=0, maxvalue=w)
                if cx is None: return
                cy = simpledialog.askinteger("Circle", f"Center Y (0-{h}):", minvalue=0, maxvalue=h)
                if cy is None: return
                radius = simpledialog.askinteger("Circle", "Radius:", minvalue=1)
                if radius is None: return
                img = shapes.draw_circle(self.current_image, cx, cy, radius, color, thickness)
            
            else:  # line
                x1 = simpledialog.askinteger("Line", f"X1 (0-{w}):", minvalue=0, maxvalue=w)
                if x1 is None: return
                y1 = simpledialog.askinteger("Line", f"Y1 (0-{h}):", minvalue=0, maxvalue=h)
                if y1 is None: return
                x2 = simpledialog.askinteger("Line", f"X2 (0-{w}):", minvalue=0, maxvalue=w)
                if x2 is None: return
                y2 = simpledialog.askinteger("Line", f"Y2 (0-{h}):", minvalue=0, maxvalue=h)
                if y2 is None: return
                img = shapes.draw_line(self.current_image, x1, y1, x2, y2, color, thickness)
            
            self.commit_change(img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to draw shape: {str(e)}")
    
    def add_text_overlay(self, text: str, font_size: int, color: tuple):
        """Add text overlay to image."""
        if self.current_image is None:
            return
        
        try:
            w, h = self.current_image.size
            x = simpledialog.askinteger("Text Position", f"X (0-{w}):", minvalue=0, maxvalue=w)
            if x is None: return
            y = simpledialog.askinteger("Text Position", f"Y (0-{h}):", minvalue=0, maxvalue=h)
            if y is None: return
            
            img = add_text(self.current_image, text, x, y, self.matched_font, font_size, color)
            self.commit_change(img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add text: {str(e)}")
    
    def detect_text_blocks(self):
        """Detect all text blocks in current image."""
        if self.current_image is None:
            return []
        
        return detect_all_text(self.current_image)
    
    def highlight_text_block(self, block):
        """Highlight a text block on canvas."""
        self.canvas.highlight_text_block(block)
    
    def clear_text_highlight(self):
        """Clear text block highlight."""
        self.canvas.clear_highlight()
    
    def extract_text_properties(self, block):
        """Extract all properties from text block."""
        if self.current_image is None:
            return {}
        
        from editor.text_editor import extract_text_properties
        return extract_text_properties(self.current_image, block)
    
    def detect_block_color(self, block):
        """Detect color of text block."""
        if self.current_image is None:
            return (0, 0, 0)
        
        return detect_text_color(self.current_image, block)
    
    def replace_text_block(self, block, new_text: str, color: tuple = None):
        """Replace a single text block with photorealistic rendering."""
        if self.current_image is None:
            return
        
        try:
            # Pass color as None if not manually set (will use auto-detected)
            img = professional_replace_text(
                self.current_image,
                block,
                new_text,
                self.matched_font,
                color  # None = use auto-detected properties
            )
            self.commit_change(img)
        except Exception as e:
            raise e
    
    def replace_all_text(self, target_text: str, new_text: str, color: tuple = None):
        """Replace all occurrences of target text with photorealistic rendering."""
        if self.current_image is None:
            return
        
        try:
            blocks = detect_all_text(self.current_image)
            img = self.current_image.copy()
            
            for block in blocks:
                if block.text.lower() == target_text.lower():
                    # Pass color as None if not manually set (will use auto-detected)
                    img = professional_replace_text(img, block, new_text, self.matched_font, color)
            
            self.commit_change(img)
        except Exception as e:
            raise e
    
    def delete_text_block(self, block):
        """Delete a single text block with photorealistic inpainting."""
        if self.current_image is None:
            return
        
        try:
            img = professional_delete_text(self.current_image, block)
            self.commit_change(img)
        except Exception as e:
            raise e
    
    def delete_all_text(self, blocks: list):
        """Delete all text blocks with photorealistic inpainting."""
        if self.current_image is None:
            return
        
        try:
            img = self.current_image.copy()
            for block in blocks:
                img = professional_delete_text(img, block)
            self.commit_change(img)
        except Exception as e:
            raise e
    
    def commit_change(self, new_image: Image.Image):
        """Commit change to history and update display."""
        self.history.push(new_image)
        self.current_image = new_image
        self.base_image = new_image.copy()
        self.sidebar.reset_adjustments()
        self.update_canvas()
        self.update_undo_redo_buttons()
    
    def undo(self):
        """Undo last change."""
        img = self.history.undo()
        if img:
            self.current_image = img
            self.base_image = img.copy()
            self.sidebar.reset_adjustments()
            self.update_canvas()
            self.update_undo_redo_buttons()
    
    def redo(self):
        """Redo last undone change."""
        img = self.history.redo()
        if img:
            self.current_image = img
            self.base_image = img.copy()
            self.sidebar.reset_adjustments()
            self.update_canvas()
            self.update_undo_redo_buttons()
    
    def update_canvas(self):
        """Update canvas with current images."""
        self.canvas.update_images(self.original_image, self.current_image)
    
    def update_undo_redo_buttons(self):
        """Update undo/redo button states."""
        self.toolbar.update_undo_redo(self.history.can_undo(), self.history.can_redo())
    
    def run(self):
        """Start the application."""
        self.root.mainloop()
