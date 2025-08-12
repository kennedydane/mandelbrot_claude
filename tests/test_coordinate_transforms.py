import pytest
import numpy as np
from typing import Tuple


class TestPixelToComplexConversion:
    """Test pixel coordinate to complex plane conversion."""
    
    def test_pixel_to_complex_basic(self) -> None:
        """Test basic pixel to complex coordinate conversion."""
        from src.coordinate_transforms import pixel_to_complex
        
        # Simple case: 100x100 image, region [-1, 1] x [-1, 1]
        width, height = 100, 100
        x_min, x_max = -1.0, 1.0
        y_min, y_max = -1.0, 1.0
        
        # Center pixel should map to (0, 0)
        center_x, center_y = width // 2, height // 2
        complex_point = pixel_to_complex(center_x, center_y, width, height, x_min, x_max, y_min, y_max)
        
        assert abs(complex_point.real) < 0.05, f"Center x should be ~0, got {complex_point.real}"
        assert abs(complex_point.imag) < 0.05, f"Center y should be ~0, got {complex_point.imag}"
    
    def test_pixel_to_complex_corners(self) -> None:
        """Test conversion of corner pixels."""
        from src.coordinate_transforms import pixel_to_complex
        
        width, height = 10, 8
        x_min, x_max = -2.0, 2.0
        y_min, y_max = -1.0, 1.0
        
        # Top-left corner (0, 0) should map to (x_min, y_max)
        top_left = pixel_to_complex(0, 0, width, height, x_min, x_max, y_min, y_max)
        assert abs(top_left.real - x_min) < 0.01, f"Top-left real should be {x_min}, got {top_left.real}"
        assert abs(top_left.imag - y_max) < 0.01, f"Top-left imag should be {y_max}, got {top_left.imag}"
        
        # Bottom-right corner (width-1, height-1) should map to (x_max, y_min)
        bottom_right = pixel_to_complex(width-1, height-1, width, height, x_min, x_max, y_min, y_max)
        assert abs(bottom_right.real - x_max) < 0.01, f"Bottom-right real should be {x_max}, got {bottom_right.real}"
        assert abs(bottom_right.imag - y_min) < 0.01, f"Bottom-right imag should be {y_min}, got {bottom_right.imag}"
    
    def test_pixel_to_complex_aspect_ratio(self) -> None:
        """Test conversion with different aspect ratios."""
        from src.coordinate_transforms import pixel_to_complex
        
        # Wide image
        width, height = 200, 100
        x_min, x_max = -4.0, 4.0
        y_min, y_max = -2.0, 2.0
        
        center_point = pixel_to_complex(width//2, height//2, width, height, x_min, x_max, y_min, y_max)
        assert abs(center_point.real) < 0.05, "Wide image center real should be ~0"
        assert abs(center_point.imag) < 0.05, "Wide image center imag should be ~0"
        
        # Tall image
        width, height = 100, 200
        x_min, x_max = -2.0, 2.0
        y_min, y_max = -4.0, 4.0
        
        center_point = pixel_to_complex(width//2, height//2, width, height, x_min, x_max, y_min, y_max)
        assert abs(center_point.real) < 0.05, "Tall image center real should be ~0"
        assert abs(center_point.imag) < 0.05, "Tall image center imag should be ~0"
    
    def test_pixel_to_complex_edge_cases(self) -> None:
        """Test edge cases for pixel to complex conversion."""
        from src.coordinate_transforms import pixel_to_complex
        
        width, height = 5, 5
        x_min, x_max = 0.0, 1.0
        y_min, y_max = 0.0, 1.0
        
        # Test all corner and edge pixels
        test_cases = [
            (0, 0),      # Top-left
            (4, 0),      # Top-right  
            (0, 4),      # Bottom-left
            (4, 4),      # Bottom-right
            (2, 2),      # Center
        ]
        
        for px, py in test_cases:
            complex_point = pixel_to_complex(px, py, width, height, x_min, x_max, y_min, y_max)
            
            # Check bounds
            assert x_min <= complex_point.real <= x_max, \
                f"Real part {complex_point.real} out of bounds [{x_min}, {x_max}] for pixel ({px}, {py})"
            assert y_min <= complex_point.imag <= y_max, \
                f"Imag part {complex_point.imag} out of bounds [{y_min}, {y_max}] for pixel ({px}, {py})"


class TestComplexToPixelConversion:
    """Test complex plane to pixel coordinate conversion."""
    
    def test_complex_to_pixel_basic(self) -> None:
        """Test basic complex to pixel coordinate conversion."""
        from src.coordinate_transforms import complex_to_pixel
        
        width, height = 100, 100
        x_min, x_max = -1.0, 1.0
        y_min, y_max = -1.0, 1.0
        
        # Origin (0, 0) should map to center pixel
        origin = complex(0, 0)
        px, py = complex_to_pixel(origin, width, height, x_min, x_max, y_min, y_max)
        
        expected_x, expected_y = width // 2, height // 2
        assert abs(px - expected_x) <= 1, f"Origin x should be ~{expected_x}, got {px}"
        assert abs(py - expected_y) <= 1, f"Origin y should be ~{expected_y}, got {py}"
    
    def test_complex_to_pixel_corners(self) -> None:
        """Test conversion of complex corner points."""
        from src.coordinate_transforms import complex_to_pixel
        
        width, height = 10, 8
        x_min, x_max = -2.0, 2.0
        y_min, y_max = -1.0, 1.0
        
        # Complex corners should map to pixel corners
        test_cases = [
            (complex(x_min, y_max), 0, 0),           # Top-left
            (complex(x_max, y_max), width-1, 0),     # Top-right
            (complex(x_min, y_min), 0, height-1),    # Bottom-left
            (complex(x_max, y_min), width-1, height-1),  # Bottom-right
        ]
        
        for complex_point, expected_x, expected_y in test_cases:
            px, py = complex_to_pixel(complex_point, width, height, x_min, x_max, y_min, y_max)
            
            assert abs(px - expected_x) <= 1, \
                f"Complex {complex_point} x should be ~{expected_x}, got {px}"
            assert abs(py - expected_y) <= 1, \
                f"Complex {complex_point} y should be ~{expected_y}, got {py}"
    
    def test_complex_to_pixel_bounds_checking(self) -> None:
        """Test that pixel coordinates are within image bounds."""
        from src.coordinate_transforms import complex_to_pixel
        
        width, height = 50, 30
        x_min, x_max = -1.0, 1.0
        y_min, y_max = -0.5, 0.5
        
        # Test various complex points
        test_points = [
            complex(0, 0),      # Center
            complex(-0.5, 0.25),  # Inside region
            complex(0.8, -0.3),   # Near edge
            complex(-1.0, 0.5),   # Exact corner
        ]
        
        for point in test_points:
            px, py = complex_to_pixel(point, width, height, x_min, x_max, y_min, y_max)
            
            assert 0 <= px < width, f"Pixel x {px} out of bounds [0, {width}) for {point}"
            assert 0 <= py < height, f"Pixel y {py} out of bounds [0, {height}) for {point}"
    
    def test_complex_to_pixel_outside_bounds(self) -> None:
        """Test behavior with complex points outside the viewing region."""
        from src.coordinate_transforms import complex_to_pixel
        
        width, height = 10, 10
        x_min, x_max = -1.0, 1.0
        y_min, y_max = -1.0, 1.0
        
        # Points outside the region should still return pixel coordinates
        # (they might be clipped or extrapolated depending on implementation)
        outside_points = [
            complex(-2.0, 0),    # Left of region
            complex(2.0, 0),     # Right of region
            complex(0, -2.0),    # Below region
            complex(0, 2.0),     # Above region
        ]
        
        for point in outside_points:
            px, py = complex_to_pixel(point, width, height, x_min, x_max, y_min, y_max)
            
            # Should return some pixel coordinates (implementation may vary)
            assert isinstance(px, (int, float)), f"Should return numeric x coordinate for {point}"
            assert isinstance(py, (int, float)), f"Should return numeric y coordinate for {point}"


class TestRoundTripConversion:
    """Test round-trip conversions between pixel and complex coordinates."""
    
    def test_pixel_to_complex_to_pixel_roundtrip(self) -> None:
        """Test that pixel -> complex -> pixel gives back original coordinates."""
        from src.coordinate_transforms import pixel_to_complex, complex_to_pixel
        
        width, height = 20, 15
        x_min, x_max = -2.5, 1.5
        y_min, y_max = -1.2, 1.2
        
        # Test various pixel coordinates
        test_pixels = [
            (0, 0),
            (width//2, height//2),
            (width-1, height-1),
            (5, 3),
            (15, 10),
        ]
        
        for orig_x, orig_y in test_pixels:
            # Convert pixel -> complex -> pixel
            complex_point = pixel_to_complex(orig_x, orig_y, width, height, x_min, x_max, y_min, y_max)
            final_x, final_y = complex_to_pixel(complex_point, width, height, x_min, x_max, y_min, y_max)
            
            # Should get back approximately the same pixel coordinates
            assert abs(final_x - orig_x) <= 1, \
                f"Round-trip x failed: {orig_x} -> {complex_point} -> {final_x}"
            assert abs(final_y - orig_y) <= 1, \
                f"Round-trip y failed: {orig_y} -> {complex_point} -> {final_y}"
    
    def test_complex_to_pixel_to_complex_roundtrip(self) -> None:
        """Test that complex -> pixel -> complex gives back original coordinates.""" 
        from src.coordinate_transforms import pixel_to_complex, complex_to_pixel
        
        width, height = 30, 20
        x_min, x_max = -3.0, 2.0
        y_min, y_max = -1.5, 1.5
        
        # Test various complex coordinates within the region
        test_complex = [
            complex(0, 0),
            complex(-1.5, 0.75),
            complex(1.0, -0.5),
            complex(-0.25, 1.0),
            complex(1.5, -1.0),
        ]
        
        for orig_complex in test_complex:
            # Convert complex -> pixel -> complex
            px, py = complex_to_pixel(orig_complex, width, height, x_min, x_max, y_min, y_max)
            final_complex = pixel_to_complex(px, py, width, height, x_min, x_max, y_min, y_max)
            
            # Should get back approximately the same complex coordinates
            real_diff = abs(final_complex.real - orig_complex.real)
            imag_diff = abs(final_complex.imag - orig_complex.imag)
            
            # Allow some tolerance for rounding errors
            tolerance = max(abs(x_max - x_min) / width, abs(y_max - y_min) / height) * 2
            
            assert real_diff <= tolerance, \
                f"Round-trip real failed: {orig_complex} -> ({px}, {py}) -> {final_complex}"
            assert imag_diff <= tolerance, \
                f"Round-trip imag failed: {orig_complex} -> ({px}, {py}) -> {final_complex}"


class TestViewBounds:
    """Test view bounds and region management."""
    
    def test_view_bounds_creation(self) -> None:
        """Test creating view bounds objects."""
        from src.coordinate_transforms import ViewBounds
        
        bounds = ViewBounds(-2.0, 2.0, -1.0, 1.0, 800, 600)
        
        assert bounds.x_min == -2.0
        assert bounds.x_max == 2.0
        assert bounds.y_min == -1.0
        assert bounds.y_max == 1.0
        assert bounds.width == 800
        assert bounds.height == 600
    
    def test_view_bounds_properties(self) -> None:
        """Test computed properties of view bounds."""
        from src.coordinate_transforms import ViewBounds
        
        bounds = ViewBounds(-4.0, 4.0, -2.0, 2.0, 400, 200)
        
        # Test width and height properties
        assert abs(bounds.complex_width - 8.0) < 1e-10, f"Complex width should be 8.0, got {bounds.complex_width}"
        assert abs(bounds.complex_height - 4.0) < 1e-10, f"Complex height should be 4.0, got {bounds.complex_height}"
        
        # Test center property
        center = bounds.center
        assert abs(center.real) < 1e-10, f"Center real should be 0, got {center.real}"
        assert abs(center.imag) < 1e-10, f"Center imag should be 0, got {center.imag}"
        
        # Test aspect ratio
        pixel_aspect = bounds.width / bounds.height  # 400/200 = 2.0
        complex_aspect = bounds.complex_width / bounds.complex_height  # 8.0/4.0 = 2.0
        
        assert abs(pixel_aspect - complex_aspect) < 1e-10, "Aspect ratios should match"
    
    def test_view_bounds_pixel_to_complex(self) -> None:
        """Test pixel to complex conversion using ViewBounds."""
        from src.coordinate_transforms import ViewBounds
        
        bounds = ViewBounds(-1.0, 1.0, -0.5, 0.5, 100, 50)
        
        # Test center conversion
        center_complex = bounds.pixel_to_complex(50, 25)
        assert abs(center_complex.real) < 0.05, "Center should be near origin"
        assert abs(center_complex.imag) < 0.05, "Center should be near origin"
        
        # Test corner conversions
        top_left = bounds.pixel_to_complex(0, 0)
        assert abs(top_left.real - (-1.0)) < 0.05, "Top-left real coordinate"
        assert abs(top_left.imag - 0.5) < 0.05, "Top-left imag coordinate"
    
    def test_view_bounds_complex_to_pixel(self) -> None:
        """Test complex to pixel conversion using ViewBounds."""
        from src.coordinate_transforms import ViewBounds
        
        bounds = ViewBounds(-2.0, 2.0, -1.0, 1.0, 200, 100)
        
        # Test origin conversion
        px, py = bounds.complex_to_pixel(complex(0, 0))
        assert abs(px - 100) <= 1, f"Origin x should be ~100, got {px}"
        assert abs(py - 50) <= 1, f"Origin y should be ~50, got {py}"
        
        # Test corner conversion
        px, py = bounds.complex_to_pixel(complex(-2.0, 1.0))
        assert abs(px - 0) <= 1, "Top-left x should be ~0"
        assert abs(py - 0) <= 1, "Top-left y should be ~0"