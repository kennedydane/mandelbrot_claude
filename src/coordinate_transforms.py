"""
Coordinate transformation utilities for converting between pixel and complex coordinates.

This module provides functions to convert between:
- Pixel coordinates (x, y) in image space
- Complex coordinates (real + imag*i) in the mathematical plane

Used for area selection zooming functionality.
"""

from typing import Tuple
from loguru import logger


def pixel_to_complex(
    pixel_x: int,
    pixel_y: int,
    width: int,
    height: int,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float
) -> complex:
    """
    Convert pixel coordinates to complex plane coordinates.
    
    Args:
        pixel_x: X coordinate in pixel space (0 to width-1)
        pixel_y: Y coordinate in pixel space (0 to height-1)
        width: Image width in pixels
        height: Image height in pixels
        x_min: Minimum real coordinate of viewing region
        x_max: Maximum real coordinate of viewing region
        y_min: Minimum imaginary coordinate of viewing region
        y_max: Maximum imaginary coordinate of viewing region
        
    Returns:
        Complex number representing the coordinate in the mathematical plane
    """
    # Convert pixel coordinates to normalized coordinates [0, 1]
    norm_x = pixel_x / (width - 1) if width > 1 else 0.5
    norm_y = pixel_y / (height - 1) if height > 1 else 0.5
    
    # Map normalized coordinates to complex plane coordinates
    real_part = x_min + norm_x * (x_max - x_min)
    imag_part = y_max - norm_y * (y_max - y_min)  # Note: y is flipped (screen vs math coords)
    
    result = complex(real_part, imag_part)
    
    logger.debug(f"pixel_to_complex: ({pixel_x}, {pixel_y}) -> {result}")
    return result


def complex_to_pixel(
    complex_point: complex,
    width: int,
    height: int,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float
) -> Tuple[int, int]:
    """
    Convert complex plane coordinates to pixel coordinates.
    
    Args:
        complex_point: Complex number in the mathematical plane
        width: Image width in pixels
        height: Image height in pixels
        x_min: Minimum real coordinate of viewing region
        x_max: Maximum real coordinate of viewing region
        y_min: Minimum imaginary coordinate of viewing region
        y_max: Maximum imaginary coordinate of viewing region
        
    Returns:
        Tuple of (pixel_x, pixel_y) coordinates
    """
    # Normalize complex coordinates to [0, 1] range
    norm_x = (complex_point.real - x_min) / (x_max - x_min) if x_max != x_min else 0.5
    norm_y = (y_max - complex_point.imag) / (y_max - y_min) if y_max != y_min else 0.5  # Flip y
    
    # Convert to pixel coordinates
    pixel_x = int(round(norm_x * (width - 1))) if width > 1 else 0
    pixel_y = int(round(norm_y * (height - 1))) if height > 1 else 0
    
    # Clamp to valid pixel ranges
    pixel_x = max(0, min(width - 1, pixel_x))
    pixel_y = max(0, min(height - 1, pixel_y))
    
    logger.debug(f"complex_to_pixel: {complex_point} -> ({pixel_x}, {pixel_y})")
    return (pixel_x, pixel_y)


class ViewBounds:
    """
    Manages the viewing region bounds for coordinate transformations.
    
    This class encapsulates the relationship between pixel coordinates and
    complex plane coordinates, providing convenient methods for conversion
    and region management.
    """
    
    def __init__(
        self,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        width: int,
        height: int
    ):
        """
        Initialize view bounds.
        
        Args:
            x_min: Minimum real coordinate
            x_max: Maximum real coordinate
            y_min: Minimum imaginary coordinate
            y_max: Maximum imaginary coordinate
            width: Image width in pixels
            height: Image height in pixels
        """
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.width = width
        self.height = height
        
        logger.debug(f"ViewBounds created: [{x_min}, {x_max}] x [{y_min}, {y_max}], {width}x{height}")
    
    @property
    def complex_width(self) -> float:
        """Width of the complex plane region."""
        return self.x_max - self.x_min
    
    @property
    def complex_height(self) -> float:
        """Height of the complex plane region."""
        return self.y_max - self.y_min
    
    @property
    def center(self) -> complex:
        """Center point of the viewing region."""
        real_center = (self.x_min + self.x_max) / 2
        imag_center = (self.y_min + self.y_max) / 2
        return complex(real_center, imag_center)
    
    def pixel_to_complex(self, pixel_x: int, pixel_y: int) -> complex:
        """
        Convert pixel coordinates to complex coordinates using these bounds.
        
        Args:
            pixel_x: X coordinate in pixel space
            pixel_y: Y coordinate in pixel space
            
        Returns:
            Complex coordinate
        """
        return pixel_to_complex(
            pixel_x, pixel_y, self.width, self.height,
            self.x_min, self.x_max, self.y_min, self.y_max
        )
    
    def complex_to_pixel(self, complex_point: complex) -> Tuple[int, int]:
        """
        Convert complex coordinates to pixel coordinates using these bounds.
        
        Args:
            complex_point: Complex coordinate
            
        Returns:
            Tuple of (pixel_x, pixel_y)
        """
        return complex_to_pixel(
            complex_point, self.width, self.height,
            self.x_min, self.x_max, self.y_min, self.y_max
        )
    
    def zoom_to_region(
        self, 
        top_left: Tuple[int, int], 
        bottom_right: Tuple[int, int]
    ) -> 'ViewBounds':
        """
        Create new ViewBounds zoomed to the specified pixel region.
        
        Args:
            top_left: (pixel_x, pixel_y) of top-left corner
            bottom_right: (pixel_x, pixel_y) of bottom-right corner
            
        Returns:
            New ViewBounds representing the zoomed region
        """
        # Convert pixel coordinates to complex coordinates
        top_left_complex = self.pixel_to_complex(top_left[0], top_left[1])
        bottom_right_complex = self.pixel_to_complex(bottom_right[0], bottom_right[1])
        
        # Note: screen coordinates have y increasing downward, but complex plane has y increasing upward
        new_x_min = min(top_left_complex.real, bottom_right_complex.real)
        new_x_max = max(top_left_complex.real, bottom_right_complex.real)
        new_y_min = min(top_left_complex.imag, bottom_right_complex.imag)
        new_y_max = max(top_left_complex.imag, bottom_right_complex.imag)
        
        logger.debug(f"zoom_to_region: pixels ({top_left}, {bottom_right}) -> complex [{new_x_min}, {new_x_max}] x [{new_y_min}, {new_y_max}]")
        
        return ViewBounds(new_x_min, new_x_max, new_y_min, new_y_max, self.width, self.height)
    
    def __repr__(self) -> str:
        """String representation of ViewBounds."""
        return f"ViewBounds([{self.x_min}, {self.x_max}] x [{self.y_min}, {self.y_max}], {self.width}x{self.height})"