#!/usr/bin/env python3
"""
Minimal Dear PyGUI texture test to isolate texture creation issues.
"""

import dearpygui.dearpygui as dpg
import numpy as np
from loguru import logger
import sys
from pathlib import Path

# Add src directory for logging
sys.path.insert(0, str(Path(__file__).parent / "src"))
from logger_config import setup_logging


def test_texture_creation():
    """Test different approaches to texture creation in Dear PyGUI."""
    
    logger.info("Starting texture creation test")
    
    # Create context
    dpg.create_context()
    
    # Test 1: Create a simple RGB image
    logger.info("Test 1: Creating simple RGB numpy array")
    width, height = 100, 100
    
    # Create a simple gradient image
    image_data = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            image_data[y, x] = [x * 255 // width, y * 255 // height, 128]
    
    logger.info(f"Image data shape: {image_data.shape}, dtype: {image_data.dtype}")
    logger.info(f"Image data range: {image_data.min()} to {image_data.max()}")
    
    try:
        # Test 2: Try creating texture registry
        logger.info("Test 2: Creating texture registry")
        dpg.add_texture_registry(tag="texture_registry_test")
        logger.info("✓ Texture registry created successfully")
        
        # Test 3: Convert data to float32 normalized
        logger.info("Test 3: Converting to float32 normalized format")
        float_data = image_data.astype(np.float32) / 255.0
        logger.info(f"Float data shape: {float_data.shape}, dtype: {float_data.dtype}")
        logger.info(f"Float data range: {float_data.min()} to {float_data.max()}")
        
        # Test 4: Add alpha channel for RGBA
        logger.info("Test 4: Adding alpha channel")
        alpha = np.ones((height, width, 1), dtype=np.float32)
        rgba_data = np.concatenate([float_data, alpha], axis=2)
        logger.info(f"RGBA data shape: {rgba_data.shape}")
        
        # Test 5: Flatten data
        logger.info("Test 5: Flattening data")
        flat_data = rgba_data.flatten().tolist()
        expected_size = width * height * 4
        logger.info(f"Flat data length: {len(flat_data)}, expected: {expected_size}")
        
        if len(flat_data) != expected_size:
            logger.error(f"Data size mismatch!")
            return False
        
        # Test 6: Try creating raw texture
        logger.info("Test 6: Creating raw texture")
        texture_tag = "test_texture_unique_001"
        
        dpg.add_raw_texture(
            width=width,
            height=height,
            default_value=flat_data,
            format=dpg.mvFormat_Float_rgba,
            tag=texture_tag,
            parent="texture_registry_test"
        )
        logger.info("✓ Raw texture created successfully")
        
        # Test 7: Create window with image
        logger.info("Test 7: Creating window with image")
        with dpg.window(label="Texture Test", width=200, height=200, tag="test_window"):
            dpg.add_image(texture_tag, width=100, height=100)
        
        # Test 8: Try updating texture
        logger.info("Test 8: Updating texture with new data")
        
        # Create different colored image
        new_image = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                new_image[y, x] = [255 - x * 255 // width, 128, y * 255 // height]
        
        new_float_data = new_image.astype(np.float32) / 255.0
        new_rgba_data = np.concatenate([new_float_data, alpha], axis=2)
        new_flat_data = new_rgba_data.flatten().tolist()
        
        # Delete old texture and create new one
        if dpg.does_item_exist(texture_tag):
            logger.info("Deleting existing texture")
            dpg.delete_item(texture_tag)
        
        new_texture_tag = "test_texture_unique_002"
        dpg.add_raw_texture(
            width=width,
            height=height,
            default_value=new_flat_data,
            format=dpg.mvFormat_Float_rgba,
            tag=new_texture_tag,
            parent="texture_registry_test"
        )
        
        # Update image to use new texture
        dpg.set_value("test_window", new_texture_tag)
        logger.info("✓ Texture updated successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Texture creation failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False


def test_alternative_approaches():
    """Test alternative texture creation approaches."""
    
    logger.info("Testing alternative approaches")
    
    try:
        # Method 1: Using load_image with temporary file
        logger.info("Method 1: Testing file-based texture loading")
        
        from PIL import Image
        
        # Create test image
        test_image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        pil_image = Image.fromarray(test_image)
        
        temp_file = "/tmp/test_texture.png"
        pil_image.save(temp_file)
        logger.info(f"Saved test image to {temp_file}")
        
        # Load with Dear PyGUI
        width, height, channels, data = dpg.load_image(temp_file)
        logger.info(f"Loaded image: {width}x{height}, {channels} channels, data type: {type(data)}")
        
        # Create texture from loaded data
        alt_texture_tag = "alt_texture_001"
        dpg.add_static_texture(
            width=width,
            height=height,
            default_value=data,
            tag=alt_texture_tag,
            parent="texture_registry_test"
        )
        logger.info("✓ Alternative texture method successful")
        
        # Clean up
        import os
        os.remove(temp_file)
        
        return True
        
    except Exception as e:
        logger.error(f"Alternative method failed: {e}")
        return False


def main():
    """Run texture tests."""
    setup_logging(debug=True)
    
    logger.info("=" * 50)
    logger.info("Dear PyGUI Texture Debug Test")
    logger.info("=" * 50)
    
    try:
        # Test basic texture creation
        success1 = test_texture_creation()
        
        if success1:
            logger.info("✓ Basic texture creation: SUCCESS")
        else:
            logger.error("✗ Basic texture creation: FAILED")
        
        # Test alternative methods
        success2 = test_alternative_approaches()
        
        if success2:
            logger.info("✓ Alternative texture methods: SUCCESS")
        else:
            logger.error("✗ Alternative texture methods: FAILED")
        
        if success1 or success2:
            logger.info("At least one texture method works - proceeding to GUI test")
            
            # Create viewport and show GUI briefly
            dpg.create_viewport(title="Texture Test Results", width=300, height=300)
            dpg.setup_dearpygui()
            dpg.show_viewport()
            
            # Run for a few seconds
            import time
            start_time = time.time()
            while dpg.is_dearpygui_running() and time.time() - start_time < 3:
                dpg.render_dearpygui_frame()
        
        logger.info("Test complete")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
    
    finally:
        dpg.destroy_context()


if __name__ == "__main__":
    main()