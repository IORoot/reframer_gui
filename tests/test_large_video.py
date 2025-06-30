#!/usr/bin/env python3
"""
Test script to verify that large video processing works with the new error handling and memory management.
"""

import os
import sys
import subprocess
import time

def test_large_video_processing():
    """Test processing a large video to verify error handling and memory management."""
    
    # Add the python directory to the path
    python_dir = os.path.join(os.path.dirname(__file__), 'python')
    sys.path.insert(0, python_dir)
    
    try:
        from main import main
        import argparse
        
        # Create test arguments
        class TestArgs:
            def __init__(self):
                self.input = "/Users/andypearson/Downloads/Test Videos/cars.mp4"
                self.output = "/Users/andypearson/Downloads/Test Videos/cars_test_output.mp4"
                self.target_ratio = 0.5625
                self.max_workers = 4
                self.detector = 'yolo'
                self.skip_frames = 20  # Increase skip frames for large video
                self.conf_threshold = 0.5
                self.model_size = 'n'  # Use nano model for speed
                self.object_classes = [2]  # Detect cars
                self.track_count = 1
                self.padding_ratio = 0.1
                self.size_weight = 0.4
                self.center_weight = 0.3
                self.motion_weight = 0.3
                self.history_weight = 0.1
                self.saliency_weight = 0.4
                self.face_detection = False
                self.weighted_center = False
                self.blend_saliency = False
                self.apply_smoothing = True
                self.smoothing_window = 15
                self.position_inertia = 0.7
                self.size_inertia = 0.6
                self.debug = True
        
        args = TestArgs()
        
        print("Testing large video processing with improved error handling...")
        print(f"Input: {args.input}")
        print(f"Output: {args.output}")
        print(f"Skip frames: {args.skip_frames}")
        print(f"Model size: {args.model_size}")
        print(f"Max workers: {args.max_workers}")
        
        start_time = time.time()
        
        # Run the processing
        main(args)
        
        elapsed_time = time.time() - start_time
        print(f"Test completed successfully in {elapsed_time:.2f} seconds")
        
        # Check if output file exists
        if os.path.exists(args.output):
            print(f"Output file created successfully: {args.output}")
            file_size = os.path.getsize(args.output) / (1024 * 1024)
            print(f"Output file size: {file_size:.2f} MB")
        else:
            print("Warning: Output file not found")
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_large_video_processing()
    sys.exit(0 if success else 1) 