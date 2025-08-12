"""
Core Mandelbrot set calculation functions with Numba optimization.
"""

import numpy as np
import numba as nb
from typing import Tuple
from loguru import logger


def mandelbrot_iterations(c: complex, max_iter: int) -> int:
    """
    Calculate the number of iterations for a single complex point.
    
    Args:
        c: Complex number to test
        max_iter: Maximum number of iterations to perform
        
    Returns:
        Number of iterations before escape, or max_iter if point doesn't escape
    """
    logger.debug(f"Computing iterations for c={c}, max_iter={max_iter}")
    
    z = complex(0, 0)
    
    for i in range(1, max_iter + 1):
        if abs(z) > 2.0:
            logger.debug(f"Point {c} escaped at iteration {i-1}, |z|={abs(z)}")
            return i - 1
        logger.debug(f"  i={i}: z={z}, |z|={abs(z)}")
        z = z * z + c
    
    logger.debug(f"Point {c} did not escape after {max_iter} iterations")
    return max_iter


@nb.jit(nopython=True) 
def _mandelbrot_iterations_fast(c: complex, max_iter: int) -> int:
    """Fast numba-compiled version without logging."""
    z = complex(0, 0)
    
    for i in range(1, max_iter + 1):
        if abs(z) > 2.0:
            return i - 1
        z = z * z + c
    
    return max_iter


@nb.jit(nopython=True)
def _mandelbrot_kernel(
    width: int, 
    height: int, 
    x_min: float, 
    x_max: float, 
    y_min: float, 
    y_max: float,
    max_iter: int
) -> np.ndarray:
    """
    Numba-optimized kernel for computing Mandelbrot set over a grid.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels  
        x_min, x_max: Real axis bounds
        y_min, y_max: Imaginary axis bounds
        max_iter: Maximum iterations per point
        
    Returns:
        2D array of iteration counts
    """
    result = np.zeros((height, width), dtype=np.int32)
    
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height
    
    for row in range(height):
        for col in range(width):
            # Map pixel coordinates to complex plane
            real = x_min + col * x_step
            imag = y_max - row * y_step  # Flip y-axis for screen coordinates
            c = complex(real, imag)
            
            # Calculate iterations for this point
            result[row, col] = _mandelbrot_iterations_fast(c, max_iter)
    
    return result


def mandelbrot_array(
    width: int, 
    height: int, 
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    max_iter: int
) -> np.ndarray:
    """
    Calculate Mandelbrot set over a rectangular region.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        x_min: Left boundary of complex plane region (real axis)
        x_max: Right boundary of complex plane region (real axis)
        y_min: Bottom boundary of complex plane region (imaginary axis)
        y_max: Top boundary of complex plane region (imaginary axis)
        max_iter: Maximum iterations per point
        
    Returns:
        2D numpy array of iteration counts with shape (height, width)
    """
    logger.debug(f"Computing Mandelbrot array {width}x{height} for region "
                f"[{x_min:.6f}, {x_max:.6f}] x [{y_min:.6f}, {y_max:.6f}]")
    
    return _mandelbrot_kernel(width, height, x_min, x_max, y_min, y_max, max_iter)


def mandelbrot_array_centered(
    width: int, 
    height: int, 
    center: complex, 
    zoom: float, 
    max_iter: int
) -> np.ndarray:
    """
    Calculate Mandelbrot set using center and zoom (convenience function).
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        center: Complex number at center of view
        zoom: Zoom level (higher = more zoomed in)  
        max_iter: Maximum iterations per point
        
    Returns:
        2D numpy array of iteration counts with shape (height, width)
    """
    # Calculate viewing bounds based on center and zoom
    # Base view shows roughly -2 to 2 on both axes
    base_width = 4.0
    base_height = 4.0
    
    # Adjust for aspect ratio
    aspect_ratio = width / height
    if aspect_ratio > 1:
        view_width = base_width / zoom
        view_height = base_height / (zoom * aspect_ratio)
    else:
        view_width = base_width * aspect_ratio / zoom
        view_height = base_height / zoom
    
    # Calculate bounds
    x_min = center.real - view_width / 2
    x_max = center.real + view_width / 2
    y_min = center.imag - view_height / 2
    y_max = center.imag + view_height / 2
    
    return mandelbrot_array(width, height, x_min, x_max, y_min, y_max, max_iter)