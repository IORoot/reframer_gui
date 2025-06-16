#!/usr/bin/env python3
"""
Test script for the FFmpeg manager.
This script will test downloading and using ffmpeg as a dependency.
"""

import sys
import os
from pathlib import Path

# Add the python directory to the path so we can import the ffmpeg manager
sys.path.insert(0, str(Path(__file__).parent / 'python'))

try:
    from ffmpeg_manager import get_ffmpeg_path
    print("✅ Successfully imported ffmpeg_manager")
except ImportError as e:
    print(f"❌ Failed to import ffmpeg_manager: {e}")
    sys.exit(1)

def test_ffmpeg_manager():
    """Test the ffmpeg manager functionality."""
    print("🚀 Testing FFmpeg Manager...")
    print(f"Current working directory: {os.getcwd()}")
    
    try:
        # Get ffmpeg path (this will download if needed)
        ffmpeg_path = get_ffmpeg_path()
        print(f"✅ FFmpeg path: {ffmpeg_path}")
        
        # Test if ffmpeg works
        import subprocess
        result = subprocess.run([ffmpeg_path, '-version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ FFmpeg is working correctly!")
            print(f"FFmpeg version: {result.stdout.split()[2] if len(result.stdout.split()) > 2 else 'Unknown'}")
        else:
            print(f"❌ FFmpeg test failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error testing ffmpeg manager: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_ffmpeg_manager()
    if success:
        print("\n🎉 FFmpeg manager test completed successfully!")
    else:
        print("\n💥 FFmpeg manager test failed!")
        sys.exit(1) 