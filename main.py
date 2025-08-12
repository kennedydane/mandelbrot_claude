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
    
    return parser.parse_args()


def main():
    """Main application entry point."""
    args = parse_arguments()
    
    # Setup logging
    setup_logging(debug=args.debug)
    
    try:
        # Create and run GUI
        gui = create_mandelbrot_gui(args.width, args.height)
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
