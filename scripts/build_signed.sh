#!/bin/bash

# Reframe - Manual Build and Signing Script
# This script builds, signs, and notarizes the app manually

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check environment variables
check_environment() {
    print_status "Checking environment variables..."
    
    if [ -z "$APPLE_ID" ]; then
        print_warning "APPLE_ID environment variable is not set"
        print_status "Notarization will be skipped"
    fi
    
    if [ -z "$APPLE_APP_SPECIFIC_PASSWORD" ]; then
        print_warning "APPLE_APP_SPECIFIC_PASSWORD environment variable is not set"
        print_status "Notarization will be skipped"
    fi
    
    print_success "Environment check completed"
}

# Function to clean previous builds
clean_builds() {
    print_status "Cleaning previous builds..."
    
    if [ -d "dist" ]; then
        rm -rf dist
        print_success "Cleaned dist directory"
    fi
}

# Function to build CSS
build_css() {
    print_status "Building CSS..."
    
    if ! npm run build:css; then
        print_error "CSS build failed"
        exit 1
    fi
    
    print_success "CSS built successfully"
}

# Function to build the app (without notarization)
build_app() {
    print_status "Building the app..."
    
    # Set environment variables for electron-builder
    export CSC_IDENTITY_AUTO_DISCOVERY=true
    export NOTARIZE=false
    
    # Build with electron-builder (code signing only)
    if ! npm run build:electron; then
        print_error "Build failed"
        exit 1
    fi
    
    print_success "App built and signed successfully"
}

# Function to notarize the app
notarize_app() {
    if [ -z "$APPLE_ID" ] || [ -z "$APPLE_APP_SPECIFIC_PASSWORD" ]; then
        print_warning "Skipping notarization - credentials not set"
        return
    fi
    
    print_status "Notarizing the app..."
    
    # Find the built app
    APP_PATH=$(find dist -name "*.app" -type d | head -n 1)
    
    if [ -z "$APP_PATH" ]; then
        print_error "No .app file found in dist directory"
        exit 1
    fi
    
    print_status "Found app at: $APP_PATH"
    
    # Create a temporary zip file for notarization
    TEMP_ZIP="temp_notarize.zip"
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
                print_warning "Unknown status: $STATUS"
                ;;
        esac
    done
}

# Function to staple the notarization ticket
staple_ticket() {
    if [ -z "$APPLE_ID" ] || [ -z "$APPLE_APP_SPECIFIC_PASSWORD" ]; then
        return
    fi
    
    print_status "Stapling notarization ticket to the app..."
    
    APP_PATH=$(find dist -name "*.app" -type d | head -n 1)
    
    if xcrun stapler staple "$APP_PATH"; then
        print_success "Notarization ticket stapled successfully"
    else
        print_warning "Failed to staple ticket (this is not critical)"
    fi
}

# Function to create DMG
create_dmg() {
    print_status "Creating DMG..."
    
    if ! npm run build:electron; then
        print_error "DMG creation failed"
        exit 1
    fi
    
    print_success "DMG created successfully"
}

# Function to verify the final app
verify_app() {
    print_status "Verifying the signed app..."
    
    APP_PATH=$(find dist -name "*.app" -type d | head -n 1)
    
    # Check code signing
    if codesign -dv --verbose=4 "$APP_PATH" 2>&1 | grep -q "Authority=Developer ID Application"; then
        print_success "App is properly code signed"
    else
        print_error "App is not properly code signed"
        exit 1
    fi
    
    # Check hardened runtime
    if codesign -dv --verbose=4 "$APP_PATH" 2>&1 | grep -q "runtime"; then
        print_success "App has hardened runtime enabled"
    else
        print_warning "App does not have hardened runtime enabled"
    fi
}

# Function to display final information
display_results() {
    print_status "Build completed successfully!"
    echo
    print_status "Files created in dist/ directory:"
    ls -la dist/
    echo
    print_status "The app is now ready for distribution:"
    print_status "- Code signed with Developer ID Application certificate"
    if [ ! -z "$APPLE_ID" ] && [ ! -z "$APPLE_APP_SPECIFIC_PASSWORD" ]; then
        print_status "- Notarized by Apple"
        print_status "- Users can run it without security warnings"
    else
        print_status "- Not notarized (credentials not set)"
        print_status "- Users may see security warnings"
    fi
    echo
    print_status "To test the app:"
    print_status "1. Double-click the .app file in Finder"
    print_status "2. Or run: open dist/Reframe.app"
}

# Main execution
main() {
    echo "=========================================="
    echo "Reframe - Manual Build & Signing Script"
    echo "=========================================="
    echo
    
    check_environment
    clean_builds
    build_css
    build_app
    notarize_app
    staple_ticket
    create_dmg
    verify_app
    display_results
    
    echo
    print_success "Build process completed successfully!"
}

# Run main function
main "$@" 