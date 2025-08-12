#!/usr/bin/env python3
"""
Test the Mandelbrot calculation and save output to verify it's working.
"""

import sys
from pathlib import Path

# Add src directory
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mandelbrot_core import mandelbrot_array
from color_mapping import iterations_to_rgb_array
from PIL import Image
import numpy as np


def main():
    print("Testing Mandelbrot calculation...")
    
    # Same parameters as GUI
    width, height = 400, 300
    x_min, x_max = -2.5, 1.0
    y_min, y_max = -1.25, 1.25
    max_iter = 100
    
    print(f"Calculating {width}x{height} Mandelbrot set...")
    print(f"Region: [{x_min}, {x_max}] x [{y_min}, {y_max}]")
    print(f"Max iterations: {max_iter}")
    
    # Calculate
    iterations = mandelbrot_array(width, height, x_min, x_max, y_min, y_max, max_iter)
    print(f"Iteration range: {iterations.min()} to {iterations.max()}")
    
    # Convert to RGB
    rgb_image = iterations_to_rgb_array(iterations, max_iter, 'default')
    print(f"RGB image shape: {rgb_image.shape}, dtype: {rgb_image.dtype}")
    print(f"RGB range: {rgb_image.min()} to {rgb_image.max()}")
    
    # Save as PNG
    pil_image = Image.fromarray(rgb_image, 'RGB')
    output_file = "test_mandelbrot_output.png"
    pil_image.save(output_file)
    
    print(f"Saved Mandelbrot image to: {output_file}")
    print("You can open this file to see if the calculation is working correctly.")
    
    # Check if we have some variety in the image
    unique_colors = len(np.unique(rgb_image.reshape(-1, 3), axis=0))
    print(f"Number of unique colors: {unique_colors}")
    
    if unique_colors > 100:
        print("✓ Image has good color variety - calculation appears correct")
    else:
        print("⚠ Image might be too uniform - check calculation")


if __name__ == "__main__":
    main()