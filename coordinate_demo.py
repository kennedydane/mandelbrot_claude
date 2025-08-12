#!/usr/bin/env python3
"""
Demo script showing the improved coordinate-based interface.
"""

import numpy as np
from src.mandelbrot_core import mandelbrot_array, mandelbrot_array_centered


def main():
    print("Mandelbrot Array Coordinate Interface Demo")
    print("=" * 45)
    
    width, height = 20, 15
    max_iter = 100
    
    # Method 1: Direct coordinate specification (new, improved interface)
    print("\n1. Using direct coordinate bounds:")
    print(f"   Computing {width}x{height} region from (-2.5, -1.5) to (1.0, 1.5)")
    
    result1 = mandelbrot_array(
        width=width, 
        height=height,
        x_min=-2.5, x_max=1.0,    # Real axis: -2.5 to 1.0  
        y_min=-1.5, y_max=1.5,   # Imaginary axis: -1.5 to 1.5
        max_iter=max_iter
    )
    
    print(f"   Result shape: {result1.shape}")
    print(f"   Value range: {result1.min()} to {result1.max()}")
    pixels_in_set = np.sum(result1 == max_iter)
    print(f"   Pixels in set: {pixels_in_set}/{result1.size} ({100*pixels_in_set/result1.size:.1f}%)")
    
    # Method 2: Center/zoom interface (for convenience/backward compatibility)
    print("\n2. Using center/zoom interface (convenience function):")
    print(f"   Computing {width}x{height} centered at (-0.75, 0) with zoom=0.5")
    
    result2 = mandelbrot_array_centered(
        width=width,
        height=height, 
        center=complex(-0.75, 0),
        zoom=0.5,
        max_iter=max_iter
    )
    
    print(f"   Result shape: {result2.shape}")
    print(f"   Value range: {result2.min()} to {result2.max()}")
    pixels_in_set = np.sum(result2 == max_iter)
    print(f"   Pixels in set: {pixels_in_set}/{result2.size} ({100*pixels_in_set/result2.size:.1f}%)")
    
    # Method 3: Easy area selection (perfect for zoom functionality)
    print("\n3. Zooming into an interesting region:")
    print("   Selecting region around the 'seahorse valley' at (-0.75, 0.1)")
    
    # Define a small rectangular region around an interesting area
    zoom_x_min, zoom_x_max = -0.76, -0.74
    zoom_y_min, zoom_y_max = 0.09, 0.11
    
    result3 = mandelbrot_array(
        width=width,
        height=height,
        x_min=zoom_x_min, x_max=zoom_x_max,
        y_min=zoom_y_min, y_max=zoom_y_max,
        max_iter=max_iter
    )
    
    print(f"   Region: [{zoom_x_min}, {zoom_x_max}] x [{zoom_y_min}, {zoom_y_max}]")
    print(f"   Result shape: {result3.shape}")  
    print(f"   Value range: {result3.min()} to {result3.max()}")
    pixels_in_set = np.sum(result3 == max_iter)
    print(f"   Pixels in set: {pixels_in_set}/{result3.size} ({100*pixels_in_set/result3.size:.1f}%)")
    
    print("\nBenefits of coordinate-based interface:")
    print("• Direct specification of the exact region to compute")
    print("• No confusing zoom calculations or aspect ratio issues") 
    print("• Perfect for implementing area-selection zoom functionality")
    print("• Easy to understand and debug coordinate transformations")
    print("• Natural fit for mouse selection rectangles")


if __name__ == "__main__":
    main()