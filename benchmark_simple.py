#!/usr/bin/env python3
"""
Simple Mandelbrot parallel benchmark that works within Numba's constraints.
"""

import sys
import os  
import time
import numpy as np
from pathlib import Path

# Set thread count BEFORE importing numba modules
THREAD_COUNT = int(os.environ.get('BENCH_THREADS', os.cpu_count() or 1))
os.environ['NUMBA_NUM_THREADS'] = str(THREAD_COUNT)

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mandelbrot_core import mandelbrot_array

def single_benchmark():
    """Run a single benchmark with the configured thread count."""
    
    print(f"🔥 Mandelbrot Benchmark - {THREAD_COUNT} threads")
    print("=" * 40)
    
    # Test cases
    test_cases = [
        {
            "name": "Small (400x300, 100 iter)",
            "width": 400, "height": 300, "max_iter": 100,
            "bounds": (-2.5, 1.0, -1.25, 1.25)
        },
        {
            "name": "Medium (800x600, 200 iter)", 
            "width": 800, "height": 600, "max_iter": 200,
            "bounds": (-2.5, 1.0, -1.25, 1.25)
        },
        {
            "name": "Large (1200x900, 500 iter)",
            "width": 1200, "height": 900, "max_iter": 500,
            "bounds": (-2.5, 1.0, -1.25, 1.25)
        }
    ]
    
    use_parallel = THREAD_COUNT > 1
    mode = "parallel" if use_parallel else "serial"
    
    print(f"Mode: {mode}")
    print(f"CPU cores available: {os.cpu_count()}")
    print()
    
    for case in test_cases:
        print(f"📊 {case['name']}:")
        
        # Warm up Numba
        _ = mandelbrot_array(50, 50, -1, 1, -1, 1, 10, use_parallel)
        
        # Run benchmark
        times = []
        for run in range(3):
            start_time = time.time()
            
            result = mandelbrot_array(
                case["width"], case["height"],
                *case["bounds"], case["max_iter"],
                use_parallel
            )
            
            elapsed = time.time() - start_time
            times.append(elapsed)
            
        avg_time = np.mean(times)
        min_time = np.min(times)
        pixels = case["width"] * case["height"]
        pixels_per_sec = pixels / avg_time
        
        print(f"  Average: {avg_time:.3f}s ({pixels_per_sec:,.0f} pixels/sec)")
        print(f"  Best:    {min_time:.3f}s ({pixels / min_time:,.0f} pixels/sec)")
        print()

if __name__ == "__main__":
    try:
        single_benchmark()
    except Exception as e:
        print(f"❌ Benchmark error: {e}")
        import traceback
        traceback.print_exc()