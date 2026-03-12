"""Text selection, replacement, and deletion UI panel."""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from typing import Callable, Optional
import threading


class TextSelectPanel:
    """UI panel for text detection, selection, replacement, and deletion."""
    
    def __init__(self, parent: tk.Widget, callbacks: dict[str, Callable]):
        """Initialize text selection panel."""
        self.callbacks = callbacks
        self.detected_blocks = []
        self.selected_block = None
        self.auto_color = (0, 0, 0)
        self.custom_color = None
        self.detected_properties = None  # Store all detected properties
        
        self.frame = ttk.LabelFrame(parent, text="🔤 Text Select & Replace", padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._setup_ui()
        self.disable()
    
    def _setup_ui(self):
        """Setup UI components."""
        # Detect button
        self.detect_btn = ttk.Button(
            self.frame,
            text="🔍 Detect Text in Image",
            command=self._detect_text
        )
        self.detect_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Text blocks list
        ttk.Label(self.frame, text="Detected text blocks:").pack(anchor=tk.W)
        
        list_frame = tk.Frame(self.frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.blocks_listbox = tk.Listbox(
            list_frame,
            height=6,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9)
        )
        self.blocks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.blocks_listbox.yview)
        
        self.blocks_listbox.bind('<<ListboxSelect>>', self._on_block_select)
        self.blocks_listbox.bind('<Delete>', lambda e: self._delete_selected())
        self.blocks_listbox.bind('<Escape>', lambda e: self._clear_selection())
        
        # Selected block label
        self.selected_label = ttk.Label(self.frame, text="Selected: None", foreground="gray")
        self.selected_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Detected properties display
        self.properties_label = ttk.Label(
            self.frame, 
            text="",
            foreground="blue",
            font=("TkDefaultFont", 9)
        )
        self.properties_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Replacement text entry
        ttk.Label(self.frame, text="Replace with:").pack(anchor=tk.W)
        self.replace_entry = ttk.Entry(self.frame)
        self.replace_entry.pack(fill=tk.X, pady=(2, 10))
        self.replace_entry.bind('<Return>', lambda e: self._replace_selected())
        self.replace_entry.bind('<Escape>', lambda e: self._clear_selection())
        
        # Color controls
        color_frame = tk.Frame(self.frame)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(color_frame, text="Color:").pack(side=tk.LEFT)
        
        self.auto_color_btn = ttk.Button(
            color_frame,
            text="■ Auto-detect",
            command=self._use_auto_color,
            width=12
        )
        self.auto_color_btn.pack(side=tk.LEFT, padx=(5, 2))
        
        self.pick_color_btn = ttk.Button(
            color_frame,
            text="🎨 Pick Color",
            command=self._pick_color,
            width=12
        )
        self.pick_color_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        # Action buttons
        btn_frame1 = tk.Frame(self.frame)
        btn_frame1.pack(fill=tk.X, pady=(0, 5))
        
        self.replace_btn = ttk.Button(
            btn_frame1,
            text="✏️ Replace Selected",
            command=self._replace_selected
        )
        self.replace_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        self.delete_btn = ttk.Button(
            btn_frame1,
            text="🗑️ Delete Selected",
            command=self._delete_selected
        )
        self.delete_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        btn_frame2 = tk.Frame(self.frame)
        btn_frame2.pack(fill=tk.X, pady=(0, 10))
        
        self.replace_all_btn = ttk.Button(
            btn_frame2,
            text="🔄 Replace All",
            command=self._replace_all
        )
        self.replace_all_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        self.delete_all_btn = ttk.Button(
            btn_frame2,
            text="🗑️ Delete All",
            command=self._delete_all
        )
        self.delete_all_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Filter section
        filter_section = ttk.LabelFrame(self.frame, text="🎨 Filter Selected Text Region", padding=8)
        filter_section.pack(fill=tk.X, pady=(10, 0))
        
        # Filter dropdown
        ttk.Label(filter_section, text="Filter:").pack(anchor=tk.W)
        self.filter_var = tk.StringVar(value="Grayscale")
        self.filter_combo = ttk.Combobox(
            filter_section,
            textvariable=self.filter_var,
            state="readonly",
            values=[
                "Grayscale", "Sepia", "Blur", "Sharpen",
                "Brightness", "Contrast", "Saturation",
                "Edge Detection", "Emboss", "Invert",
                "Pixelate", "Highlight", "Redact", "White Redact"
            ]
        )
        self.filter_combo.pack(fill=tk.X, pady=(2, 10))
        self.filter_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # Intensity slider
        intensity_frame = tk.Frame(filter_section)
        intensity_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.intensity_label = ttk.Label(intensity_frame, text="Intensity:")
        self.intensity_label.pack(anchor=tk.W)
        
        slider_frame = tk.Frame(intensity_frame)
        slider_frame.pack(fill=tk.X)
        
        self.intensity_var = tk.DoubleVar(value=1.0)
        self.intensity_slider = ttk.Scale(
            slider_frame,
            from_=0.0,
            to=2.0,
            variable=self.intensity_var,
            orient=tk.HORIZONTAL
        )
        self.intensity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.intensity_value_label = ttk.Label(slider_frame, text="1.00", width=5)
        self.intensity_value_label.pack(side=tk.LEFT, padx=(5, 0))
        
        self.intensity_var.trace_add('write', self._update_intensity_label)
        
        # Filter buttons
        filter_btn_frame = tk.Frame(filter_section)
        filter_btn_frame.pack(fill=tk.X)
        
        self.apply_filter_btn = ttk.Button(
            filter_btn_frame,
            text="✅ Apply Filter",
            command=self._apply_filter
        )
        self.apply_filter_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        self.preview_filter_btn = ttk.Button(
            filter_btn_frame,
            text="👁 Preview",
            command=self._preview_filter
        )
        self.preview_filter_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Update intensity visibility
        self._on_filter_change(None)
    
    def _detect_text(self):
        """Detect text blocks in image."""
        self.frame.config(cursor="watch")
        self.detect_btn.config(state=tk.DISABLED, text="⏳ Detecting...")
        self.frame.update()
        
        def detect_thread():
            try:
                blocks = self.callbacks['detect']()
                self.frame.after(0, self._on_detection_complete, blocks)
            except Exception as error:
                self.frame.after(0, self._on_detection_error, str(error))
        
        threading.Thread(target=detect_thread, daemon=True).start()
    
    def _on_detection_complete(self, blocks):
        """Handle detection completion."""
        self.detected_blocks = blocks
        self.blocks_listbox.delete(0, tk.END)
        
        if not blocks:
            messagebox.showinfo(
                "No Text Detected",
                "No text was found in this image.\nTry increasing contrast first."
            )
        else:
            for block in blocks:
                # Truncate long text for display
                display_text = block.text
                if len(display_text) > 30:
                    display_text = display_text[:27] + "..."
                
                conf_pct = int(block.conf * 100)
                display = f"{block.block_id+1:2d} │ {display_text:30s} │ {conf_pct:3d}%"
                self.blocks_listbox.insert(tk.END, display)
            
            self.blocks_listbox.selection_set(0)
            self._on_block_select(None)
        
        self.detect_btn.config(state=tk.NORMAL, text="🔍 Detect Text in Image")
        self.frame.config(cursor="")
    
    def _on_detection_error(self, error_msg):
        """Handle detection error."""
        messagebox.showerror("Detection Error", f"Failed to detect text:\n{error_msg}")
        self.detect_btn.config(state=tk.NORMAL, text="🔍 Detect Text in Image")
        self.frame.config(cursor="")
    
    def _on_block_select(self, event):
        """Handle block selection."""
        selection = self.blocks_listbox.curselection()
        if not selection:
            self.selected_block = None
            self.selected_label.config(text="Selected: None", foreground="gray")
            self.properties_label.config(text="")
            self.callbacks['clear_highlight']()
            return
        
        idx = selection[0]
        self.selected_block = self.detected_blocks[idx]
        self.selected_label.config(
            text=f'Selected: "{self.selected_block.text}"',
            foreground="black"
        )
        
        # Extract ALL properties from original text
        self.detected_properties = self.callbacks['extract_properties'](self.selected_block)
        self.auto_color = self.detected_properties['color']
        self.custom_color = None  # Reset to auto mode
        
        # Display detected properties
        from utils.color_utils import rgb_to_hex
        color_hex = rgb_to_hex(self.auto_color)
        font_name = self.detected_properties['best_font_path'].split('/')[-1] if self.detected_properties['best_font_path'] != 'default' else 'Default'
        style_info = []
        if self.detected_properties['is_bold']:
            style_info.append('Bold')
        if self.detected_properties['is_italic']:
            style_info.append('Italic')
        if self.detected_properties['has_shadow']:
            style_info.append('Shadow')
        if self.detected_properties['has_outline']:
            style_info.append('Outline')
        
        style_str = ', '.join(style_info) if style_info else 'Regular'
        props_text = f"🔍 Detected: {font_name} {self.detected_properties['font_size']}pt | Color: {color_hex} | {style_str}"
        self.properties_label.config(text=props_text)
        
        # Highlight on canvas
        self.callbacks['highlight'](self.selected_block)
    
    def _clear_selection(self):
        """Clear block selection."""
        self.blocks_listbox.selection_clear(0, tk.END)
        self.selected_block = None
        self.detected_properties = None
        self.selected_label.config(text="Selected: None", foreground="gray")
        self.properties_label.config(text="")
        self.callbacks['clear_highlight']()
    
    def _use_auto_color(self):
        """Use auto-detected color."""
        self.custom_color = None
        if self.detected_properties:
            from utils.color_utils import rgb_to_hex
            color_hex = rgb_to_hex(self.auto_color)
            messagebox.showinfo("Auto Color", f"Using auto-detected color: {color_hex} RGB{self.auto_color}")
        else:
            messagebox.showinfo("Auto Color", "Select a text block first to detect color.")
    
    def _pick_color(self):
        """Pick custom color."""
        color = colorchooser.askcolor(title="Choose Text Color")
        if color[0]:
            self.custom_color = tuple(int(c) for c in color[0])
    
    def _get_current_color(self):
        """Get current color (custom or auto)."""
        # Return None if using auto-detected (let the backend use extracted properties)
        return self.custom_color
    
    def _replace_selected(self):
        """Replace selected text block."""
        if not self.selected_block:
            messagebox.showwarning("No Selection", "Please select a text block first.")
            return
        
        new_text = self.replace_entry.get()
        if not new_text:
            result = messagebox.askyesno(
                "Empty Replacement",
                "Replace with empty string? This will erase the text visually."
            )
            if not result:
                return
        
        try:
            # Store the index before replacement
            selection = self.blocks_listbox.curselection()
            if not selection:
                return
            idx = selection[0]
            
            # Use custom color if set, otherwise None (will use auto-detected)
            color = self.custom_color if self.custom_color else None
            self.callbacks['replace'](self.selected_block, new_text, color)
            
            # Force canvas refresh immediately
            self.callbacks['force_refresh']()
            
            # Update the block text in memory
            self.detected_blocks[idx].text = new_text
            
            # Update the listbox display immediately
            conf_pct = int(self.detected_blocks[idx].conf * 100)
            display = f"{self.detected_blocks[idx].block_id+1:2d} │ {new_text[:20]:20s} │ {conf_pct:3d}%"
            self.blocks_listbox.delete(idx)
            self.blocks_listbox.insert(idx, display)
            self.blocks_listbox.selection_set(idx)
            
            # Update selected label
            self.selected_label.config(
                text=f'Selected: "{new_text}"',
                foreground="black"
            )
            
            # Clear replacement entry
            self.replace_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Replace Error", f"Failed to replace text:\n{str(e)}")
    
    def _delete_selected(self):
        """Delete selected text block."""
        if not self.selected_block:
            messagebox.showwarning("No Selection", "Please select a text block first.")
            return
        
        result = messagebox.askyesno(
            "Delete Text",
            f"Delete '{self.selected_block.text}'?\nThis will remove the text from the image.",
            icon='warning'
        )
        
        if not result:
            return
        
        try:
            # Store the index before deletion
            selection = self.blocks_listbox.curselection()
            if not selection:
                return
            idx = selection[0]
            
            # Call delete callback
            self.callbacks['delete'](self.selected_block)
            
            # Force canvas refresh immediately
            self.callbacks['force_refresh']()
            
            # Remove from detected blocks list
            del self.detected_blocks[idx]
            
            # Remove from listbox
            self.blocks_listbox.delete(idx)
            
            # Clear selection
            self._clear_selection()
            
            # Select next item if available
            if self.detected_blocks:
                new_idx = min(idx, len(self.detected_blocks) - 1)
                self.blocks_listbox.selection_set(new_idx)
                self._on_block_select(None)
            
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete text:\n{str(e)}")
    
    def _replace_all(self):
        """Replace all matching text blocks."""
        if not self.selected_block:
            messagebox.showwarning("No Selection", "Please select a text block first.")
            return
        
        new_text = self.replace_entry.get()
        if not new_text:
            messagebox.showwarning("Empty Text", "Please enter replacement text.")
            return
        
        target_text = self.selected_block.text
        matching = [b for b in self.detected_blocks if b.text.lower() == target_text.lower()]
        
        if len(matching) <= 1:
            messagebox.showinfo("No Matches", f"Only one occurrence of '{target_text}' found.")
            return
        
        result = messagebox.askyesno(
            "Replace All",
            f"Replace all {len(matching)} occurrences of '{target_text}'?"
        )
        
        if not result:
            return
        
        try:
            # Use custom color if set, otherwise None (will use auto-detected)
            color = self.custom_color if self.custom_color else None
            self.callbacks['replace_all'](target_text, new_text, color)
            
            # Force canvas refresh immediately
            self.callbacks['force_refresh']()
            
            # Update all matching blocks in memory and listbox
            for i, block in enumerate(self.detected_blocks):
                if block.text.lower() == target_text.lower():
                    block.text = new_text
                    conf_pct = int(block.conf * 100)
                    display = f"{block.block_id+1:2d} │ {new_text[:20]:20s} │ {conf_pct:3d}%"
                    self.blocks_listbox.delete(i)
                    self.blocks_listbox.insert(i, display)
            
            # Update selected label if current selection was replaced
            if self.selected_block and self.selected_block.text.lower() == target_text.lower():
                self.selected_block.text = new_text
                self.selected_label.config(
                    text=f'Selected: "{new_text}"',
                    foreground="black"
                )
            
            # Clear replacement entry
            self.replace_entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", f"Replaced {len(matching)} occurrence(s) of '{target_text}'.")
            
        except Exception as e:
            messagebox.showerror("Replace Error", f"Failed to replace all:\n{str(e)}")
    
    def _delete_all(self):
        """Delete all detected text blocks."""
        if not self.detected_blocks:
            messagebox.showwarning("No Text", "No text blocks detected.")
            return
        
        result = messagebox.askyesno(
            "Delete All Text",
            f"Delete ALL {len(self.detected_blocks)} detected text blocks?\n"
            "This will remove all text from the image.",
            icon='warning'
        )
        
        if not result:
            return
        
        try:
            # Call delete_all callback
            self.callbacks['delete_all'](self.detected_blocks)
            
            # Clear list
            self.detected_blocks = []
            self.blocks_listbox.delete(0, tk.END)
            self._clear_selection()
            
            messagebox.showinfo("Success", "All text blocks deleted.")
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete all text:\n{str(e)}")
    
    def _on_filter_change(self, event):
        """Handle filter selection change."""
        filter_type = self.filter_var.get().lower()
        
        # Filters that use intensity
        intensity_filters = ['blur', 'sharpen', 'brightness', 'contrast', 'saturation', 'pixelate']
        
        if filter_type in intensity_filters:
            self.intensity_label.pack(anchor=tk.W)
            self.intensity_slider.config(state=tk.NORMAL)
            self.intensity_value_label.config(foreground='black')
        else:
            self.intensity_label.pack_forget()
            self.intensity_slider.config(state=tk.DISABLED)
            self.intensity_value_label.config(foreground='gray')
    
    def _update_intensity_label(self, *args):
        """Update intensity value label."""
        value = self.intensity_var.get()
        self.intensity_value_label.config(text=f"{value:.2f}")
    
    def _apply_filter(self):
        """Apply filter to selected text region."""
        if not self.selected_block:
            messagebox.showwarning("No Selection", "Please select a text block from the list first.")
            return
        
        filter_type = self.filter_var.get().lower()
        intensity = self.intensity_var.get()
        
        try:
            self.callbacks['apply_filter'](self.selected_block, filter_type, intensity)
            
            # Force canvas refresh immediately
            self.callbacks['force_refresh']()
        except ValueError as e:
            messagebox.showerror("Filter Error", str(e))
        except Exception as e:
            messagebox.showerror("Filter Error", f"Failed to apply filter:\n{str(e)}")
    
    def _preview_filter(self):
        """Preview filter on selected text region."""
        if not self.selected_block:
            messagebox.showwarning("No Selection", "Please select a text block from the list first.")
            return
        
        filter_type = self.filter_var.get()
        intensity = self.intensity_var.get()
        
        try:
            self.callbacks['preview_filter'](self.selected_block, filter_type, intensity)
        except ValueError as e:
            messagebox.showerror("Filter Error", str(e))
        except Exception as e:
            messagebox.showerror("Filter Error", f"Failed to preview filter:\n{str(e)}")
    
    def enable(self):
        """Enable all controls."""
        self.detect_btn.config(state=tk.NORMAL)
        self.blocks_listbox.config(state=tk.NORMAL)
        self.replace_entry.config(state=tk.NORMAL)
        self.auto_color_btn.config(state=tk.NORMAL)
        self.pick_color_btn.config(state=tk.NORMAL)
        self.replace_btn.config(state=tk.NORMAL)
        self.delete_btn.config(state=tk.NORMAL)
        self.replace_all_btn.config(state=tk.NORMAL)
        self.delete_all_btn.config(state=tk.NORMAL)
        self.filter_combo.config(state="readonly")
        self.apply_filter_btn.config(state=tk.NORMAL)
        self.preview_filter_btn.config(state=tk.NORMAL)
    
    def disable(self):
        """Disable all controls."""
        self.detect_btn.config(state=tk.DISABLED)
        self.blocks_listbox.config(state=tk.DISABLED)
        self.replace_entry.config(state=tk.DISABLED)
        self.auto_color_btn.config(state=tk.DISABLED)
        self.pick_color_btn.config(state=tk.DISABLED)
        self.replace_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)
        self.replace_all_btn.config(state=tk.DISABLED)
        self.delete_all_btn.config(state=tk.DISABLED)
        self.filter_combo.config(state=tk.DISABLED)
        self.apply_filter_btn.config(state=tk.DISABLED)
        self.preview_filter_btn.config(state=tk.DISABLED)
