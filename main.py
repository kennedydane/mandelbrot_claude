#!/usr/bin/env python3
"""
Main entry point for the Mandelbrot Set Visualizer.

Usage:
    python main.py [--debug] [--width WIDTH] [--height HEIGHT]
"""

import argparse
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from logger_config import setup_logging
from mandelbrot_gui import create_mandelbrot_gui


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Interactive Mandelbrot Set Visualizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with default settings
  python main.py --debug            # Run with debug logging
  python main.py --width 1024 --height 768  # Custom resolution
  
Controls:
  • Click and drag to select an area to zoom into
  • Use the control panel to adjust parameters
  • Reset View button returns to the full Mandelbrot set
  • Zoom Out button enlarges the current view
        """
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--width',
        type=int,
        default=800,
        help='Image width in pixels (default: 800)'
    )
    
    parser.add_argument(
        '--height', 
        type=int,
        default=600,
        help='Image height in pixels (default: 600)'
    )
    
    parser.add_argument(
        '--threads',
        type=int,
        default=0,
        help='Number of threads for parallel processing (0=auto-detect, 1=serial mode, default: 0)'
    )
    
    return parser.parse_args()


def main():
    """Main application entry point."""
    args = parse_arguments()
    
    # Setup logging
    setup_logging(debug=args.debug)
    
    # Configure threading
    import os
    if args.threads == 0:
        # Auto-detect CPU cores
        thread_count = os.cpu_count() or 1
        use_parallel = True
    elif args.threads == 1:
        # Serial mode explicitly requested
        thread_count = 1
        use_parallel = False
    else:
        # Specific thread count requested
        thread_count = max(1, args.threads)
        use_parallel = True
    
    # Set Numba thread count
    os.environ['NUMBA_NUM_THREADS'] = str(thread_count)
    
    from loguru import logger
    mode = "parallel" if use_parallel else "serial"
    logger.info(f"Starting Mandelbrot visualizer in {mode} mode with {thread_count} threads")
    
    try:
        # Create and run GUI
        gui = create_mandelbrot_gui(args.width, args.height, use_parallel=use_parallel)
        gui.run()
        
    except KeyboardInterrupt:
        print("\\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Application error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
