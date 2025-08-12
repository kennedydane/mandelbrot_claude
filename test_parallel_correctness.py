#!/usr/bin/env python3
"""
Test to verify parallel and serial Mandelbrot calculations produce identical results.
"""

import sys
import os
import numpy as np
from pathlib import Path

# Add src directory to path  
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_parallel_correctness():
    """Test that parallel and serial produce identical results."""
    print("🔍 Testing Parallel vs Serial Correctness")
    print("=" * 45)
    
    # Import after setting up path
    from mandelbrot_core import mandelbrot_array
    
    # Test parameters
    test_cases = [
        {"name": "Full Set", "width": 200, "height": 150, "bounds": (-2.5, 1.0, -1.25, 1.25), "max_iter": 100},
        {"name": "Zoomed Region", "width": 150, "height": 100, "bounds": (-0.8, -0.6, 0.0, 0.2), "max_iter": 200},
        {"name": "Edge Case", "width": 100, "height": 75, "bounds": (-0.1, 0.1, -0.1, 0.1), "max_iter": 50},
    ]
    
    # Set thread count for parallel mode
    os.environ['NUMBA_NUM_THREADS'] = str(min(4, os.cpu_count() or 1))
    
    all_passed = True
    
    for case in test_cases:
        print(f"Testing: {case['name']} ({case['width']}x{case['height']}, {case['max_iter']} iter)")
        
        # Calculate with serial mode
        serial_result = mandelbrot_array(
            case["width"], case["height"], 
            *case["bounds"], case["max_iter"],
            use_parallel=False
        )
        
        # Calculate with parallel mode  
        parallel_result = mandelbrot_array(
            case["width"], case["height"],
            *case["bounds"], case["max_iter"], 
            use_parallel=True
        )
        
        # Compare results
        if np.array_equal(serial_result, parallel_result):
            print(f"  ✅ PASS: Results are identical")
        else:
            print(f"  ❌ FAIL: Results differ")
            differences = np.sum(serial_result != parallel_result)
            total_pixels = case["width"] * case["height"] 
            print(f"     {differences}/{total_pixels} pixels differ ({differences/total_pixels*100:.2f}%)")
            print(f"     Serial range: {serial_result.min()}-{serial_result.max()}")
            print(f"     Parallel range: {parallel_result.min()}-{parallel_result.max()}")
            all_passed = False
        
        print()
    
    if all_passed:
        print("🎉 All tests passed! Parallel implementation is correct.")
        return True
    else:
        print("❌ Some tests failed. Parallel implementation has issues.")
        return False

if __name__ == "__main__":
    try:
        success = test_parallel_correctness()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)