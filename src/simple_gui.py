"""
Simplified Dear PyGUI interface that draws pixels directly.
"""

import dearpygui.dearpygui as dpg
import numpy as np
from typing import Tuple, Optional
from loguru import logger

from mandelbrot_core import mandelbrot_array
from color_mapping import iterations_to_rgb_array, get_available_palettes
from coordinate_transforms import ViewBounds


class SimpleMandelbrotGUI:
    """
    Simplified Mandelbrot GUI that draws pixels directly using Dear PyGUI's drawing API.
    """
    
    def __init__(self, width: int = 400, height: int = 300):
        """Initialize with smaller default size for pixel-by-pixel drawing."""
        self.image_width = width
        self.image_height = height
        
        # Initial viewing region
        self.view_bounds = ViewBounds(-2.5, 1.0, -1.25, 1.25, width, height)
        
        # Parameters
        self.max_iterations = 50  # Lower for faster rendering
        self.current_palette = 'default'
        
        # GUI elements
        self.canvas_tag = "mandelbrot_canvas"
        
        # Selection state
        self.selection_active = False
        self.selection_start: Optional[Tuple[int, int]] = None
        self.selection_end: Optional[Tuple[int, int]] = None
        
        logger.info(f"SimpleMandelbrotGUI initialized: {width}x{height}")
    
    def setup_gui(self) -> None:
        """Set up the Dear PyGUI interface."""
        logger.info("Setting up simplified Dear PyGUI interface")
        
        dpg.create_context()
        
        # Create viewport
        dpg.create_viewport(
            title="Mandelbrot Set Visualizer (Pixel Mode)",
            width=self.image_width + 300,
            height=self.image_height + 100
        )
        
        # Main window with drawing canvas
        with dpg.window(
            label="Mandelbrot Visualization",
            pos=[10, 10],
            width=self.image_width + 20,
            height=self.image_height + 50,
            no_resize=True
        ):
            # Create a drawing canvas
            with dpg.drawlist(width=self.image_width, height=self.image_height, tag=self.canvas_tag):
                # Initial black background
                dpg.draw_rectangle(
                    (0, 0), 
                    (self.image_width, self.image_height), 
                    fill=(0, 0, 0, 255)
                )
            
            # Mouse handlers for the canvas
            with dpg.item_handler_registry() as canvas_handler:
                dpg.add_item_clicked_handler(callback=self._on_canvas_click)
                dpg.add_item_hover_handler(callback=self._on_canvas_hover)
            
            dpg.bind_item_handler_registry(self.canvas_tag, canvas_handler)
        
        # Control panel
        with dpg.window(
            label="Controls",
            pos=[self.image_width + 30, 10],
            width=250,
            height=400,
            no_resize=True
        ):
            dpg.add_text("Mandelbrot Parameters")
            dpg.add_separator()
            
            dpg.add_slider_int(
                label="Max Iterations",
                default_value=self.max_iterations,
                min_value=20,
                max_value=200,
                callback=self._on_iterations_changed
            )
            
            dpg.add_separator()
            dpg.add_text("Color Palette")
            
            palettes = get_available_palettes()
            dpg.add_combo(
                label="Palette",
                items=palettes,
                default_value=self.current_palette,
                callback=self._on_palette_changed
            )
            
            dpg.add_separator()
            dpg.add_text("View Controls")
            
            dpg.add_text("Click to zoom in at point")
            dpg.add_button(
                label="Reset View",
                callback=self._reset_view,
                width=200
            )
            dpg.add_button(
                label="Zoom Out (2x)",
                callback=self._zoom_out,
                width=200
            )
            
            dpg.add_button(
                label="Render Image",
                callback=self._render_mandelbrot,
                width=200
            )
            
            dpg.add_separator()
            dpg.add_text("Current View:")
            dpg.add_text("", tag="view_info")
            self._update_view_info()
        
        # Generate initial image
        self._render_mandelbrot()
        
        logger.info("Simplified GUI setup complete")
    
    def _render_mandelbrot(self) -> None:
        """Render the Mandelbrot set pixel by pixel."""
        logger.info(f"Rendering Mandelbrot: bounds={self.view_bounds}, iterations={self.max_iterations}")
        
        # Clear the canvas
        dpg.delete_item(self.canvas_tag, children_only=True)
        
        # Calculate iteration counts
        iterations = mandelbrot_array(
            self.image_width, self.image_height,
            self.view_bounds.x_min, self.view_bounds.x_max,
            self.view_bounds.y_min, self.view_bounds.y_max,
            self.max_iterations
        )
        
        # Convert to RGB
        rgb_image = iterations_to_rgb_array(iterations, self.max_iterations, self.current_palette)
        
        logger.info("Drawing pixels...")
        
        # Draw pixels directly
        # For efficiency, we'll draw small rectangles instead of individual pixels
        pixel_size = 1
        if self.image_width > 200 or self.image_height > 200:
            pixel_size = 2  # Use 2x2 blocks for larger images
        
        for y in range(0, self.image_height, pixel_size):
            for x in range(0, self.image_width, pixel_size):
                # Get RGB color from the image
                r, g, b = rgb_image[y, x]
                color = (r, g, b, 255)  # RGBA
                
                # Draw a small rectangle for this pixel
                dpg.draw_rectangle(
                    (x, y),
                    (x + pixel_size, y + pixel_size),
                    fill=color,
                    parent=self.canvas_tag
                )
        
        self._update_view_info()
        logger.info("Mandelbrot rendering complete")
    
    def _update_view_info(self) -> None:
        """Update the view information display."""
        if dpg.does_item_exist("view_info"):
            info_text = (
                f"Real: [{self.view_bounds.x_min:.4f}, {self.view_bounds.x_max:.4f}]\\n"
                f"Imag: [{self.view_bounds.y_min:.4f}, {self.view_bounds.y_max:.4f}]"
            )
            dpg.set_value("view_info", info_text)
    
    def _on_iterations_changed(self, sender, app_data) -> None:
        """Handle max iterations change."""
        self.max_iterations = app_data
        logger.debug(f"Max iterations changed to: {self.max_iterations}")
        # Don't auto-render, let user click render button
    
    def _on_palette_changed(self, sender, app_data) -> None:
        """Handle palette change."""
        self.current_palette = app_data
        logger.debug(f"Palette changed to: {self.current_palette}")
        # Don't auto-render, let user click render button
    
    def _reset_view(self) -> None:
        """Reset to the default view."""
        logger.info("Resetting view")
        self.view_bounds = ViewBounds(-2.5, 1.0, -1.25, 1.25, self.image_width, self.image_height)
        self._render_mandelbrot()
    
    def _zoom_out(self) -> None:
        """Zoom out by 2x."""
        logger.info("Zooming out")
        center = self.view_bounds.center
        new_width = self.view_bounds.complex_width * 2
        new_height = self.view_bounds.complex_height * 2
        
        new_x_min = center.real - new_width / 2
        new_x_max = center.real + new_width / 2
        new_y_min = center.imag - new_height / 2
        new_y_max = center.imag + new_height / 2
        
        self.view_bounds = ViewBounds(new_x_min, new_x_max, new_y_min, new_y_max, self.image_width, self.image_height)
        self._render_mandelbrot()
    
    def _on_canvas_click(self, sender, app_data) -> None:
        """Handle canvas click for zoom-to-point."""
        # Get mouse position relative to canvas
        mouse_pos = dpg.get_mouse_pos()
        canvas_pos = dpg.get_item_pos(self.canvas_tag)
        
        rel_x = mouse_pos[0] - canvas_pos[0]
        rel_y = mouse_pos[1] - canvas_pos[1]
        
        # Check if click is within canvas
        if 0 <= rel_x < self.image_width and 0 <= rel_y < self.image_height:
            # Convert to complex coordinates
            click_complex = self.view_bounds.pixel_to_complex(int(rel_x), int(rel_y))
            
            logger.info(f"Zoom to point: ({rel_x}, {rel_y}) -> {click_complex}")
            
            # Zoom in by 4x centered on this point
            zoom_factor = 4
            new_width = self.view_bounds.complex_width / zoom_factor
            new_height = self.view_bounds.complex_height / zoom_factor
            
            new_x_min = click_complex.real - new_width / 2
            new_x_max = click_complex.real + new_width / 2
            new_y_min = click_complex.imag - new_height / 2
            new_y_max = click_complex.imag + new_height / 2
            
            self.view_bounds = ViewBounds(new_x_min, new_x_max, new_y_min, new_y_max, self.image_width, self.image_height)
            self._render_mandelbrot()
    
    def _on_canvas_hover(self, sender, app_data) -> None:
        """Handle canvas hover for coordinate display."""
        # This could show coordinates in real-time, but we'll keep it simple for now
        pass
    
    def run(self) -> None:
        """Run the GUI application."""
        logger.info("Starting simplified Mandelbrot GUI")
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
        
        dpg.destroy_context()
        logger.info("GUI shutdown complete")


def create_simple_gui(width: int = 400, height: int = 300) -> SimpleMandelbrotGUI:
    """
    Create and return a configured SimpleMandelbrotGUI instance.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        Configured SimpleMandelbrotGUI instance
    """
    gui = SimpleMandelbrotGUI(width, height)
    gui.setup_gui()
    return gui