#!/usr/bin/env python3
"""
Debug script to test Mandelbrot calculations with detailed logging.
"""

import argparse
from src.logger_config import setup_logging
from src.mandelbrot_core import mandelbrot_iterations


def main():
    parser = argparse.ArgumentParser(description="Debug Mandelbrot calculations")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    setup_logging(debug=args.debug)
    
    # Test problematic points from failing tests
    test_points = [
        (complex(0, 1), 10, "Point (0,1) should escape quickly"),
        (complex(-0.74529, 0.11307), 100, "Boundary point should escape"),
        (complex(0, 0), 10, "Origin should not escape"),
        (complex(1, 0), 10, "Point (1,0) should escape quickly"),
    ]
    
    print("Testing Mandelbrot iteration calculations:")
    print("=" * 50)
    
    for c, max_iter, description in test_points:
        print(f"\n{description}")
        print(f"Testing c={c} with max_iter={max_iter}")
        result = mandelbrot_iterations(c, max_iter)
        print(f"Result: {result} iterations")


if __name__ == "__main__":
    main()