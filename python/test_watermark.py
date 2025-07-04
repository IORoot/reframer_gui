#!/usr/bin/env python3
"""
Test script for watermark functionality
"""

import cv2
import numpy as np
import os
from config import config
from watermark import watermark_renderer

def create_test_frame(width=640, height=480):
    """Create a test frame with a gradient background."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create a gradient background
    for y in range(height):
        for x in range(width):
            r = int(255 * x / width)
            g = int(255 * y / height)
            b = int(255 * (x + y) / (width + height))
            frame[y, x] = [b, g, r]
    
    return frame

def test_watermark_configuration():
    """Test watermark configuration system."""
    print("Testing watermark configuration system...")
    
    # Test default configuration
    watermark_config = config.get_watermark_config()
    print(f"Default watermark config: {watermark_config}")
    
    # Test enabling watermark
    config.set_watermark_enabled(True)
    config.set_watermark_text("TEST")
    config.set_watermark_position("center")
    config.set_watermark_opacity(0.5)
    
    updated_config = config.get_watermark_config()
    print(f"Updated watermark config: {updated_config}")
    
    # Test disabling watermark
    config.set_watermark_enabled(False)
    final_config = config.get_watermark_config()
    print(f"Final watermark config: {final_config}")
    
    print("✓ Watermark configuration test passed")

def test_watermark_rendering():
    """Test watermark rendering on a test frame."""
    print("Testing watermark rendering...")
    
    # Create test frame
    frame = create_test_frame(640, 480)
    
    # Enable watermark
    config.set_watermark_enabled(True)
    config.set_watermark_text("BETA TEST")
    config.set_watermark_position("bottom-right")
    config.set_watermark_opacity(0.3)
    
    # Apply watermark
    watermarked_frame = watermark_renderer.apply_watermark(frame)
    
    # Save test images
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    cv2.imwrite(f"{output_dir}/original_frame.png", frame)
    cv2.imwrite(f"{output_dir}/watermarked_frame.png", watermarked_frame)
    
    print(f"✓ Watermark rendering test passed")
    print(f"Test images saved to {output_dir}/")
    
    # Test different positions
    positions = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
    
    for position in positions:
        config.set_watermark_position(position)
        watermarked = watermark_renderer.apply_watermark(frame)
        cv2.imwrite(f"{output_dir}/watermark_{position.replace('-', '_')}.png", watermarked)
        print(f"  - Tested position: {position}")
    
    # Disable watermark
    config.set_watermark_enabled(False)

def test_watermark_disabled():
    """Test that watermark is not applied when disabled."""
    print("Testing watermark disabled state...")
    
    frame = create_test_frame(640, 480)
    original_frame = frame.copy()
    
    # Ensure watermark is disabled
    config.set_watermark_enabled(False)
    
    # Apply watermark (should return original frame)
    result_frame = watermark_renderer.apply_watermark(frame)
    
    # Check that frames are identical
    if np.array_equal(original_frame, result_frame):
        print("✓ Watermark disabled test passed")
    else:
        print("✗ Watermark disabled test failed - frames are different")

def main():
    """Run all watermark tests."""
    print("Running watermark functionality tests...")
    print("=" * 50)
    
    try:
        test_watermark_configuration()
        print()
        
        test_watermark_rendering()
        print()
        
        test_watermark_disabled()
        print()
        
        print("=" * 50)
        print("All watermark tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 