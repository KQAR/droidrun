"""
Coordinate conversion utilities.

Provides conversion between normalized coordinates and absolute pixel coordinates.
Normalized coordinate range: [0, 1000]
"""

from dataclasses import dataclass
from typing import Tuple

# Normalized coordinate range constant
NORMALIZED_RANGE = 1000


class CoordinateError(ValueError):
    """Error raised for invalid coordinate values."""
    pass


@dataclass
class ScreenSize:
    """
    Screen size data class.
    
    Attributes:
        width: Screen width in pixels
        height: Screen height in pixels
    """
    width: int
    height: int

    def __post_init__(self):
        """Validate screen size values."""
        if self.width <= 0:
            raise CoordinateError(f"Screen width must be positive, got {self.width}")
        if self.height <= 0:
            raise CoordinateError(f"Screen height must be positive, got {self.height}")

    @classmethod
    def from_device_context(cls, device_context: dict) -> "ScreenSize":
        """
        Create ScreenSize from device context.
        
        Args:
            device_context: Device context dict containing screen_bounds
            
        Returns:
            ScreenSize instance
            
        Raises:
            CoordinateError: If screen dimensions are invalid
        """
        screen_bounds = device_context.get("screen_bounds", {})
        width = screen_bounds.get("width", 1080)
        height = screen_bounds.get("height", 2400)
        
        if width <= 0 or height <= 0:
            raise CoordinateError(
                f"Invalid screen dimensions: {width}x{height}. "
                "Both width and height must be positive."
            )
        
        return cls(width=width, height=height)


def validate_normalized_coords(x: int, y: int, context: str = "") -> None:
    """
    Validate that normalized coordinates are within valid range [0, 1000].
    
    Args:
        x: Normalized X coordinate
        y: Normalized Y coordinate
        context: Optional context string for error messages
        
    Raises:
        CoordinateError: If coordinates are out of valid range
    """
    ctx_prefix = f"{context}: " if context else ""
    
    if not (0 <= x <= NORMALIZED_RANGE):
        raise CoordinateError(
            f"{ctx_prefix}X coordinate ({x}) out of valid range [0, {NORMALIZED_RANGE}]"
        )
    if not (0 <= y <= NORMALIZED_RANGE):
        raise CoordinateError(
            f"{ctx_prefix}Y coordinate ({y}) out of valid range [0, {NORMALIZED_RANGE}]"
        )


def normalized_to_absolute(
    norm_x: int,
    norm_y: int,
    screen_size: ScreenSize
) -> Tuple[int, int]:
    """
    Convert normalized coordinates to absolute pixel coordinates.
    
    Args:
        norm_x: Normalized X coordinate [0-1000]
        norm_y: Normalized Y coordinate [0-1000]
        screen_size: Screen size
        
    Returns:
        (abs_x, abs_y) tuple of absolute pixel coordinates
        
    Raises:
        CoordinateError: If normalized coordinates are out of valid range
    """
    validate_normalized_coords(norm_x, norm_y, "normalized_to_absolute")
    
    abs_x = int(norm_x * screen_size.width / NORMALIZED_RANGE)
    abs_y = int(norm_y * screen_size.height / NORMALIZED_RANGE)
    
    return abs_x, abs_y


def absolute_to_normalized(
    abs_x: int,
    abs_y: int,
    screen_size: ScreenSize
) -> Tuple[int, int]:
    """
    Convert absolute pixel coordinates to normalized coordinates.
    
    Args:
        abs_x: Absolute X coordinate in pixels
        abs_y: Absolute Y coordinate in pixels
        screen_size: Screen size
        
    Returns:
        (norm_x, norm_y) tuple of normalized coordinates [0-1000]
    """
    norm_x = int(abs_x * NORMALIZED_RANGE / screen_size.width)
    norm_y = int(abs_y * NORMALIZED_RANGE / screen_size.height)
    
    # Clamp to valid range
    norm_x = max(0, min(NORMALIZED_RANGE, norm_x))
    norm_y = max(0, min(NORMALIZED_RANGE, norm_y))
    
    return norm_x, norm_y


def validate_normalized_area(
    x1: int, y1: int, x2: int, y2: int, context: str = ""
) -> None:
    """
    Validate that normalized area coordinates are valid.
    
    Args:
        x1: Top-left X coordinate [0-1000]
        y1: Top-left Y coordinate [0-1000]
        x2: Bottom-right X coordinate [0-1000]
        y2: Bottom-right Y coordinate [0-1000]
        context: Optional context string for error messages
        
    Raises:
        CoordinateError: If coordinates are invalid
    """
    ctx_prefix = f"{context}: " if context else ""
    
    # Validate individual coordinates are in range
    validate_normalized_coords(x1, y1, f"{ctx_prefix}top-left")
    validate_normalized_coords(x2, y2, f"{ctx_prefix}bottom-right")
    
    # Validate area bounds
    if x1 > x2:
        raise CoordinateError(
            f"{ctx_prefix}Invalid area: x1 ({x1}) > x2 ({x2}). "
            "Top-left X must be <= bottom-right X"
        )
    if y1 > y2:
        raise CoordinateError(
            f"{ctx_prefix}Invalid area: y1 ({y1}) > y2 ({y2}). "
            "Top-left Y must be <= bottom-right Y"
        )


def normalized_area_to_center(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    screen_size: ScreenSize
) -> Tuple[int, int]:
    """
    Convert normalized area coordinates to center point absolute coordinates.
    
    Args:
        x1: Top-left normalized X coordinate [0-1000]
        y1: Top-left normalized Y coordinate [0-1000]
        x2: Bottom-right normalized X coordinate [0-1000]
        y2: Bottom-right normalized Y coordinate [0-1000]
        screen_size: Screen size
        
    Returns:
        (center_x, center_y) absolute pixel coordinates of area center
        
    Raises:
        CoordinateError: If area coordinates are invalid
    """
    validate_normalized_area(x1, y1, x2, y2, "normalized_area_to_center")
    
    # Calculate normalized center point
    center_norm_x = (x1 + x2) // 2
    center_norm_y = (y1 + y2) // 2
    
    return normalized_to_absolute(center_norm_x, center_norm_y, screen_size)


def bounds_to_normalized(
    bounds_str: str,
    screen_size: ScreenSize
) -> Tuple[int, int, int, int]:
    """
    Convert element bounds string to normalized coordinates.
    
    Args:
        bounds_str: Bounds string in format "left,top,right,bottom"
        screen_size: Screen size
        
    Returns:
        (norm_x1, norm_y1, norm_x2, norm_y2) normalized bounds coordinates
    """
    left, top, right, bottom = map(int, bounds_str.split(","))
    
    norm_x1, norm_y1 = absolute_to_normalized(left, top, screen_size)
    norm_x2, norm_y2 = absolute_to_normalized(right, bottom, screen_size)
    
    return norm_x1, norm_y1, norm_x2, norm_y2
