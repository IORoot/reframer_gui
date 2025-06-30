#!/usr/bin/env python3
"""
Test script to verify that the OpenCV video writer crash fixes work correctly.
"""

import sys
import os
import numpy as np
import cv2
import traceback

def test_frame_validation():
    """Test frame validation function."""
    print("Testing frame validation...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))
        from video_processor import VideoProcessor
        
        processor = VideoProcessor()
        
        # Test valid frame
        valid_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        is_valid, msg = processor.validate_frame(valid_frame, 640, 480)
        if is_valid:
            print("✅ Valid frame validation passed")
        else:
            print(f"❌ Valid frame validation failed: {msg}")
            return False
        
        # Test None frame
        is_valid, msg = processor.validate_frame(None)
        if not is_valid and "None" in msg:
            print("✅ None frame validation passed")
        else:
            print(f"❌ None frame validation failed: {msg}")
            return False
        
        # Test invalid dimensions
        invalid_frame = np.zeros((0, 0, 3), dtype=np.uint8)
        is_valid, msg = processor.validate_frame(invalid_frame)
        if not is_valid and "invalid dimensions" in msg:
            print("✅ Invalid dimensions validation passed")
        else:
            print(f"❌ Invalid dimensions validation failed: {msg}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Frame validation test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_crop_validation():
    """Test crop validation function."""
    print("\nTesting crop validation...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))
        from crop_calculator import CropCalculator
        
        calculator = CropCalculator()
        
        # Test valid crop window
        valid_crop = [10, 20, 100, 200]
        is_valid = calculator._validate_crop_window(valid_crop, 640, 480)
        if is_valid:
            print("✅ Valid crop window validation passed")
        else:
            print("❌ Valid crop window validation failed")
            return False
        
        # Test invalid crop window (negative dimensions)
        invalid_crop = [10, 20, -100, 200]
        is_valid = calculator._validate_crop_window(invalid_crop, 640, 480)
        if not is_valid:
            print("✅ Invalid crop window validation passed")
        else:
            print("❌ Invalid crop window validation failed")
            return False
        
        # Test out of bounds crop window
        out_of_bounds_crop = [10, 20, 1000, 200]
        is_valid = calculator._validate_crop_window(out_of_bounds_crop, 640, 480)
        if not is_valid:
            print("✅ Out of bounds crop window validation passed")
        else:
            print("❌ Out of bounds crop window validation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Crop validation test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_safe_crop_calculation():
    """Test that crop calculation handles invalid inputs safely."""
    print("\nTesting safe crop calculation...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))
        from crop_calculator import CropCalculator
        
        calculator = CropCalculator()
        
        # Test with invalid frame dimensions
        crop = calculator.calculate([], 0, 0)
        if crop and len(crop) == 4 and all(isinstance(v, (int, float)) for v in crop):
            print("✅ Invalid frame dimensions handled safely")
        else:
            print("❌ Invalid frame dimensions not handled safely")
            return False
        
        # Test with invalid objects
        crop = calculator.calculate([{'invalid': 'object'}], 640, 480)
        if crop and len(crop) == 4 and all(isinstance(v, (int, float)) for v in crop):
            print("✅ Invalid objects handled safely")
        else:
            print("❌ Invalid objects not handled safely")
            return False
        
        # Test with None objects
        crop = calculator.calculate(None, 640, 480)
        if crop and len(crop) == 4 and all(isinstance(v, (int, float)) for v in crop):
            print("✅ None objects handled safely")
        else:
            print("❌ None objects not handled safely")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Safe crop calculation test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_video_writer_safety():
    """Test that video writer handles invalid frames safely."""
    print("\nTesting video writer safety...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))
        from video_processor import VideoProcessor
        
        processor = VideoProcessor()
        
        # Test with valid frame
        valid_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cropped = processor.apply_crop(valid_frame, [10, 20, 100, 200])
        if cropped is not None and cropped.shape == (200, 100, 3):
            print("✅ Valid frame cropping passed")
        else:
            print("❌ Valid frame cropping failed")
            return False
        
        # Test with None frame
        cropped = processor.apply_crop(None, [10, 20, 100, 200])
        if cropped is None:
            print("✅ None frame cropping handled safely")
        else:
            print("❌ None frame cropping not handled safely")
            return False
        
        # Test with invalid crop window
        cropped = processor.apply_crop(valid_frame, [1000, 2000, -100, -200])
        if cropped is not None:  # Should return a valid crop within bounds
            print("✅ Invalid crop window handled safely")
        else:
            print("❌ Invalid crop window not handled safely")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Video writer safety test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing OpenCV crash fixes...")
    print("=" * 50)
    
    tests = [
        test_frame_validation,
        test_crop_validation,
        test_safe_crop_calculation,
        test_video_writer_safety
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print(f"Traceback: {traceback.format_exc()}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OpenCV crash fixes are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. There may still be issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 