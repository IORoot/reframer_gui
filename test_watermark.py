#!/usr/bin/env python3
"""
Simple test script to verify watermark functionality
"""

import cv2
import numpy as np
import sys
import os

# Add the python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from video_processor import VideoProcessor

def test_watermark():
    """Test the watermark functionality"""
    print("Testing watermark functionality...")
    
    # Create a test frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (100, 150, 200)  # Blue-ish background
    
    # Create video processor
    processor = VideoProcessor()
    
    # Test watermark
    watermarked_frame = processor.add_watermark(frame, "BETA", "center", 0.8)
    
    if watermarked_frame is not None:
        print("✅ Watermark test successful!")
        
        # Save test image
        cv2.imwrite("test_watermark.png", watermarked_frame)
        print("✅ Test image saved as 'test_watermark.png'")
        
        # Check if the watermark is visible
        # Look for white pixels (watermark text)
        white_pixels = np.sum(watermarked_frame == [255, 255, 255])
        if white_pixels > 0:
            print(f"✅ Watermark text detected: {white_pixels} white pixels found")
        else:
            print("⚠️  No white pixels found - watermark might not be visible")
            
    else:
        print("❌ Watermark test failed!")
    
    return watermarked_frame is not None

if __name__ == "__main__":
    success = test_watermark()
    sys.exit(0 if success else 1) 