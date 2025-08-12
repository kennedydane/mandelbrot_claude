#!/usr/bin/env python3
"""
Quick fix version of GUI using static texture from file approach.
"""

import sys
from pathlib import Path
import dearpygui.dearpygui as dpg
import tempfile
import os

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mandelbrot_core import mandelbrot_array
from color_mapping import iterations_to_rgb_array, get_available_palettes
from coordinate_transforms import ViewBounds
from PIL import Image
from logger_config import setup_logging


class QuickFixMandelbrotGUI:
    """Quick fix GUI using file-based textures."""
    
    def __init__(self, width=500, height=400):
        self.width = width
        self.height = height
        self.view_bounds = ViewBounds(-2.5, 1.0, -1.25, 1.25, width, height)
        self.max_iterations = 100
        self.palette = 'default'
        self.temp_file = None
        
    def create_mandelbrot_image_file(self):
        """Create Mandelbrot image and save to temporary file."""
        print("Calculating Mandelbrot image...")
        
        # Calculate
        iterations = mandelbrot_array(
            self.width, self.height,
            self.view_bounds.x_min, self.view_bounds.x_max,
            self.view_bounds.y_min, self.view_bounds.y_max,
            self.max_iterations
        )
        
        # Convert to RGB
        rgb_image = iterations_to_rgb_array(iterations, self.max_iterations, self.palette)
        
        # Save to temporary file
        if self.temp_file:
            os.unlink(self.temp_file)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            self.temp_file = f.name
            
        pil_image = Image.fromarray(rgb_image, 'RGB')
        pil_image.save(self.temp_file)
        
        print(f"Saved image to: {self.temp_file}")
        return self.temp_file
    
    def run(self):
        """Run the GUI."""
        setup_logging(debug=True)
        
        dpg.create_context()
        
        # Generate initial image
        image_file = self.create_mandelbrot_image_file()
        
        # Load texture from file
        width, height, channels, data = dpg.load_image(image_file)
        print(f"Loaded image: {width}x{height}, {channels} channels")
        
        with dpg.texture_registry():
            texture_id = dpg.add_static_texture(width, height, data, tag="mandelbrot_tex")
            
        # Create GUI
        with dpg.window(label="Mandelbrot Visualizer", width=self.width+100, height=self.height+100, tag="main"):
            dpg.add_text("Mandelbrot Set:")
            dpg.add_image("mandelbrot_tex", width=width, height=height)
            
            dpg.add_separator()
            
            dpg.add_slider_int(
                label="Max Iterations", 
                default_value=self.max_iterations,
                min_value=50, max_value=300,
                callback=self.on_iterations_changed
            )
            
            palettes = get_available_palettes()
            dpg.add_combo(
                label="Palette",
                items=palettes,
                default_value=self.palette,
                callback=self.on_palette_changed
            )
            
            dpg.add_button(label="Render", callback=self.render_new_image)
            dpg.add_button(label="Reset View", callback=self.reset_view)
        
        # Show
        dpg.create_viewport(title="Fixed Mandelbrot GUI", width=self.width+150, height=self.height+150)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main", True)
        
        print("GUI started - you should see the Mandelbrot set!")
        dpg.start_dearpygui()
        
        # Cleanup
        if self.temp_file:
            os.unlink(self.temp_file)
        dpg.destroy_context()
    
    def on_iterations_changed(self, sender, value):
        self.max_iterations = value
        
    def on_palette_changed(self, sender, value):
        self.palette = value
        
    def render_new_image(self):
        """Render new image and update display."""
        print("Rendering new image...")
        
        # Create new image
        image_file = self.create_mandelbrot_image_file()
        
        # Load new texture
        width, height, channels, data = dpg.load_image(image_file)
        
        # Delete old texture
        if dpg.does_item_exist("mandelbrot_tex"):
            dpg.delete_item("mandelbrot_tex")
            
        # Create new texture
        texture_id = dpg.add_static_texture(width, height, data, tag="mandelbrot_tex", parent=dpg.get_item_parent("mandelbrot_tex"))
        
        print("Image updated!")
    
    def reset_view(self):
        """Reset to default view."""
        self.view_bounds = ViewBounds(-2.5, 1.0, -1.25, 1.25, self.width, self.height)
        self.render_new_image()


if __name__ == "__main__":
    gui = QuickFixMandelbrotGUI(400, 300)
    gui.run()