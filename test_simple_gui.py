#!/usr/bin/env python3
"""
Simple Dear PyGUI test to verify basic functionality.
"""

import dearpygui.dearpygui as dpg
import numpy as np

def create_simple_gui():
    """Test basic Dear PyGUI functionality."""
    
    # Create context
    dpg.create_context()
    
    # Create a simple window
    with dpg.window(label="Test Window", width=400, height=300, tag="test_window"):
        dpg.add_text("Hello Dear PyGUI!")
        dpg.add_button(label="Test Button", callback=lambda: print("Button clicked!"))
        dpg.add_slider_float(label="Test Slider", default_value=0.5, min_value=0.0, max_value=1.0)
    
    # Create viewport
    dpg.create_viewport(title="Simple GUI Test", width=500, height=400)
    
    # Setup and show
    dpg.setup_dearpygui()
    dpg.show_viewport()
    
    # Set primary window
    dpg.set_primary_window("test_window", True)
    
    print("Starting Dear PyGUI...")
    
    # Run for a few seconds then exit
    import time
    start_time = time.time()
    while dpg.is_dearpygui_running() and time.time() - start_time < 5:
        dpg.render_dearpygui_frame()
    
    # Cleanup
    dpg.destroy_context()
    print("GUI test complete")

if __name__ == "__main__":
    create_simple_gui()