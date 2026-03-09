"""
Command registry for feimg.

Each image feature is implemented in its own module file so maintenance stays
simple and the command surface can grow incrementally.
"""

from . import border, clip, crop, overlay, pad, resize, rotate
from . import info, labeled, line, marker, new, oval, rect, text, ticks

__all__ = [
    "border",
    "clip",
    "crop",
    "info",
    "labeled",
    "line",
    "marker",
    "new",
    "oval",
    "overlay",
    "pad",
    "rect",
    "resize",
    "rotate",
    "text",
    "ticks",
]
