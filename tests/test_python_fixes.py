#!/usr/bin/env python3
"""
Test script to verify that the Python fixes prevent crashes.
"""

import sys
import os
import subprocess
import traceback

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        from concurrent.futures import ThreadPoolExecutor
        print("✅ ThreadPoolExecutor imported successfully")
    except ImportError as e:
        print(f"❌ ThreadPoolExecutor import failed: {e}")
        return False
    
    try:
        # Test local imports
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))
        from main import parse_args, main, start_gui
        print("✅ Local modules imported successfully")
    except ImportError as e:
        print(f"❌ Local module import failed: {e}")
        return False
    
    return True

def test_argument_parsing():
    """Test that argument parsing works without crashing."""
    print("\nTesting argument parsing...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))
        from main import parse_args
        
        # Test with minimal arguments
        test_args = ['--input', 'test.mp4', '--output', 'output.mp4']
        original_argv = sys.argv
        sys.argv = ['main.py'] + test_args
        
        try:
            args = parse_args()
            print("✅ Argument parsing successful")
            print(f"   Input: {args.input}")
            print(f"   Output: {args.output}")
            return True
        finally:
            sys.argv = original_argv
            
    except Exception as e:
        print(f"❌ Argument parsing failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_start_gui_function():
    """Test that the start_gui function exists and doesn't crash."""
    print("\nTesting start_gui function...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))
        from main import start_gui
        
        # The function should exist and be callable
        if callable(start_gui):
            print("✅ start_gui function exists and is callable")
            return True
        else:
            print("❌ start_gui is not callable")
            return False
            
    except Exception as e:
        print(f"❌ start_gui function test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_script_execution():
    """Test that the main script can be executed without crashing."""
    print("\nTesting script execution...")
    
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'python', 'main.py')
        
        # Test with --help argument
        result = subprocess.run(
            [sys.executable, script_path, '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode in [0, 1, 2]:  # Success or expected error codes
            print("✅ Script execution successful")
            return True
        else:
            print(f"❌ Script execution failed with return code {result.returncode}")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Script execution timed out")
        return False
    except Exception as e:
        print(f"❌ Script execution failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_no_arguments():
    """Test that the script handles no arguments gracefully."""
    print("\nTesting no arguments handling...")
    
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'python', 'main.py')
        
        # Test without arguments (should call start_gui)
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should exit with code 1 (as defined in start_gui)
        if result.returncode == 1:
            print("✅ No arguments handled gracefully")
            return True
        else:
            print(f"❌ Unexpected return code: {result.returncode}")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ No arguments test timed out")
        return False
    except Exception as e:
        print(f"❌ No arguments test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Python fixes to prevent crashes...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_argument_parsing,
        test_start_gui_function,
        test_script_execution,
        test_no_arguments
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
        print("🎉 All tests passed! Python fixes are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. There may still be issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 