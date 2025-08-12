"""
Dear PyGUI interface for the Mandelbrot set visualizer.

This module provides the interactive GUI including:
- Main visualization window with image display
- Control panel with parameter sliders
- Area selection zooming functionality
- Real-time rendering and feedback
"""

import dearpygui.dearpygui as dpg
import numpy as np
from typing import Tuple, Optional, List
from loguru import logger

from mandelbrot_core import mandelbrot_array
from color_mapping import iterations_to_rgb_array, get_available_palettes
from coordinate_transforms import ViewBounds


class MandelbrotGUI:
    """
    Main GUI class for the Mandelbrot set visualizer.
    
    Features:
    - Interactive image display with Dear PyGUI
    - Real-time parameter adjustment
    - Area selection for zooming
    - Multiple color palettes
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize the Mandelbrot GUI.
        
        Args:
            width: Initial image width
            height: Initial image height
        """
        self.image_width = width
        self.image_height = height
        
        # Initial viewing region (classic Mandelbrot view)
        self.view_bounds = ViewBounds(-2.5, 1.0, -1.25, 1.25, width, height)
        
        # Calculation parameters
        self.max_iterations = 100
        self.current_palette = 'default'
        
        # GUI state - use unique IDs to avoid conflicts
        import time
        unique_id = str(int(time.time() * 1000))
        self.texture_tag = f"mandelbrot_texture_{unique_id}"
        self.image_tag = f"mandelbrot_image_{unique_id}"
        self.window_tag = f"mandelbrot_window_{unique_id}"
        self.control_window_tag = f"control_window_{unique_id}"
        
        # Current image data
        self.current_image: Optional[np.ndarray] = None
        
        # Area selection state
        self.selection_active = False
        self.selection_start: Optional[Tuple[int, int]] = None
        self.selection_end: Optional[Tuple[int, int]] = None
        
        logger.info(f"MandelbrotGUI initialized: {width}x{height}, bounds: {self.view_bounds}")
    
    def setup_gui(self) -> None:
        """Set up the Dear PyGUI interface."""
        logger.info("Setting up Dear PyGUI interface")
        
        # Create Dear PyGUI context
        dpg.create_context()
        
        # Configure viewport
        dpg.create_viewport(
            title="Mandelbrot Set Visualizer",
            width=self.image_width + 300,  # Extra space for controls
            height=self.image_height + 100
        )
        
        # Create texture registry first
        dpg.add_texture_registry(tag="texture_registry")
        
        # Create initial texture (black placeholder)
        placeholder_data = np.zeros((self.image_height, self.image_width, 3), dtype=np.uint8)
        self._create_texture(placeholder_data)
        
        # Create main window
        with dpg.window(
            label="Mandelbrot Visualization", 
            tag=self.window_tag,
            pos=[10, 10],
            width=self.image_width + 20,
            height=self.image_height + 50,
            no_resize=True,
            no_move=True
        ):
            # Add image widget
            dpg.add_image(self.texture_tag, tag=self.image_tag)
            
            # Add mouse handlers for area selection
            with dpg.handler_registry():
                dpg.add_mouse_click_handler(
                    button=dpg.mvMouseButton_Left,
                    callback=self._on_mouse_click
                )
                dpg.add_mouse_drag_handler(
                    button=dpg.mvMouseButton_Left,
                    callback=self._on_mouse_drag
                )
                dpg.add_mouse_release_handler(
                    button=dpg.mvMouseButton_Left,
                    callback=self._on_mouse_release
                )
        
        # Create control panel
        self._create_control_panel()
        
        # Generate initial image
        self._generate_mandelbrot()
        
        logger.info("GUI setup complete")
    
    def _create_control_panel(self) -> None:
        """Create the control panel with parameter sliders."""
        with dpg.window(
            label="Controls",
            tag=self.control_window_tag,
            pos=[self.image_width + 30, 10],
            width=250,
            height=400,
            no_resize=True,
            no_move=True
        ):
            dpg.add_text("Mandelbrot Parameters")
            dpg.add_separator()
            
            # Max iterations slider
            dpg.add_slider_int(
                label="Max Iterations",
                default_value=self.max_iterations,
                min_value=50,
                max_value=500,
                callback=self._on_iterations_changed,
                tag="iterations_slider"
            )
            
            dpg.add_separator()
            dpg.add_text("Color Palette")
            
            # Color palette selection
            palettes = get_available_palettes()
            dpg.add_combo(
                label="Palette",
                items=palettes,
                default_value=self.current_palette,
                callback=self._on_palette_changed,
                tag="palette_combo"
            )
            
            dpg.add_separator()
            dpg.add_text("View Controls")
            
            # View information
            dpg.add_text("", tag="view_info")
            self._update_view_info()
            
            # Reset view button
            dpg.add_button(
                label="Reset View",
                callback=self._reset_view,
                width=200
            )
            
            # Zoom out button
            dpg.add_button(
                label="Zoom Out (2x)",
                callback=self._zoom_out,
                width=200
            )
            
            dpg.add_separator()
            dpg.add_text("Instructions")
            dpg.add_text("• Click and drag to select area")
            dpg.add_text("• Selected area will zoom on release")
            dpg.add_text("• Use Reset View to return")
    
    def _create_texture(self, image_data: np.ndarray) -> None:
        """Create or update the texture for the image display."""
        logger.debug(f"Creating texture from image data: shape={image_data.shape}, dtype={image_data.dtype}")
        
        # Save image as temporary file and load as texture
        # This avoids the raw texture issues we're having
        temp_file = f"/tmp/mandelbrot_temp_{self.texture_tag}.png"
        
        try:
            from PIL import Image
            # Convert numpy array to PIL Image and save
            if image_data.dtype == np.uint8:
                img = Image.fromarray(image_data, 'RGB')
            else:
                # Ensure it's in the right format
                img_data = (image_data * 255).astype(np.uint8) if image_data.max() <= 1.0 else image_data.astype(np.uint8)
                img = Image.fromarray(img_data, 'RGB')
            
            img.save(temp_file)
            logger.debug(f"Saved temporary image: {temp_file}")
            
            # Delete existing texture if it exists  
            if dpg.does_item_exist(self.texture_tag):
                dpg.delete_item(self.texture_tag)
            
            # Load texture from file
            width, height, channels, data = dpg.load_image(temp_file)
            logger.debug(f"Loaded image: {width}x{height}, {channels} channels")
            
            # Create texture from loaded data
            dpg.add_static_texture(
                width=width,
                height=height,
                default_value=data,
                tag=self.texture_tag,
                parent="texture_registry"
            )
            
            # Clean up temp file
            import os
            os.remove(temp_file)
            
        except Exception as e:
            logger.error(f"Error creating texture: {e}")
            # Fallback: create a simple colored rectangle
            self._create_fallback_texture()
    
    def _create_fallback_texture(self) -> None:
        """Create a simple fallback texture when image loading fails."""
        logger.warning("Creating fallback texture")
        
        # Create a simple gradient as fallback
        fallback_data = []
        for y in range(self.image_height):
            for x in range(self.image_width):
                # Simple gradient from blue to red
                r = int(255 * x / self.image_width) / 255.0
                g = 0.0
                b = int(255 * (1 - x / self.image_width)) / 255.0
                a = 1.0
                fallback_data.extend([r, g, b, a])
        
        # Delete existing texture if it exists
        if dpg.does_item_exist(self.texture_tag):
            dpg.delete_item(self.texture_tag)
        
        # Create simple texture
        dpg.add_static_texture(
            width=self.image_width,
            height=self.image_height,
            default_value=fallback_data,
            tag=self.texture_tag,
            parent="texture_registry"
        )
    
    def _generate_mandelbrot(self) -> None:
        """Generate a new Mandelbrot image with current parameters."""
        logger.info(f"Generating Mandelbrot: bounds={self.view_bounds}, iterations={self.max_iterations}")
        
        # Calculate iteration counts
        iterations = mandelbrot_array(
            self.image_width, self.image_height,
            self.view_bounds.x_min, self.view_bounds.x_max,
            self.view_bounds.y_min, self.view_bounds.y_max,
            self.max_iterations
        )
        
        # Convert to RGB
        rgb_image = iterations_to_rgb_array(iterations, self.max_iterations, self.current_palette)
        
        # Store current image
        self.current_image = rgb_image
        
        # Update texture
        self._create_texture(rgb_image)
        
        # Update view information
        self._update_view_info()
        
        logger.info("Mandelbrot generation complete")
    
    def _update_view_info(self) -> None:
        """Update the view information display."""
        if dpg.does_item_exist("view_info"):
            info_text = (
                f"Real: [{self.view_bounds.x_min:.6f}, {self.view_bounds.x_max:.6f}]\\n"
                f"Imag: [{self.view_bounds.y_min:.6f}, {self.view_bounds.y_max:.6f}]\\n"
                f"Width: {self.view_bounds.complex_width:.6f}\\n"
                f"Height: {self.view_bounds.complex_height:.6f}"
            )
            dpg.set_value("view_info", info_text)
    
    def _on_iterations_changed(self, sender, app_data) -> None:
        """Handle max iterations slider change."""
        self.max_iterations = app_data
        logger.debug(f"Max iterations changed to: {self.max_iterations}")
        self._generate_mandelbrot()
    
    def _on_palette_changed(self, sender, app_data) -> None:
        """Handle color palette change."""
        self.current_palette = app_data
        logger.debug(f"Color palette changed to: {self.current_palette}")
        self._generate_mandelbrot()
    
    def _reset_view(self) -> None:
        """Reset to the default Mandelbrot view."""
        logger.info("Resetting view to default")
        self.view_bounds = ViewBounds(-2.5, 1.0, -1.25, 1.25, self.image_width, self.image_height)
        self._generate_mandelbrot()
    
    def _zoom_out(self) -> None:
        """Zoom out by a factor of 2."""
        logger.info("Zooming out by 2x")
        center = self.view_bounds.center
        new_width = self.view_bounds.complex_width * 2
        new_height = self.view_bounds.complex_height * 2
        
        new_x_min = center.real - new_width / 2
        new_x_max = center.real + new_width / 2
        new_y_min = center.imag - new_height / 2
        new_y_max = center.imag + new_height / 2
        
        self.view_bounds = ViewBounds(new_x_min, new_x_max, new_y_min, new_y_max, self.image_width, self.image_height)
        self._generate_mandelbrot()
    
    def _on_mouse_click(self, sender, app_data) -> None:
        """Handle mouse click for area selection."""
        # Get mouse position relative to image
        mouse_pos = dpg.get_mouse_pos()
        image_pos = dpg.get_item_pos(self.image_tag)
        
        # Check if click is within image bounds
        rel_x = mouse_pos[0] - image_pos[0]
        rel_y = mouse_pos[1] - image_pos[1]
        
        if 0 <= rel_x < self.image_width and 0 <= rel_y < self.image_height:
            self.selection_active = True
            self.selection_start = (int(rel_x), int(rel_y))
            self.selection_end = None
            logger.debug(f"Selection started at: {self.selection_start}")
    
    def _on_mouse_drag(self, sender, app_data) -> None:
        """Handle mouse drag for area selection."""
        if self.selection_active:
            mouse_pos = dpg.get_mouse_pos()
            image_pos = dpg.get_item_pos(self.image_tag)
            
            rel_x = mouse_pos[0] - image_pos[0]
            rel_y = mouse_pos[1] - image_pos[1]
            
            # Clamp to image bounds
            rel_x = max(0, min(self.image_width - 1, int(rel_x)))
            rel_y = max(0, min(self.image_height - 1, int(rel_y)))
            
            self.selection_end = (rel_x, rel_y)
            # TODO: Draw selection rectangle overlay
    
    def _on_mouse_release(self, sender, app_data) -> None:
        """Handle mouse release to complete area selection."""
        if self.selection_active and self.selection_start and self.selection_end:
            logger.info(f"Selection completed: {self.selection_start} to {self.selection_end}")
            
            # Ensure we have a valid selection rectangle
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            
            # Make sure we have a minimum selection size
            if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
                # Create new view bounds from selection
                top_left = (min(x1, x2), min(y1, y2))
                bottom_right = (max(x1, x2), max(y1, y2))
                
                self.view_bounds = self.view_bounds.zoom_to_region(top_left, bottom_right)
                self._generate_mandelbrot()
            else:
                logger.debug("Selection too small, ignoring")
        
        # Reset selection state
        self.selection_active = False
        self.selection_start = None
        self.selection_end = None
    
    def run(self) -> None:
        """Run the GUI application."""
        logger.info("Starting Mandelbrot GUI")
        
        # Setup viewport and show
        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        # Main loop
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
        
        # Cleanup
        dpg.destroy_context()
        logger.info("GUI shutdown complete")


def create_gui(width: int = 800, height: int = 600) -> MandelbrotGUI:
    """
    Create and return a configured MandelbrotGUI instance.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        Configured MandelbrotGUI instance
    """
    gui = MandelbrotGUI(width, height)
    gui.setup_gui()
    return gui