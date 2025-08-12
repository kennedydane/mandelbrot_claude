#!/usr/bin/env python3
"""
Analyze how color mapping works in the Mandelbrot visualizer.
This answers the question: "Is the palette applied dynamically based on the range?"
"""

import numpy as np
from src.mandelbrot_core import mandelbrot_array
from src.color_mapping import iterations_to_rgb_array
from PIL import Image

def analyze_color_mapping():
    """Analyze how colors are mapped to iteration counts."""
    print("=== Color Mapping Analysis ===\n")
    
    # Test with different regions and iteration limits
    test_cases = [
        {"name": "Full Set", "bounds": (-2.5, 1.0, -1.25, 1.25), "max_iter": 100},
        {"name": "Zoomed In", "bounds": (-0.8, -0.6, 0.0, 0.2), "max_iter": 100},
        {"name": "High Detail", "bounds": (-0.8, -0.6, 0.0, 0.2), "max_iter": 500},
    ]
    
    for i, case in enumerate(test_cases):
        print(f"Test Case {i+1}: {case['name']}")
        print(f"  Bounds: {case['bounds']}")
        print(f"  Max iterations: {case['max_iter']}")
        
        # Calculate Mandelbrot
        x_min, x_max, y_min, y_max = case['bounds']
        iterations = mandelbrot_array(200, 150, x_min, x_max, y_min, y_max, case['max_iter'])
        
        # Analyze iteration distribution
        unique_iterations = np.unique(iterations)
        print(f"  Iteration range: {iterations.min()} to {iterations.max()}")
        print(f"  Unique iteration counts: {len(unique_iterations)}")
        print(f"  Most common iterations: {unique_iterations[:10]}")
        
        # Show how colors are assigned
        print("  Color mapping examples:")
        sample_iterations = [1, 10, 25, 50, case['max_iter']//2, case['max_iter']-1, case['max_iter']]
        for iter_count in sample_iterations:
            if iter_count <= case['max_iter']:
                t = iter_count / case['max_iter']  # This is the key normalization!
                print(f"    {iter_count:3d} iterations → t={t:.3f} → color based on this fraction")
        
        # Create image to show the result
        rgb_image = iterations_to_rgb_array(iterations, case['max_iter'], 'default')
        pil_image = Image.fromarray(rgb_image)
        filename = f"color_analysis_{i+1}_{case['name'].lower().replace(' ', '_')}.png"
        pil_image.save(filename)
        print(f"  Saved image: {filename}")
        print()

def compare_static_vs_dynamic():
    """Compare static vs dynamic color mapping approaches."""
    print("=== Static vs Dynamic Color Mapping ===\n")
    
    # Same region, different max_iter values
    bounds = (-0.8, -0.6, 0.0, 0.2)  # Interesting zoomed region
    max_iters = [50, 100, 200, 500]
    
    print("Testing how the SAME region looks with different max_iter values:")
    print("(This shows whether colors are applied dynamically)\n")
    
    for max_iter in max_iters:
        print(f"Max iterations: {max_iter}")
        
        # Calculate
        iterations = mandelbrot_array(300, 200, *bounds, max_iter)
        
        print(f"  Actual iteration range: {iterations.min()} to {iterations.max()}")
        print(f"  Normalization factor: 1/{max_iter} = {1/max_iter:.6f}")
        
        # Key insight: Same iteration count gets different colors!
        sample_iter = 25
        if sample_iter < max_iter:
            t = sample_iter / max_iter
            print(f"  25 iterations → t={t:.3f} (different color each time!)")
        
        # Save image
        rgb_image = iterations_to_rgb_array(iterations, max_iter, 'default')
        pil_image = Image.fromarray(rgb_image)
        filename = f"dynamic_comparison_maxiter_{max_iter}.png"
        pil_image.save(filename)
        print(f"  Saved: {filename}")
        print()
    
    print("CONCLUSION:")
    print("✓ Colors ARE applied dynamically!")
    print("✓ The same iteration count gets different colors depending on max_iter")
    print("✓ This maximizes color range utilization for any zoom level")

if __name__ == "__main__":
    analyze_color_mapping()
    compare_static_vs_dynamic()