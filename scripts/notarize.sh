#!/bin/bash

# Post-build notarization script
# This script runs after electron-builder creates the signed app

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment variables are set
if [ -z "$APPLE_ID" ]; then
    print_error "APPLE_ID environment variable is not set"
    exit 1
fi

if [ -z "$APPLE_APP_SPECIFIC_PASSWORD" ]; then
    print_error "APPLE_APP_SPECIFIC_PASSWORD environment variable is not set"
    exit 1
fi

# Find the built app
APP_PATH=$(find dist -name "*.app" -type d | head -n 1)

if [ -z "$APP_PATH" ]; then
    print_error "No .app file found in dist directory"
    exit 1
fi

print_status "Found app at: $APP_PATH"

# Create a temporary zip file for notarization
TEMP_ZIP="temp_notarize.zip"
print_status "Creating temporary zip for notarization..."
ditto -c -k --keepParent "$APP_PATH" "$TEMP_ZIP"

# Submit for notarization
print_status "Submitting to Apple for notarization..."

NOTARIZATION_UUID=$(xcrun altool --notarize-app \
    --primary-bundle-id "com.reframe.app" \
    --username "$APPLE_ID" \
    --password "$APPLE_APP_SPECIFIC_PASSWORD" \
    --file "$TEMP_ZIP" \
    --output-format xml | grep -o 'RequestUUID>[^<]*' | cut -d'>' -f2)

if [ -z "$NOTARIZATION_UUID" ]; then
    print_error "Failed to submit for notarization"
    rm -f "$TEMP_ZIP"
    exit 1
fi

print_success "Submitted for notarization with UUID: $NOTARIZATION_UUID"
rm -f "$TEMP_ZIP"

# Wait for notarization to complete
print_status "Waiting for notarization to complete (this may take several minutes)..."

while true; do
    sleep 30
    STATUS=$(xcrun altool --notarization-info "$NOTARIZATION_UUID" \
        --username "$APPLE_ID" \
        --password "$APPLE_APP_SPECIFIC_PASSWORD" \
        --output-format xml | grep -o 'Status>[^<]*' | cut -d'>' -f2)
    
    case $STATUS in
        "success")
            print_success "Notarization completed successfully!"
            break
            ;;
        "in progress")
            print_status "Still in progress..."
            ;;
        "invalid")
            print_error "Notarization failed"
            xcrun altool --notarization-info "$NOTARIZATION_UUID" \
                --username "$APPLE_ID" \
                --password "$APPLE_APP_SPECIFIC_PASSWORD"
            exit 1
            ;;
        *)
            print_status "Unknown status: $STATUS"
            ;;
    esac
done

# Staple the notarization ticket
print_status "Stapling notarization ticket to the app..."
if xcrun stapler staple "$APP_PATH"; then
    print_success "Notarization ticket stapled successfully"
else
    print_error "Failed to staple ticket"
    exit 1
fi

print_success "Notarization process completed successfully!"
print_status "The app is now ready for distribution:"
print_status "- Code signed with Developer ID Application certificate"
print_status "- Notarized by Apple"
print_status "- Users can run it without security warnings" 