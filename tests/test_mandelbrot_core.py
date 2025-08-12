import pytest
import numpy as np
from typing import Tuple


class TestMandelbrotIteration:
    """Test basic Mandelbrot iteration functionality."""
    
    def test_mandelbrot_iteration_known_inside_point(self) -> None:
        """Test that a known point inside the set doesn't escape."""
        c = complex(0, 0)  # Origin is in the Mandelbrot set
        max_iter = 100
        
        # This will be implemented in mandelbrot_core.py
        from src.mandelbrot_core import mandelbrot_iterations
        
        result = mandelbrot_iterations(c, max_iter)
        assert result == max_iter, f"Origin should not escape, got {result} iterations"
    
    def test_mandelbrot_iteration_known_outside_point(self) -> None:
        """Test that a known point outside the set escapes quickly."""
        c = complex(2, 2)  # Clearly outside the set
        max_iter = 100
        
        from src.mandelbrot_core import mandelbrot_iterations
        
        result = mandelbrot_iterations(c, max_iter)
        assert result < max_iter, f"Point (2,2) should escape quickly, got {result} iterations"
        assert result <= 2, f"Point (2,2) should escape in ≤2 iterations, got {result}"
    
    def test_mandelbrot_iteration_boundary_point(self) -> None:
        """Test a point that actually escapes after several iterations."""
        c = complex(-0.75, 0.1)  # Known point that escapes
        max_iter = 100
        
        from src.mandelbrot_core import mandelbrot_iterations
        
        result = mandelbrot_iterations(c, max_iter)
        # This point should escape but not immediately  
        assert 2 < result < max_iter, f"Boundary point should take >2 but <max iterations, got {result}"
    
    def test_mandelbrot_iteration_max_iterations_reached(self) -> None:
        """Test that max_iterations parameter is respected."""
        c = complex(0, 0)  # Point that won't escape
        max_iter = 50
        
        from src.mandelbrot_core import mandelbrot_iterations
        
        result = mandelbrot_iterations(c, max_iter)
        assert result == max_iter, f"Should return max_iter={max_iter} when not escaping"
    
    def test_mandelbrot_iteration_escape_radius(self) -> None:
        """Test that escape occurs when |z| > 2."""
        c = complex(1, 1)  # Will escape quickly
        max_iter = 100
        
        from src.mandelbrot_core import mandelbrot_iterations
        
        result = mandelbrot_iterations(c, max_iter)
        assert result < 10, f"Point (1,1) should escape quickly, got {result} iterations"


