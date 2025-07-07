#!/bin/bash

# Simple build script that avoids notarization issues

set -e

echo "Building with electron-builder (code signing only)..."

# Set environment variables
export CSC_IDENTITY_AUTO_DISCOVERY=true
export NOTARIZE=false

# Clean and build CSS
npm run clean
npm run build:css

# Build with electron-builder
npm run build:electron

echo "Build completed successfully!"
echo "App is signed and ready for manual notarization if needed." 