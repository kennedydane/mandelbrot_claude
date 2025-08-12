#!/usr/bin/env python3
"""
Demo script showing different color palettes applied to Mandelbrot calculations.
"""

import numpy as np
from src.mandelbrot_core import mandelbrot_array
from src.color_mapping import iterations_to_rgb_array, get_available_palettes
from PIL import Image
import os


def create_mandelbrot_demo():
    """Create demo images showing different color palettes."""
    print("Mandelbrot Color Palette Demo")
    print("=" * 35)
    
    # Calculate a small Mandelbrot region
    width, height = 400, 300
    x_min, x_max = -2.5, 1.0
    y_min, y_max = -1.2, 1.2
    max_iter = 100
    
    print(f"\nCalculating {width}x{height} Mandelbrot array...")
    iterations = mandelbrot_array(width, height, x_min, x_max, y_min, y_max, max_iter)
    print(f"Iteration range: {iterations.min()} to {iterations.max()}")
    
    # Create images with different palettes
    palettes = get_available_palettes()
    print(f"\nGenerating images with {len(palettes)} palettes:")
    
    os.makedirs("demo_output", exist_ok=True)
    
    for palette in palettes:
        print(f"  • {palette}")
        
        # Convert iterations to RGB
        rgb_image = iterations_to_rgb_array(iterations, max_iter, palette=palette)
        
        # Save as PNG using PIL
        image = Image.fromarray(rgb_image, 'RGB')
        filename = f"demo_output/mandelbrot_{palette}.png"
        image.save(filename)
        
        print(f"    Saved: {filename}")
    
    # Create a color gradient sample for each palette
    print(f"\nGenerating color gradient samples:")
    gradient_width = 400
    gradient_height = 50
    
    for palette in palettes:
        # Create gradient from 1 to max_iter-1
        gradient = np.zeros((gradient_height, gradient_width), dtype=np.int32)
        for x in range(gradient_width):
            iter_value = int(1 + (max_iter - 2) * x / (gradient_width - 1))
            gradient[:, x] = iter_value
        
        # Convert to RGB
        rgb_gradient = iterations_to_rgb_array(gradient, max_iter, palette=palette)
        
        # Save gradient
        image = Image.fromarray(rgb_gradient, 'RGB')
        filename = f"demo_output/gradient_{palette}.png"
        image.save(filename)
        
        print(f"  • {palette}: {filename}")
    
    print(f"\nDemo complete! Check the 'demo_output' directory for images.")
    print("You can open these PNG files to see the different color palettes.")


def print_color_samples():
    """Print some color samples to terminal."""
    print("\nColor Samples (RGB values):")
    print("-" * 40)
    
    from src.color_mapping import iterations_to_rgb
    
    max_iter = 100
    test_iterations = [1, 10, 25, 50, 75, 90, 100]
    
    for palette in get_available_palettes():
        print(f"\n{palette.upper()} palette:")
        for iter_count in test_iterations:
            rgb = iterations_to_rgb(iter_count, max_iter, palette)
            if iter_count == max_iter:
                print(f"  {iter_count:3d} iterations: {rgb} (in set - black)")
            else:
                print(f"  {iter_count:3d} iterations: {rgb}")


if __name__ == "__main__":
    create_mandelbrot_demo()
    print_color_samples()