class TestMandelbrotVectorized:
    """Test vectorized Mandelbrot calculations."""
    
    def test_mandelbrot_array_shape(self) -> None:
        """Test that output array has correct shape."""
        width, height = 10, 8
        x_min, x_max = -2.0, 2.0
        y_min, y_max = -2.0, 2.0
        max_iter = 100
        
        from src.mandelbrot_core import mandelbrot_array
        
        result = mandelbrot_array(width, height, x_min, x_max, y_min, y_max, max_iter)
        assert result.shape == (height, width), f"Expected shape ({height}, {width}), got {result.shape}"
    
    def test_mandelbrot_array_data_type(self) -> None:
        """Test that output array has correct data type."""
        width, height = 5, 5
        x_min, x_max = -1.0, 1.0
        y_min, y_max = -1.0, 1.0
        max_iter = 100
        
        from src.mandelbrot_core import mandelbrot_array
        
        result = mandelbrot_array(width, height, x_min, x_max, y_min, y_max, max_iter)
        assert result.dtype == np.int32, f"Expected int32 dtype, got {result.dtype}"
    
    def test_mandelbrot_array_value_range(self) -> None:
        """Test that all values are within expected range."""
        width, height = 10, 10
        x_min, x_max = -2.0, 2.0
        y_min, y_max = -2.0, 2.0
        max_iter = 50
        
        from src.mandelbrot_core import mandelbrot_array
        
        result = mandelbrot_array(width, height, x_min, x_max, y_min, y_max, max_iter)
        assert np.all(result >= 1), "All iteration counts should be >= 1"
        assert np.all(result <= max_iter), f"All iteration counts should be <= {max_iter}"
    
    def test_mandelbrot_array_known_regions(self) -> None:
        """Test known regions of the Mandelbrot set."""
        width, height = 20, 20
        # Wide view showing main cardioid and bulb
        x_min, x_max = -2.5, 1.5  
        y_min, y_max = -2.0, 2.0
        max_iter = 100
        
        from src.mandelbrot_core import mandelbrot_array
        
        result = mandelbrot_array(width, height, x_min, x_max, y_min, y_max, max_iter)
        
        # Center region should have some high iteration counts (inside set)
        center_region = result[height//4:3*height//4, width//4:3*width//4]
        high_iter_count = np.sum(center_region == max_iter)
        total_center_pixels = center_region.size
        
        # With wide view, expect at least some pixels in the set
        assert high_iter_count >= 5, \
            f"Expected at least 5 center pixels to be in set, got {high_iter_count}/{total_center_pixels}"
    
    def test_mandelbrot_array_different_regions(self) -> None:
        """Test that different coordinate regions produce different results."""
        width, height = 10, 10
        max_iter = 50
        
        from src.mandelbrot_core import mandelbrot_array
        
        # Two different regions
        result1 = mandelbrot_array(width, height, -2.0, 2.0, -2.0, 2.0, max_iter)  # Wide view
        result2 = mandelbrot_array(width, height, -1.0, 1.0, -1.0, 1.0, max_iter)  # Zoomed in
        
        # Results should be different (different regions being sampled)
        assert not np.array_equal(result1, result2), \
            "Different coordinate regions should produce different results"
    
    def test_mandelbrot_array_coordinate_bounds(self) -> None:
        """Test that coordinate bounds work correctly."""
        width, height = 4, 4
        max_iter = 50
        
        from src.mandelbrot_core import mandelbrot_array
        
        # Test a region that should have the origin at center
        result = mandelbrot_array(width, height, -1.0, 1.0, -1.0, 1.0, max_iter)
        
        # Center pixel should correspond to origin (which is in the set)
        center_y, center_x = height // 2, width // 2
        center_iterations = result[center_y, center_x]
        
        # Origin should have high iteration count (it's in the set)
        assert center_iterations == max_iter, \
            f"Origin should be in set (max_iter={max_iter}), got {center_iterations} iterations"


class TestEscapeTime:
    """Test escape time calculation accuracy."""
    
    def test_escape_time_specific_points(self) -> None:
        """Test escape time for mathematically known points."""
        from src.mandelbrot_core import mandelbrot_iterations
        
        test_cases = [
            (complex(0, 0), 100, 100),      # Origin: in set
            (complex(-1, 0), 100, 100),     # Point on real axis: in set  
            (complex(0.25, 0), 100, 100),   # Another point in set
            (complex(1, 0), 10, 3),         # Outside set: escapes quickly
            (complex(0, 1), 100, 100),      # Point (0,1) is actually in the set (oscillates)
            (complex(2, 0), 10, 2),         # Point (2,0) escapes very quickly
        ]
        
        for c, max_iter, expected_range in test_cases:
            result = mandelbrot_iterations(c, max_iter)
            if expected_range == max_iter:
                assert result == max_iter, \
                    f"Point {c} should not escape (result={result})"
            else:
                assert result <= expected_range, \
                    f"Point {c} should escape in ≤{expected_range} iterations (result={result})"
    
    def test_escape_time_consistency(self) -> None:
        """Test that escape time is consistent across calls."""
        c = complex(-0.7, 0.3)
        max_iter = 100
        
        from src.mandelbrot_core import mandelbrot_iterations
        
        # Multiple calls should return same result
        results = [mandelbrot_iterations(c, max_iter) for _ in range(5)]
        assert all(r == results[0] for r in results), \
            f"Escape time should be consistent, got {results}"
    
    def test_escape_time_iteration_limit_scaling(self) -> None:
        """Test that higher iteration limits can reveal more detail."""
        c = complex(-0.75, 0.1)  # Point near boundary
        
        from src.mandelbrot_core import mandelbrot_iterations
        
        result_50 = mandelbrot_iterations(c, 50)
        result_100 = mandelbrot_iterations(c, 100)
        result_200 = mandelbrot_iterations(c, 200)
        
        # Results should be non-decreasing
        assert result_50 <= result_100 <= result_200, \
            f"Higher iteration limits should give same or higher counts: {result_50}, {result_100}, {result_200}"