"""
Color mapping functions for converting Mandelbrot iteration counts to RGB colors.
"""

import numpy as np
import math
from typing import Tuple, List
from loguru import logger


# Define color palettes
_PALETTES = {
    'default': {
        'name': 'Classic Blue-Orange',
        'description': 'Traditional Mandelbrot colors with blue to orange gradient',
    },
    'hot': {
        'name': 'Hot Colors', 
        'description': 'Black-red-orange-yellow-white heat map',
    },
    'cool': {
        'name': 'Cool Colors',
        'description': 'Blue-cyan-green gradient',
    },
    'grayscale': {
        'name': 'Grayscale',
        'description': 'Simple black to white gradient',
    },
    'rainbow': {
        'name': 'Rainbow',
        'description': 'Full spectrum rainbow colors',
    }
}


def get_available_palettes() -> List[str]:
    """
    Get list of available color palette names.
    
    Returns:
        List of palette name strings
    """
    return list(_PALETTES.keys())


def iterations_to_rgb(iterations: int, max_iter: int, palette: str = 'default') -> Tuple[int, int, int]:
    """
    Convert a single iteration count to RGB color.
    
    Args:
        iterations: Number of iterations before escape (1 to max_iter)
        max_iter: Maximum possible iterations
        palette: Color palette name
        
    Returns:
        RGB tuple (r, g, b) with values 0-255
        
    Raises:
        ValueError: If palette name is not recognized
    """
    if palette not in _PALETTES:
        available = ', '.join(get_available_palettes())
        raise ValueError(f"Unknown palette '{palette}'. Available: {available}")
    
    logger.debug(f"Converting iterations={iterations} to RGB using palette='{palette}'")
    
    # Points in the set are always black
    if iterations >= max_iter:
        return (0, 0, 0)
    
    # Normalize iteration count to [0, 1]
    t = iterations / max_iter
    
    # Apply palette-specific color mapping
    if palette == 'default':
        return _default_palette(t)
    elif palette == 'hot':
        return _hot_palette(t)
    elif palette == 'cool':
        return _cool_palette(t)
    elif palette == 'grayscale':
        return _grayscale_palette(t)
    elif palette == 'rainbow':
        return _rainbow_palette(t)
    else:
        # Fallback (should never reach here due to check above)
        return _default_palette(t)


def iterations_to_rgb_array(
    iterations: np.ndarray, 
    max_iter: int, 
    palette: str = 'default'
) -> np.ndarray:
    """
    Convert array of iteration counts to RGB image.
    
    Args:
        iterations: 2D array of iteration counts
        max_iter: Maximum possible iterations
        palette: Color palette name
        
    Returns:
        3D numpy array of shape (height, width, 3) with RGB values (0-255)
        
    Raises:
        ValueError: If palette name is not recognized
    """
    if palette not in _PALETTES:
        available = ', '.join(get_available_palettes())
        raise ValueError(f"Unknown palette '{palette}'. Available: {available}")
    
    logger.debug(f"Converting {iterations.shape} iteration array to RGB using palette='{palette}'")
    
    height, width = iterations.shape
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Process each row to minimize function call overhead
    for row in range(height):
        for col in range(width):
            iter_count = iterations[row, col]
            # Direct palette application without additional logging per pixel
            rgb = _apply_palette_direct(iter_count, max_iter, palette)
            rgb_image[row, col] = rgb
    
    return rgb_image


def _apply_palette_direct(iterations: int, max_iter: int, palette: str) -> Tuple[int, int, int]:
    """Apply palette without debug logging for array processing."""
    # Points in the set are always black
    if iterations >= max_iter:
        return (0, 0, 0)
    
    # Normalize iteration count to [0, 1]
    t = iterations / max_iter
    
    # Apply palette-specific color mapping
    if palette == 'default':
        return _default_palette(t)
    elif palette == 'hot':
        return _hot_palette(t)
    elif palette == 'cool':
        return _cool_palette(t)
    elif palette == 'grayscale':
        return _grayscale_palette(t)
    elif palette == 'rainbow':
        return _rainbow_palette(t)
    else:
        return _default_palette(t)


def _default_palette(t: float) -> Tuple[int, int, int]:
    """Default blue-orange palette."""
    # Smooth gradient from dark blue through cyan to orange/yellow
    if t < 0.25:
        # Dark blue to blue
        factor = t / 0.25
        r = int(factor * 0)
        g = int(factor * 50)
        b = int(100 + factor * 155)
    elif t < 0.5:
        # Blue to cyan
        factor = (t - 0.25) / 0.25
        r = int(factor * 0)
        g = int(50 + factor * 205)
        b = 255
    elif t < 0.75:
        # Cyan to yellow
        factor = (t - 0.5) / 0.25
        r = int(factor * 255)
        g = 255
        b = int(255 - factor * 255)
    else:
        # Yellow to orange/red
        factor = (t - 0.75) / 0.25
        r = 255
        g = int(255 - factor * 100)
        b = int(factor * 50)
    
    return (r, g, b)


def _hot_palette(t: float) -> Tuple[int, int, int]:
    """Hot colors palette (black-red-orange-yellow-white)."""
    if t < 0.33:
        # Black to red
        factor = t / 0.33
        r = int(factor * 255)
        g = 0
        b = 0
    elif t < 0.66:
        # Red to orange/yellow
        factor = (t - 0.33) / 0.33
        r = 255
        g = int(factor * 255)
        b = 0
    else:
        # Orange to white
        factor = (t - 0.66) / 0.34
        r = 255
        g = 255
        b = int(factor * 255)
    
    return (r, g, b)


def _cool_palette(t: float) -> Tuple[int, int, int]:
    """Cool colors palette (blue-cyan-green)."""
    if t < 0.5:
        # Dark blue to cyan
        factor = t / 0.5
        r = 0
        g = int(factor * 255)
        b = int(100 + factor * 155)
    else:
        # Cyan to green
        factor = (t - 0.5) / 0.5
        r = 0
        g = 255
        b = int(255 - factor * 255)
    
    return (r, g, b)


def _grayscale_palette(t: float) -> Tuple[int, int, int]:
    """Simple grayscale palette."""
    value = int(t * 255)
    return (value, value, value)


def _rainbow_palette(t: float) -> Tuple[int, int, int]:
    """Rainbow spectrum palette."""
    # Use HSV color space for smooth rainbow
    hue = t * 360  # Full spectrum
    saturation = 1.0
    value = 1.0
    
    # Convert HSV to RGB
    h = hue / 60
    c = value * saturation
    x = c * (1 - abs((h % 2) - 1))
    m = value - c
    
    if 0 <= h < 1:
        r_prime, g_prime, b_prime = c, x, 0
    elif 1 <= h < 2:
        r_prime, g_prime, b_prime = x, c, 0
    elif 2 <= h < 3:
        r_prime, g_prime, b_prime = 0, c, x
    elif 3 <= h < 4:
        r_prime, g_prime, b_prime = 0, x, c
    elif 4 <= h < 5:
        r_prime, g_prime, b_prime = x, 0, c
    else:
        r_prime, g_prime, b_prime = c, 0, x
    
    r = int((r_prime + m) * 255)
    g = int((g_prime + m) * 255)
    b = int((b_prime + m) * 255)
    
    return (r, g, b)