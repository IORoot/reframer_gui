#!/bin/bash

# Set environment variables for code signing
export CSC_IDENTITY_AUTO_DISCOVERY=true
export APPLE_APP_SPECIFIC_PASSWORD="$APPLE_ID_PASSWORD"
export APPLE_TEAM_ID="43DRWGP9KX"

# Check if Apple ID credentials are set
if [ -z "$APPLE_ID" ]; then
    echo "Warning: APPLE_ID not set. Notarization will be skipped."
    echo "Set it with: export APPLE_ID='your-apple-id@example.com'"
fi

if [ -z "$APPLE_ID_PASSWORD" ]; then
    echo "Warning: APPLE_ID_PASSWORD not set. Notarization will be skipped."
    echo "Set it with: export APPLE_ID_PASSWORD='your-app-specific-password'"
fi

# Build with signing
echo "Building with code signing enabled..."
npm run build:mac 