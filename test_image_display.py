#!/usr/bin/env python3
"""
Test script to isolate image display issues.
"""

import dearpygui.dearpygui as dpg
import numpy as np
import sys
from pathlib import Path

# Add src directory for logging
sys.path.insert(0, str(Path(__file__).parent / "src"))

from logger_config import setup_logging
from mandelbrot_core import mandelbrot_array
from color_mapping import iterations_to_rgb_array


def test_image_display():
    """Test image display with a simple approach."""
    setup_logging(debug=True)
    
    print("Creating Dear PyGUI context...")
    dpg.create_context()
    
    # Calculate a small Mandelbrot image
    print("Calculating Mandelbrot image...")
    width, height = 200, 150
    iterations = mandelbrot_array(width, height, -2.5, 1.0, -1.25, 1.25, 50)
    rgb_image = iterations_to_rgb_array(iterations, 50, 'default')
    
    print(f"Image shape: {rgb_image.shape}, dtype: {rgb_image.dtype}")
    print(f"Image range: {rgb_image.min()} to {rgb_image.max()}")
    
    # Create texture registry
    with dpg.texture_registry():
        # Convert to float and add alpha
        float_image = rgb_image.astype(np.float32) / 255.0
        alpha = np.ones((height, width, 1), dtype=np.float32)
        rgba_image = np.concatenate([float_image, alpha], axis=2)
        flat_data = rgba_image.flatten().tolist()
        
        print(f"Texture data length: {len(flat_data)}, expected: {width * height * 4}")
        
        # Create texture
        texture_id = dpg.add_raw_texture(
            width=width,
            height=height,
            default_value=flat_data,
            format=dpg.mvFormat_Float_rgba,
            tag="test_texture"
        )
        
        print(f"Created texture with ID: {texture_id}")
    
    # Create window with image
    with dpg.window(label="Image Test", width=300, height=250, tag="main_window"):
        dpg.add_text("Mandelbrot Image Test:")
        image_widget = dpg.add_image("test_texture", width=width, height=height)
        print(f"Created image widget: {image_widget}")
        
        dpg.add_separator()
        dpg.add_button(label="Close", callback=lambda: dpg.stop_dearpygui())
    
    # Create viewport and show
    dpg.create_viewport(title="Image Display Test", width=350, height=300)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    
    print("Starting GUI loop...")
    dpg.start_dearpygui()
    
    dpg.destroy_context()
    print("Test complete.")


if __name__ == "__main__":
    test_image_display()