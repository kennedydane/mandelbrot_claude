#!/usr/bin/env python3
"""
Very simple texture test with a colorful pattern.
"""

import dearpygui.dearpygui as dpg
import numpy as np


def main():
    print("Starting simple texture test...")
    
    dpg.create_context()
    
    # Create a simple colorful image
    width, height = 100, 100
    
    # Create rainbow gradient
    image = np.zeros((height, width, 4), dtype=np.float32)
    for y in range(height):
        for x in range(width):
            # Rainbow colors
            image[y, x, 0] = x / width      # Red gradient left to right
            image[y, x, 1] = y / height     # Green gradient top to bottom  
            image[y, x, 2] = 0.5           # Blue constant
            image[y, x, 3] = 1.0           # Alpha
    
    flat_data = image.flatten().tolist()
    print(f"Image size: {width}x{height}, data length: {len(flat_data)}")
    
    # Create texture
    with dpg.texture_registry():
        dpg.add_raw_texture(
            width=width,
            height=height, 
            default_value=flat_data,
            format=dpg.mvFormat_Float_rgba,
            tag="rainbow_texture"
        )
    
    # Create window
    with dpg.window(label="Simple Texture Test", width=200, height=200):
        dpg.add_text("Rainbow texture:")
        dpg.add_image("rainbow_texture", width=width, height=height)
        dpg.add_button(label="Close", callback=dpg.stop_dearpygui)
    
    # Show window
    dpg.create_viewport(title="Texture Test", width=250, height=250)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    
    print("GUI started - you should see a rainbow gradient")
    dpg.start_dearpygui()
    
    dpg.destroy_context()
    print("Test complete")


if __name__ == "__main__":
    main()