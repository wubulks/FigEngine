# -*- coding: utf-8 -*-

"""
Project: FigEngine
File: consts.py
Author: Omarjan Obulkasim @ SYSU
Date: 2026/01/18
License: MIT License
Description: General constant library for FigEngine.
"""

from .logger import get_logger

# Logger setup
logger = get_logger(__name__)

class Consts:
    """
    A class to hold all the constants used in the FigEngine project.
    Constants should be organized here to avoid magic numbers/strings in the code.
    """
    
    # Image properties
    DEFAULT_IMAGE_WIDTH = 12  # Default width for generated images (inches)
    DEFAULT_IMAGE_HEIGHT = 9  # Default height for generated images (inches)
    DPI = 600  # Default DPI for printing
    DEFAULT_FONT_SIZE = 16  # Default font size for image labels and text
    REF_LEN = 1000

    # Layout constants
    MARGIN = 0.05  # Default margin (in ratio)
    GAP = 0.05  # Default gap between subplots (in ratio)

    # Unit conversion factors
    INCH_TO_MM = 25.4  # 1 inch = 25.4 mm
    CM_TO_INCH = 0.393701  # 1 cm = 0.393701 inches

    # Color constants
    COLOR_PRIMARY = "#3498db"  # Primary color for charts (blue)
    COLOR_SECONDARY = "#e74c3c"  # Secondary color for charts (red)
    COLOR_BACKGROUND = "#ffffff"  # Background color for plots
    DEFAULT_BACKGROUND = (255, 255, 255)


    # Logging
    LOG_LEVEL = "INFO"  # Default logging level

    MAX_IMAGE_PIXEL = 1_000_000_000