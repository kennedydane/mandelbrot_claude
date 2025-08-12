"""
Logging configuration for the Mandelbrot visualizer.
"""

import sys
from loguru import logger


def setup_logging(debug: bool = False) -> None:
    """
    Configure loguru logging based on debug flag.
    
    Args:
        debug: If True, enable DEBUG level logging with detailed output
    """
    # Remove default logger
    logger.remove()
    
    if debug:
        # Debug mode: detailed logging to stderr
        logger.add(
            sys.stderr,
            level="DEBUG", 
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            colorize=True
        )
        logger.debug("Debug logging enabled")
    else:
        # Normal mode: info and above to stderr
        logger.add(
            sys.stderr,
            level="INFO",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            colorize=True
        )