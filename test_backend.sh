#!/bin/bash

# Test script for Reframer GUI Backend
# This script runs a basic test to verify the Python backend can be executed

echo "🧪 Testing Reframer GUI Backend"
echo "================================"

# Check if we're in the right directory
if [ ! -f "python/main.py" ]; then
    echo "❌ Error: python/main.py not found. Please run this script from the project root."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Run the basic test
echo ""
echo "Running basic backend test..."
python3 tests/test_basic_execution.py

# Check the exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Backend test completed successfully!"
    echo "The Python backend is ready for use."
else
    echo ""
    echo "⚠️  Backend test failed. Please check the issues above."
    exit 1
fi 