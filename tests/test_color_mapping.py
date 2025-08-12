import pytest
import numpy as np
from typing import Tuple


class TestColorMapping:
    """Test RGB color mapping functionality."""
    
    def test_iterations_to_rgb_basic(self) -> None:
        """Test basic iteration count to RGB conversion."""
        from src.color_mapping import iterations_to_rgb
        
        # Test single values
        rgb = iterations_to_rgb(50, max_iter=100)
        assert len(rgb) == 3, "RGB should have 3 components"
        assert all(0 <= c <= 255 for c in rgb), "RGB values should be in [0, 255] range"
        assert all(isinstance(c, int) for c in rgb), "RGB values should be integers"
    
    def test_iterations_to_rgb_boundaries(self) -> None:
        """Test RGB conversion at boundary values."""
        from src.color_mapping import iterations_to_rgb
        
        max_iter = 100
        
        # Test minimum iteration (escaped immediately)
        rgb_min = iterations_to_rgb(1, max_iter)
        assert len(rgb_min) == 3
        
        # Test maximum iteration (in the set)
        rgb_max = iterations_to_rgb(max_iter, max_iter)
        assert rgb_max == (0, 0, 0), "Points in set should be black"
        
        # Test mid-range value
        rgb_mid = iterations_to_rgb(max_iter // 2, max_iter)
        assert len(rgb_mid) == 3
        assert rgb_mid != (0, 0, 0), "Mid-range should not be black"
    
    def test_iterations_to_rgb_array(self) -> None:
        """Test RGB conversion for numpy arrays."""
        from src.color_mapping import iterations_to_rgb_array
        
        # Create test iteration array
        iterations = np.array([
            [1, 5, 100],
            [25, 50, 100],
            [75, 99, 100]
        ], dtype=np.int32)
        
        max_iter = 100
        
        rgb_image = iterations_to_rgb_array(iterations, max_iter)
        
        # Check output shape
        expected_shape = (iterations.shape[0], iterations.shape[1], 3)
        assert rgb_image.shape == expected_shape, f"Expected shape {expected_shape}, got {rgb_image.shape}"
        
        # Check data type
        assert rgb_image.dtype == np.uint8, f"Expected uint8, got {rgb_image.dtype}"
        
        # Check value ranges
        assert np.all(rgb_image >= 0), "RGB values should be >= 0"
        assert np.all(rgb_image <= 255), "RGB values should be <= 255"
        
        # Check that points in set (max_iter) are black
        max_iter_mask = iterations == max_iter
        black_pixels = rgb_image[max_iter_mask]
        assert np.all(black_pixels == [0, 0, 0]), "Points in set should be black"
    
    def test_iterations_to_rgb_consistency(self) -> None:
        """Test that single value and array conversions are consistent."""
        from src.color_mapping import iterations_to_rgb, iterations_to_rgb_array
        
        max_iter = 100
        test_values = [1, 25, 50, 75, 99, 100]
        
        for value in test_values:
            # Convert single value
            single_rgb = iterations_to_rgb(value, max_iter)
            
            # Convert as 1x1 array
            array_rgb = iterations_to_rgb_array(np.array([[value]]), max_iter)
            array_rgb_single = tuple(array_rgb[0, 0])
            
            assert single_rgb == array_rgb_single, \
                f"Single and array conversion should match for {value}: {single_rgb} != {array_rgb_single}"
    
    def test_smooth_color_transition(self) -> None:
        """Test that color transitions are smooth."""
        from src.color_mapping import iterations_to_rgb
        
        max_iter = 100
        
        # Test a sequence of iterations for smoothness
        colors = []
        for i in range(1, max_iter, 10):
            rgb = iterations_to_rgb(i, max_iter)
            colors.append(rgb)
        
        # Colors should be different (not all the same)
        assert len(set(colors)) > 1, "Should have variety in colors"
        
        # Colors should change gradually (no huge jumps)
        for i in range(len(colors) - 1):
            curr = np.array(colors[i])
            next_color = np.array(colors[i + 1])
            diff = np.abs(curr - next_color)
            max_diff = np.max(diff)
            
            # Allow reasonable color changes but not extreme jumps
            assert max_diff < 200, f"Color change too abrupt: {colors[i]} -> {colors[i+1]} (diff: {max_diff})"


class TestColorPalettes:
    """Test different color palette functionality."""
    
    def test_default_palette_exists(self) -> None:
        """Test that default palette is available."""
        from src.color_mapping import get_available_palettes, iterations_to_rgb
        
        palettes = get_available_palettes()
        assert len(palettes) > 0, "Should have at least one palette"
        assert 'default' in palettes, "Should have a 'default' palette"
        
        # Test using default palette
        rgb = iterations_to_rgb(50, max_iter=100, palette='default')
        assert len(rgb) == 3
    
    def test_multiple_palettes(self) -> None:
        """Test that multiple palettes produce different results."""
        from src.color_mapping import get_available_palettes, iterations_to_rgb
        
        palettes = get_available_palettes()
        
        if len(palettes) > 1:
            # Test same iteration with different palettes
            iteration = 50
            max_iter = 100
            
            colors = {}
            for palette in palettes:
                rgb = iterations_to_rgb(iteration, max_iter, palette=palette)
                colors[palette] = rgb
            
            # Different palettes should produce different colors (at least some)
            unique_colors = set(colors.values())
            assert len(unique_colors) > 1 or len(palettes) == 1, \
                "Different palettes should produce different colors"
    
    def test_palette_switching(self) -> None:
        """Test switching between palettes."""
        from src.color_mapping import iterations_to_rgb_array, get_available_palettes
        
        palettes = get_available_palettes()
        
        # Create test array
        iterations = np.array([[25, 50, 75]], dtype=np.int32)
        max_iter = 100
        
        results = {}
        for palette in palettes:
            rgb_image = iterations_to_rgb_array(iterations, max_iter, palette=palette)
            results[palette] = rgb_image.copy()
        
        # All results should have correct shape and type
        for palette, result in results.items():
            assert result.shape == (1, 3, 3), f"Wrong shape for palette {palette}"
            assert result.dtype == np.uint8, f"Wrong dtype for palette {palette}"
    
    def test_invalid_palette(self) -> None:
        """Test handling of invalid palette names."""
        from src.color_mapping import iterations_to_rgb
        
        with pytest.raises(ValueError, match="Unknown palette"):
            iterations_to_rgb(50, max_iter=100, palette='nonexistent_palette')
    
    def test_palette_names_are_strings(self) -> None:
        """Test that palette names are valid strings."""
        from src.color_mapping import get_available_palettes
        
        palettes = get_available_palettes()
        
        for palette in palettes:
            assert isinstance(palette, str), f"Palette name should be string, got {type(palette)}"
            assert len(palette) > 0, "Palette name should not be empty"