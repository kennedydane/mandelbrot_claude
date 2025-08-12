"""
Corrected Dear PyGUI interface for Mandelbrot visualization using proven texture patterns.
"""

import dearpygui.dearpygui as dpg
import numpy as np
from typing import Tuple, Optional
from loguru import logger
import time
import threading

from mandelbrot_core import mandelbrot_array
from color_mapping import iterations_to_rgb_array, get_available_palettes
from coordinate_transforms import ViewBounds


class MandelbrotGUI:
    """
    Mandelbrot GUI with proper texture handling and progressive zoom UX.
    """
    
    def __init__(self, width: int = 600, height: int = 400):
        """Initialize with reasonable size for texture performance."""
        self.image_width = width
        self.image_height = height
        
        # View bounds
        self.view_bounds = ViewBounds(-2.5, 1.0, -1.25, 1.25, width, height)
        
        # Parameters
        self.max_iterations = 100
        self.current_palette = 'default'
        
        # Texture management
        self.texture_counter = 0
        self.current_texture_tag = None
        self.texture_registry_tag = "mandelbrot_texture_registry"
        
        # GUI elements  
        self.main_window_tag = "main_window"
        self.control_window_tag = "control_window"
        self.image_tag = "mandelbrot_image"
        
        # Calculation state
        self.calculating = False
        self.calculation_thread = None
        
        # Zoom history for better navigation
        self.zoom_history = []
        self.max_history = 10
        
        # Selection state
        self.selection_active = False
        self.selection_start: Optional[Tuple[int, int]] = None
        self.selection_end: Optional[Tuple[int, int]] = None
        self.selection_overlay_tag = None
        
        # Resize optimization
        self.resize_pending = False
        self.last_resize_time = 0
        self.resize_throttle_delay = 0.2  # 200ms throttle
        
        # Save functionality
        self.current_rgb_image = None  # Store current image for saving
        
        logger.info(f"MandelbrotGUI initialized: {width}x{height}")
    
    def setup_gui(self) -> None:
        """Set up the Dear PyGUI interface with proper texture handling."""
        logger.info("Setting up Mandelbrot GUI")
        
        # Create context
        dpg.create_context()
        
        # Create viewport
        dpg.create_viewport(
            title="Mandelbrot Set Visualizer",
            width=self.image_width + 350,
            height=self.image_height + 100
        )
        
        # Create texture registry ONCE
        dpg.add_texture_registry(tag=self.texture_registry_tag)
        
        # Create initial black texture
        self._create_initial_texture()
        
        # Main visualization window - properly sized to avoid scrollbars
        with dpg.window(
            label="Mandelbrot Visualization", 
            tag=self.main_window_tag,
            pos=[10, 10],
            width=self.image_width + 30,  # Extra padding for window borders
            height=self.image_height + 80,  # Room for status text + window chrome
            no_resize=False,  # Allow resizing
            no_scrollbar=True,  # Disable scrollbars 
            no_collapse=False,
            on_close=lambda: dpg.stop_dearpygui()  # Close app when main window closes
        ):
            # Status text at the top - separated from image area
            dpg.add_text("Click and drag to select area to zoom, or click to zoom to point", tag="status_text", wrap=self.image_width + 10)
            dpg.add_separator()
            
            # Image display directly in main window
            dpg.add_image(self.current_texture_tag, tag=self.image_tag, width=self.image_width, height=self.image_height)
            
            # Mouse handlers for area selection
            with dpg.handler_registry():
                dpg.add_mouse_click_handler(
                    button=dpg.mvMouseButton_Left,
                    callback=self._on_mouse_press
                )
                dpg.add_mouse_drag_handler(
                    button=dpg.mvMouseButton_Left,
                    callback=self._on_mouse_drag
                )
                dpg.add_mouse_release_handler(
                    button=dpg.mvMouseButton_Left,
                    callback=self._on_mouse_release
                )
                
                # Keyboard shortcuts
                dpg.add_key_press_handler(
                    dpg.mvKey_R,
                    callback=lambda: self._render_mandelbrot()
                )
                dpg.add_key_press_handler(
                    dpg.mvKey_H,
                    callback=lambda: self._reset_view()
                )
                dpg.add_key_press_handler(
                    dpg.mvKey_O,
                    callback=lambda: self._zoom_out()
                )
                dpg.add_key_press_handler(
                    dpg.mvKey_Escape,
                    callback=lambda: logger.debug("Escape pressed")
                )
                dpg.add_key_press_handler(
                    dpg.mvKey_B,
                    callback=lambda: self._zoom_back()
                )
                dpg.add_key_press_handler(
                    dpg.mvKey_S,
                    callback=lambda: self._show_save_dialog()
                )
        
        # Create window-specific handler registry for resize events
        with dpg.item_handler_registry(tag="window_handlers") as handler_reg:
            dpg.add_item_resize_handler(callback=self._on_window_resize)
        
        # Bind handler registry to main window
        dpg.bind_item_handler_registry(self.main_window_tag, "window_handlers")
        
        # Control panel
        self._create_control_panel()
        
        
        logger.info("GUI setup complete")
    
    
    def _create_initial_texture(self) -> None:
        """Create initial black texture using file-based approach."""
        logger.debug("Creating initial texture")
        
        import tempfile
        import os
        from PIL import Image
        
        # Create black RGB image
        black_image = np.zeros((self.image_height, self.image_width, 3), dtype=np.uint8)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_file = f.name
        
        pil_image = Image.fromarray(black_image)
        pil_image.save(temp_file)
        
        # Load texture from file
        width, height, channels, data = dpg.load_image(temp_file)
        
        # Create texture with unique tag
        self.texture_counter += 1
        self.current_texture_tag = f"mandelbrot_texture_{self.texture_counter}"
        
        dpg.add_static_texture(
            width=width,
            height=height,
            default_value=data,
            tag=self.current_texture_tag,
            parent=self.texture_registry_tag
        )
        
        # Clean up temp file
        os.unlink(temp_file)
        
        logger.debug(f"Initial texture created: {self.current_texture_tag}")
    
    def _create_control_panel(self) -> None:
        """Create control panel with parameters."""
        with dpg.window(
            label="Controls",
            tag=self.control_window_tag,
            pos=[self.image_width + 40, 10],
            width=280,
            height=500,
            no_resize=True
        ):
            dpg.add_text("Mandelbrot Parameters", color=[255, 255, 255])
            dpg.add_separator()
            
            # Iterations slider
            dpg.add_slider_int(
                label="Max Iterations",
                default_value=self.max_iterations,
                min_value=50,
                max_value=500,
                callback=self._on_iterations_changed,
                tag="iterations_slider"
            )
            
            dpg.add_separator()
            
            # Color palette
            dpg.add_text("Color Palette")
            palettes = get_available_palettes()
            dpg.add_combo(
                label="Palette",
                items=palettes,
                default_value=self.current_palette,
                callback=self._on_palette_changed,
                tag="palette_combo"
            )
            
            dpg.add_separator()
            
            # View controls
            dpg.add_text("View Controls")
            
            dpg.add_button(
                label="Render Image",
                callback=self._render_mandelbrot,
                width=250,
                tag="render_button"
            )
            
            dpg.add_button(
                label="Reset View",
                callback=self._reset_view,
                width=250
            )
            
            dpg.add_button(
                label="Zoom Out (2x)",
                callback=self._zoom_out,
                width=250
            )
            
            dpg.add_button(
                label="Back (Zoom History)",
                callback=self._zoom_back,
                width=250
            )
            
            dpg.add_button(
                label="Save Image",
                callback=self._show_save_dialog,
                width=250
            )
            
            dpg.add_separator()
            
            # View information
            dpg.add_text("Current View:")
            dpg.add_text("", tag="view_info", wrap=250)
            
            dpg.add_separator()
            
            # Calculation status
            dpg.add_text("Status:", tag="calc_status")
            dpg.add_progress_bar(tag="progress_bar", default_value=0.0, width=250)
            
            dpg.add_separator()
            
            # Instructions
            dpg.add_text("Instructions:", color=[255, 255, 0])
            dpg.add_text("• Click and drag to select area to zoom", wrap=250)
            dpg.add_text("• Small drag or click zooms to point", wrap=250)
            dpg.add_text("• Adjust parameters and click Render", wrap=250)
            dpg.add_text("• Use Reset View to return to full set", wrap=250)
            
            dpg.add_separator()
            dpg.add_text("Keyboard Shortcuts:", color=[255, 255, 0])
            dpg.add_text("• R - Render image", wrap=250)
            dpg.add_text("• H - Reset to home view", wrap=250) 
            dpg.add_text("• O - Zoom out 2x", wrap=250)
            dpg.add_text("• B - Back (zoom history)", wrap=250)
            dpg.add_text("• S - Save image", wrap=250)
            
        self._update_view_info()
    
    def _update_texture(self, rgb_image: np.ndarray) -> None:
        """Update texture using file-based approach (proven to work)."""
        logger.debug("Updating texture with new image using file method")
        
        import tempfile
        import os
        from PIL import Image
        
        # Store current image for saving functionality
        self.current_rgb_image = rgb_image.copy()
        
        try:
            # Save image to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                temp_file = f.name
            
            pil_image = Image.fromarray(rgb_image)
            pil_image.save(temp_file)
            
            # Load texture from file
            width, height, channels, data = dpg.load_image(temp_file)
            logger.debug(f"Loaded image: {width}x{height}, {channels} channels")
            
            # Delete old texture
            if self.current_texture_tag and dpg.does_item_exist(self.current_texture_tag):
                dpg.delete_item(self.current_texture_tag)
            
            # Create new texture with unique tag
            self.texture_counter += 1
            new_texture_tag = f"mandelbrot_texture_{self.texture_counter}"
            
            dpg.add_static_texture(
                width=width,
                height=height,
                default_value=data,
                tag=new_texture_tag,
                parent=self.texture_registry_tag
            )
            
            # Update image widget to use new texture
            logger.debug(f"Updating image widget with texture: {new_texture_tag}")
            if dpg.does_item_exist(self.image_tag):
                # Update the texture source directly instead of recreating the widget
                logger.debug(f"Updating image texture source to: {new_texture_tag}")
                dpg.configure_item(self.image_tag, texture_tag=new_texture_tag)
                logger.debug(f"Image texture updated successfully")
            else:
                logger.debug(f"Image widget {self.image_tag} doesn't exist yet - this is normal for initial setup")
            
            # Update current texture reference
            self.current_texture_tag = new_texture_tag
            
            # Clean up temp file
            os.unlink(temp_file)
            
            logger.debug(f"Texture updated successfully: {new_texture_tag}")
            
        except Exception as e:
            logger.error(f"Failed to update texture: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Continue anyway - don't let texture issues kill the GUI
            logger.warning("Continuing with GUI despite texture update failure")
    
    def _render_initial_mandelbrot(self) -> None:
        """Render initial Mandelbrot image synchronously."""
        logger.info("Rendering initial Mandelbrot image")
        
        try:
            # Calculate iterations
            iterations = mandelbrot_array(
                self.image_width, self.image_height,
                self.view_bounds.x_min, self.view_bounds.x_max,
                self.view_bounds.y_min, self.view_bounds.y_max,
                self.max_iterations
            )
            
            # Convert to RGB
            rgb_image = iterations_to_rgb_array(iterations, self.max_iterations, self.current_palette)
            
            # Update texture immediately
            self._update_texture(rgb_image)
            self._update_view_info()
            self._update_status("Ready")
            
            logger.info("Initial Mandelbrot image rendered successfully")
            
        except Exception as e:
            logger.error(f"Failed to render initial image: {e}")
            self._update_status(f"Error: {e}")
    
    def _render_mandelbrot(self) -> None:
        """Render Mandelbrot set with progress feedback."""
        if self.calculating:
            logger.info("Calculation already in progress")
            return
        
        logger.info(f"Starting Mandelbrot calculation: {self.view_bounds}")
        
        self.calculating = True
        self._update_status("Calculating...")
        dpg.set_value("progress_bar", 0.0)
        
        # Start calculation in background thread
        self.calculation_thread = threading.Thread(target=self._calculate_mandelbrot)
        self.calculation_thread.daemon = True
        self.calculation_thread.start()
    
    def _calculate_mandelbrot(self) -> None:
        """Calculate Mandelbrot set in background thread."""
        try:
            # Simulate progress updates
            dpg.set_value("progress_bar", 0.2)
            
            # Calculate iterations
            iterations = mandelbrot_array(
                self.image_width, self.image_height,
                self.view_bounds.x_min, self.view_bounds.x_max,
                self.view_bounds.y_min, self.view_bounds.y_max,
                self.max_iterations
            )
            
            dpg.set_value("progress_bar", 0.6)
            
            # Convert to RGB
            rgb_image = iterations_to_rgb_array(iterations, self.max_iterations, self.current_palette)
            
            dpg.set_value("progress_bar", 0.9)
            
            # Update texture on main thread
            dpg.set_value("progress_bar", 1.0)
            self._update_texture(rgb_image)
            self._update_view_info()
            self._update_status("Ready")
            
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            self._update_status(f"Error: {e}")
        
        finally:
            self.calculating = False
            dpg.set_value("progress_bar", 0.0)
    
    def _update_status(self, status: str) -> None:
        """Update status text."""
        if dpg.does_item_exist("calc_status"):
            dpg.set_value("calc_status", f"Status: {status}")
    
    def _update_view_info(self) -> None:
        """Update view information display."""
        if dpg.does_item_exist("view_info"):
            info = (
                f"Real: [{self.view_bounds.x_min:.6f}, {self.view_bounds.x_max:.6f}]\n"
                f"Imag: [{self.view_bounds.y_min:.6f}, {self.view_bounds.y_max:.6f}]\n"
                f"Size: {self.view_bounds.complex_width:.6f} x {self.view_bounds.complex_height:.6f}"
            )
            dpg.set_value("view_info", info)
    
    def _on_iterations_changed(self, sender, app_data) -> None:
        """Handle iterations slider change."""
        self.max_iterations = app_data
        logger.debug(f"Max iterations: {self.max_iterations}")
    
    def _on_palette_changed(self, sender, app_data) -> None:
        """Handle palette change."""
        self.current_palette = app_data
        logger.debug(f"Palette: {self.current_palette}")
    
    def _reset_view(self) -> None:
        """Reset to default view."""
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
    
    def _get_mouse_image_pos(self) -> Optional[Tuple[int, int]]:
        """Get mouse position relative to the image."""
        try:
            mouse_pos = dpg.get_mouse_pos()
            
            # Get the image widget position directly
            image_pos = dpg.get_item_pos(self.image_tag)
            
            # Calculate relative position within the image
            rel_x = int(mouse_pos[0] - image_pos[0])
            rel_y = int(mouse_pos[1] - image_pos[1])
            
            # Check if within image bounds
            if 0 <= rel_x < self.image_width and 0 <= rel_y < self.image_height:
                return (rel_x, rel_y)
            return None
        except Exception as e:
            logger.debug(f"Mouse position error: {e}")
            return None
    
    def _on_mouse_press(self, sender, app_data) -> None:
        """Handle mouse press to start area selection."""
        pos = self._get_mouse_image_pos()
        if pos:
            self.selection_start = pos
            self.selection_end = None
            self.selection_active = True
            logger.debug(f"Selection started at: {pos}")
    
    def _on_mouse_drag(self, sender, app_data) -> None:
        """Handle mouse drag to update selection area."""
        if self.selection_active:
            pos = self._get_mouse_image_pos()
            if pos:
                self.selection_end = pos
                
                # Log drag position for feedback
                if self.selection_start:
                    width = abs(pos[0] - self.selection_start[0])
                    height = abs(pos[1] - self.selection_start[1])
                    logger.debug(f"Selection drag: {self.selection_start} -> {pos}, size: {width}x{height}")
    
    def _on_mouse_release(self, sender, app_data) -> None:
        """Handle mouse release to complete area selection."""
        if self.selection_active and self.selection_start and self.selection_end:
            # Check if we have a meaningful selection
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            # Minimum selection size to avoid tiny zooms
            if width > 20 and height > 20:
                logger.info(f"Area selection: {self.selection_start} to {self.selection_end}")
                self._zoom_to_selection()
            else:
                # Small drag - treat as click-to-zoom
                click_point = self.view_bounds.pixel_to_complex(x1, y1)
                logger.info(f"Click zoom at: ({x1}, {y1}) -> {click_point}")
                self._zoom_to_point(click_point)
        
        # Reset selection state
        self.selection_active = False
        self.selection_start = None
        self.selection_end = None
    
    
    def _zoom_to_selection(self) -> None:
        """Zoom to the selected area."""
        if not (self.selection_start and self.selection_end):
            return
        
        x1, y1 = self.selection_start
        x2, y2 = self.selection_end
        
        # Ensure proper ordering
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        
        # Save to history before zooming
        self._save_to_history()
        
        # Use ViewBounds zoom_to_region method
        self.view_bounds = self.view_bounds.zoom_to_region((min_x, min_y), (max_x, max_y))
        self._render_mandelbrot()
    
    def _zoom_to_point(self, point: complex, zoom_factor: float = 4.0) -> None:
        """Zoom to a specific point."""
        # Save to history before zooming
        self._save_to_history()
        
        new_width = self.view_bounds.complex_width / zoom_factor
        new_height = self.view_bounds.complex_height / zoom_factor
        
        new_x_min = point.real - new_width / 2
        new_x_max = point.real + new_width / 2
        new_y_min = point.imag - new_height / 2
        new_y_max = point.imag + new_height / 2
        
        self.view_bounds = ViewBounds(new_x_min, new_x_max, new_y_min, new_y_max, self.image_width, self.image_height)
        self._render_mandelbrot()
    
    def _save_to_history(self) -> None:
        """Save current view bounds to history."""
        current_bounds = (
            self.view_bounds.x_min, self.view_bounds.x_max,
            self.view_bounds.y_min, self.view_bounds.y_max
        )
        
        # Avoid duplicates
        if not self.zoom_history or self.zoom_history[-1] != current_bounds:
            self.zoom_history.append(current_bounds)
            
            # Keep history size manageable
            if len(self.zoom_history) > self.max_history:
                self.zoom_history.pop(0)
    
    def _zoom_back(self) -> None:
        """Go back to previous zoom level."""
        if len(self.zoom_history) > 1:
            # Remove current position
            self.zoom_history.pop()
            
            # Get previous position
            x_min, x_max, y_min, y_max = self.zoom_history[-1]
            self.view_bounds = ViewBounds(x_min, x_max, y_min, y_max, self.image_width, self.image_height)
            self._render_mandelbrot()
            
            logger.info("Zoomed back in history")
        else:
            logger.info("No zoom history available")
    
    def _show_save_dialog(self) -> None:
        """Show dialog to save current image."""
        if self.current_rgb_image is None:
            self._update_status("No image to save - render first")
            logger.warning("No current image available to save")
            return
        
        # Generate default filename with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"mandelbrot_{timestamp}.png"
        
        # Create save dialog
        with dpg.window(
            label="Save Image", 
            tag="save_dialog",
            modal=True,
            width=400,
            height=150,
            pos=[200, 200]
        ):
            dpg.add_text("Enter filename for the image:")
            dpg.add_input_text(
                label="",
                default_value=default_filename,
                tag="save_filename_input",
                width=350
            )
            
            dpg.add_separator()
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Save",
                    callback=self._save_image_confirmed,
                    width=100
                )
                dpg.add_button(
                    label="Cancel", 
                    callback=lambda: dpg.delete_item("save_dialog"),
                    width=100
                )
    
    def _save_image_confirmed(self) -> None:
        """Save the image with the specified filename."""
        if not dpg.does_item_exist("save_filename_input"):
            return
            
        filename = dpg.get_value("save_filename_input").strip()
        dpg.delete_item("save_dialog")
        
        if not filename:
            self._update_status("Save cancelled - no filename provided")
            return
        
        # Ensure .png extension
        if not filename.lower().endswith('.png'):
            filename += '.png'
        
        self._save_current_image(filename)
    
    def _save_current_image(self, filename: str) -> None:
        """Save the current RGB image to a PNG file."""
        if self.current_rgb_image is None:
            self._update_status("No image to save")
            return
        
        try:
            from PIL import Image
            import os
            
            logger.info(f"Saving current image to: {filename}")
            self._update_status(f"Saving image to {filename}...")
            
            # Convert RGB array to PIL Image
            pil_image = Image.fromarray(self.current_rgb_image)
            
            # Check if file exists and get user confirmation if needed
            if os.path.exists(filename):
                logger.warning(f"File {filename} already exists - overwriting")
            
            # Save the image
            pil_image.save(filename)
            
            # Success feedback
            self._update_status(f"Image saved successfully: {filename}")
            logger.info(f"Image saved successfully to: {filename}")
            
        except Exception as e:
            error_msg = f"Failed to save image: {e}"
            self._update_status(error_msg)
            logger.error(error_msg)
    
    def _on_window_resize(self, sender, app_data) -> None:
        """Handle window resize with throttling and visual feedback."""
        if not dpg.does_item_exist(self.main_window_tag):
            return
            
        current_time = time.time()
        
        # Throttle resize events to prevent excessive re-renders
        if current_time - self.last_resize_time < self.resize_throttle_delay:
            self.resize_pending = True
            return
            
        self.last_resize_time = current_time
        self.resize_pending = False
        
        # Get current window dimensions
        window_width = dpg.get_item_width(self.main_window_tag)
        window_height = dpg.get_item_height(self.main_window_tag)
        
        # Calculate new image dimensions with padding
        new_image_width = max(200, window_width - 30)  # Minimum 200px width
        new_image_height = max(150, window_height - 80)  # Minimum 150px height
        
        # Only update if dimensions changed significantly (avoid micro-updates)
        width_diff = abs(new_image_width - self.image_width)
        height_diff = abs(new_image_height - self.image_height)
        
        if width_diff > 10 or height_diff > 10:
            logger.info(f"Window resized: {window_width}x{window_height} -> image: {new_image_width}x{new_image_height}")
            
            # Show resize feedback in status
            self._update_status(f"Resizing to {new_image_width}x{new_image_height}...")
            
            # Update dimensions
            self.image_width = new_image_width
            self.image_height = new_image_height
            
            # Update view bounds to maintain aspect ratio
            self.view_bounds = ViewBounds(
                self.view_bounds.x_min, self.view_bounds.x_max,
                self.view_bounds.y_min, self.view_bounds.y_max,
                self.image_width, self.image_height
            )
            
            # Resize the image widget
            if dpg.does_item_exist(self.image_tag):
                dpg.configure_item(self.image_tag, width=self.image_width, height=self.image_height)
            
            # Update status text wrap
            if dpg.does_item_exist("status_text"):
                dpg.configure_item("status_text", wrap=self.image_width + 10)
            
            # Update view information display
            self._update_view_info()
            
            # Trigger optimized re-render with new dimensions
            self._render_mandelbrot_optimized()
    
    def _render_mandelbrot_optimized(self) -> None:
        """Optimized render for resize operations - uses lower quality for speed."""
        if self.calculating:
            logger.debug("Skipping optimized render - calculation in progress")
            return
        
        # Use reduced iterations for resize preview (faster rendering)
        preview_iterations = min(50, self.max_iterations // 2)
        
        logger.debug(f"Starting optimized render with {preview_iterations} iterations")
        
        self.calculating = True
        self._update_status("Quick preview...")
        
        def quick_calculation():
            try:
                # Calculate with reduced iterations
                iterations = mandelbrot_array(
                    self.image_width, self.image_height,
                    self.view_bounds.x_min, self.view_bounds.x_max,
                    self.view_bounds.y_min, self.view_bounds.y_max,
                    preview_iterations
                )
                
                # Convert to RGB
                rgb_image = iterations_to_rgb_array(iterations, preview_iterations, self.current_palette)
                
                # Update texture
                self._update_texture(rgb_image)
                self._update_view_info()
                self._update_status("Preview ready - Click Render for full quality")
                
            except Exception as e:
                logger.error(f"Optimized calculation error: {e}")
                self._update_status(f"Preview error: {e}")
            
            finally:
                self.calculating = False
        
        # Run in background
        thread = threading.Thread(target=quick_calculation)
        thread.daemon = True
        thread.start()
    
    def run(self) -> None:
        """Run the GUI application."""
        logger.info("Starting Mandelbrot GUI")
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        # Trigger initial render after GUI is ready
        initial_render_done = False
        
        # Main loop
        while dpg.is_dearpygui_running():
            # Render the initial Mandelbrot image after the first frame
            if not initial_render_done:
                logger.info("Triggering initial render")
                self._render_mandelbrot()
                initial_render_done = True
            
            dpg.render_dearpygui_frame()
        
        # Cleanup
        if self.calculation_thread and self.calculation_thread.is_alive():
            self.calculating = False
            self.calculation_thread.join(timeout=1.0)
        
        dpg.destroy_context()
        logger.info("GUI shutdown complete")


def create_mandelbrot_gui(width: int = 600, height: int = 400) -> MandelbrotGUI:
    """
    Create and setup Mandelbrot GUI.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        Configured MandelbrotGUI instance
    """
    gui = MandelbrotGUI(width, height)
    gui.setup_gui()
    return gui