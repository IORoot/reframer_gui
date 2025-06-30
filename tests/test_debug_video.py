#!/usr/bin/env python3
"""
Test script to verify the new debug video functionality in ObjectDetector using landscape_10secs.mp4.
"""

import cv2
import os
from python.object_detector import ObjectDetector

def test_debug_video_with_real_video():
    """Test the debug video functionality using landscape_10secs.mp4."""
    print("Testing debug video functionality with landscape_10secs.mp4...")
    
    video_path = "landscape_10secs.mp4"
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return
    
    print(f"✅ Found video file: {video_path}")
    
    # Create detector with debug enabled
    detector = ObjectDetector(
        confidence_threshold=0.3,  # Lower threshold for testing
        model_size='n',
        classes=[0],  # Detect people
        debug=True
    )
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Could not open video: {video_path}")
        return
    
    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Video properties:")
    print(f"  Total frames: {total_frames}")
    print(f"  FPS: {fps}")
    print(f"  Resolution: {width}x{height}")
    
    # Process frames (every 10th frame to speed up testing)
    frame_skip = 10
    processed_frames = 0
    detection_count = 0
    
    print(f"\nProcessing every {frame_skip}th frame...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        
        # Only process every nth frame
        if frame_number % frame_skip != 0:
            continue
        
        processed_frames += 1
        print(f"Processing frame {frame_number}/{total_frames} (processed: {processed_frames})")
        
        # Detect objects
        detections = detector.detect(frame, top_n=2)
        
        if detections:
            detection_count += len(detections)
            print(f"  Found {len(detections)} detections:")
            for det in detections:
                print(f"    {det['class_name']}: {det['confidence']:.2f}")
        
        # Limit processing to first 50 frames for testing
        if processed_frames >= 50:
            print("Reached 50 processed frames, stopping for testing...")
            break
    
    # Clean up
    cap.release()
    
    # Finalize the debug video
    detector.finalize_debug_video()
    
    # Check if the video file was created
    if detector.debug_video_path and os.path.exists(detector.debug_video_path):
        print(f"\n✅ Debug video created successfully: {detector.debug_video_path}")
        file_size = os.path.getsize(detector.debug_video_path)
        print(f"   File size: {file_size} bytes")
        print(f"   Frames processed: {detector.frame_count}")
    else:
        print("\n❌ Debug video was not created")
    
    # Check if the log file was created
    log_path = "debug_logs/log1_detections.txt"
    if os.path.exists(log_path):
        print(f"✅ Debug log created: {log_path}")
        with open(log_path, 'r') as f:
            log_lines = f.readlines()
        print(f"   Log entries: {len(log_lines)}")
        print(f"   Total detections logged: {detection_count}")
    else:
        print("❌ Debug log was not created")
    
    print(f"\nTest summary:")
    print(f"  Frames processed: {processed_frames}")
    print(f"  Total detections: {detection_count}")
    print(f"  Debug video frames: {detector.frame_count}")

if __name__ == "__main__":
    test_debug_video_with_real_video() 