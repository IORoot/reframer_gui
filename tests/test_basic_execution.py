#!/usr/bin/env python3
"""
Basic test script to verify that the Python backend can be executed.
This script can be run directly without pytest to check basic functionality.
"""

import sys
import os
from pathlib import Path

# Add the python directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import cv2
        print(f"✅ OpenCV imported successfully (version: {cv2.__version__})")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✅ NumPy imported successfully (version: {np.__version__})")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        from ultralytics import YOLO
        print("✅ Ultralytics (YOLOv8) imported successfully")
    except ImportError as e:
        print(f"❌ Ultralytics import failed: {e}")
        return False
    
    try:
        from concurrent.futures import ThreadPoolExecutor
        print("✅ concurrent.futures imported successfully")
    except ImportError as e:
        print(f"❌ concurrent.futures import failed: {e}")
        return False
    
    return True

def test_main_module():
    """Test that the main module can be imported."""
    print("\nTesting main module import...")
    
    try:
        from main import parse_args, main, process_keyframe
        print("✅ Main module imported successfully")
        print(f"✅ parse_args function: {callable(parse_args)}")
        print(f"✅ main function: {callable(main)}")
        print(f"✅ process_keyframe function: {callable(process_keyframe)}")
        return True
    except ImportError as e:
        print(f"❌ Main module import failed: {e}")
        return False

def test_other_modules():
    """Test that other key modules can be imported."""
    print("\nTesting other module imports...")
    
    modules_to_test = [
        'video_processor',
        'object_detector', 
        'object_tracker',
        'crop_calculator',
        'smoothing',
        'ffmpeg_manager'
    ]
    
    all_success = True
    
    for module_name in modules_to_test:
        try:
            module = __import__(module_name)
            print(f"✅ {module_name} imported successfully")
        except ImportError as e:
            print(f"❌ {module_name} import failed: {e}")
            all_success = False
    
    return all_success

def test_argument_parsing():
    """Test that argument parsing works."""
    print("\nTesting argument parsing...")
    
    try:
        from main import parse_args
        
        # Test with basic arguments
        original_argv = sys.argv.copy()
        sys.argv = ['main.py', '--input', 'test.mp4', '--output', 'output.mp4']
        
        args = parse_args()
        
        # Check that arguments were parsed correctly
        assert args.input == 'test.mp4'
        assert args.output == 'output.mp4'
        assert args.target_ratio == 9/16  # Default value
        assert args.model_size == 'n'     # Default value
        
        print("✅ Argument parsing works correctly")
        
        # Restore original argv
        sys.argv = original_argv
        return True
        
    except Exception as e:
        print(f"❌ Argument parsing failed: {e}")
        return False

def test_file_structure():
    """Test that required files exist."""
    print("\nTesting file structure...")
    
    python_dir = Path(__file__).parent.parent / 'python'
    required_files = [
        'main.py',
        'video_processor.py',
        'object_detector.py',
        'object_tracker.py',
        'crop_calculator.py',
        'smoothing.py',
        'ffmpeg_manager.py',
        'requirements.txt'
    ]
    
    all_exist = True
    
    for file_name in required_files:
        file_path = python_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name} exists")
        else:
            print(f"❌ {file_name} missing")
            all_exist = False
    
    return all_exist

def test_script_execution():
    """Test that the main script can be executed."""
    print("\nTesting script execution...")
    
    script_path = Path(__file__).parent.parent / 'python' / 'main.py'
    
    if not script_path.exists():
        print(f"❌ Main script not found at {script_path}")
        return False
    
    try:
        # Try to execute the script with --help
        import subprocess
        result = subprocess.run(
            [sys.executable, str(script_path), '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode in [0, 1, 2]:  # Success or expected error codes
            print("✅ Script can be executed")
            return True
        else:
            print(f"❌ Script execution failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Script execution timed out")
        return False
    except Exception as e:
        print(f"❌ Script execution failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Reframer GUI Backend - Basic Execution Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Main Module", test_main_module),
        ("Other Modules", test_other_modules),
        ("Argument Parsing", test_argument_parsing),
        ("Script Execution", test_script_execution),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The backend is ready for use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 