#!/usr/bin/env python3
"""
Benchmark script to compare serial vs parallel Mandelbrot performance.
"""

import sys
import os
import time
import numpy as np
import subprocess
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mandelbrot_core import mandelbrot_array
from color_mapping import iterations_to_rgb_array

def benchmark_mandelbrot():
    """Benchmark serial vs parallel Mandelbrot performance."""
    print("🔥 Mandelbrot Parallel Performance Benchmark")
    print("=" * 50)
    
    # Test cases with varying complexity
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
        },
        {
            "name": "Zoomed Detail (800x600, 1000 iter)",
            "width": 800, "height": 600, "max_iter": 1000,
            "bounds": (-0.8, -0.6, 0.0, 0.2)
        }
    ]
    
    # Available thread counts to test
    thread_counts = [1, 2, 4, 8, 16]
    max_threads = os.cpu_count() or 1
    thread_counts = [t for t in thread_counts if t <= max_threads]
    
    print(f"CPU cores detected: {max_threads}")
    print(f"Testing thread counts: {thread_counts}")
    print()
    
    results = []
    
    for case in test_cases:
        print(f"📊 Test Case: {case['name']}")
        print("-" * 40)
        
        case_results = {"case": case["name"], "results": []}
        
        for threads in thread_counts:
            # Configure threading
            os.environ['NUMBA_NUM_THREADS'] = str(threads)
            use_parallel = threads > 1
            
            print(f"  Threads: {threads:2d} ({'parallel' if use_parallel else 'serial ':8s})", end=" ... ")
            
            # Warm up Numba compilation (first run is always slow)
            _ = mandelbrot_array(50, 50, -1, 1, -1, 1, 10, use_parallel)
            
            # Benchmark multiple runs
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
            
            # Statistics
            avg_time = np.mean(times)
            min_time = np.min(times)
            pixels = case["width"] * case["height"]
            pixels_per_sec = pixels / avg_time
            
            case_results["results"].append({
                "threads": threads,
                "avg_time": avg_time,
                "min_time": min_time,
                "pixels_per_sec": pixels_per_sec,
                "use_parallel": use_parallel
            })
            
            print(f"{avg_time:6.3f}s  ({pixels_per_sec:9,.0f} pixels/sec)")
        
        results.append(case_results)
        print()
    
    # Performance Analysis
    print("🚀 Performance Analysis")
    print("=" * 50)
    
    for case_result in results:
        print(f"\n{case_result['case']}:")
        
        serial_result = case_result["results"][0]  # First result is always serial (1 thread)
        serial_time = serial_result["avg_time"]
        serial_perf = serial_result["pixels_per_sec"]
        
        print(f"  Serial baseline: {serial_time:.3f}s ({serial_perf:,.0f} pixels/sec)")
        print("  Parallel speedup:")
        
        best_speedup = 1.0
        best_threads = 1
        
        for result in case_result["results"]:
            if result["threads"] > 1:
                speedup = serial_time / result["avg_time"]
                efficiency = speedup / result["threads"] * 100
                
                if speedup > best_speedup:
                    best_speedup = speedup
                    best_threads = result["threads"]
                
                print(f"    {result['threads']:2d} threads: {speedup:5.2f}x faster "
                      f"({efficiency:4.1f}% efficiency) - {result['pixels_per_sec']:,.0f} pixels/sec")
        
        print(f"  🏆 Best: {best_threads} threads with {best_speedup:.2f}x speedup")
    
    print(f"\n💡 Recommendations:")
    if max_threads >= 4:
        print(f"  • Use parallel mode (--threads 0) for best performance")
        print(f"  • Your {max_threads}-core CPU should provide significant speedup")
        print(f"  • For high iteration counts (>500), parallel scaling is excellent")
    else:
        print(f"  • Your {max_threads}-core CPU has limited parallel benefit")  
        print(f"  • Parallel mode may still help with high iteration counts")
        print(f"  • Consider --threads 1 for simple calculations")
    
    print(f"\n🔧 Usage Examples:")
    print(f"  python main.py --threads 0     # Auto-detect cores (recommended)")
    print(f"  python main.py --threads 1     # Force serial mode") 
    print(f"  python main.py --threads 4     # Force 4 threads")
    print(f"  python main.py --debug         # Show detailed timing info")

def verify_correctness():
    """Verify that parallel and serial give identical results."""
    print("\n🔍 Correctness Verification")
    print("=" * 30)
    
    # Test parameters
    width, height = 200, 150
    bounds = (-1.0, 0.0, -0.5, 0.5)
    max_iter = 100
    
    print(f"Computing {width}x{height} region with {max_iter} iterations...")
    
    # Compute with serial
    os.environ['NUMBA_NUM_THREADS'] = '1'
    serial_result = mandelbrot_array(width, height, *bounds, max_iter, use_parallel=False)
    
    # Compute with parallel
    os.environ['NUMBA_NUM_THREADS'] = str(min(4, os.cpu_count() or 1))
    parallel_result = mandelbrot_array(width, height, *bounds, max_iter, use_parallel=True)
    
    # Compare results
    if np.array_equal(serial_result, parallel_result):
        print("✅ PASS: Serial and parallel results are identical")
        return True
    else:
        differences = np.sum(serial_result != parallel_result)
        total_pixels = width * height
        print(f"❌ FAIL: {differences}/{total_pixels} pixels differ")
        print(f"Serial range: {serial_result.min()}-{serial_result.max()}")
        print(f"Parallel range: {parallel_result.min()}-{parallel_result.max()}")
        return False

if __name__ == "__main__":
    try:
        # Run correctness check first
        if verify_correctness():
            # Run performance benchmark
            benchmark_mandelbrot()
        else:
            print("❌ Correctness verification failed - skipping benchmark")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Benchmark interrupted by user")
    except Exception as e:
        print(f"❌ Benchmark error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)