#!/bin/bash

# Test Application Code Signing and Notarization
# Usage: ./scripts/test_app.sh /path/to/app.app

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

# Check if file path is provided
if [ $# -eq 0 ]; then
    print_error "Usage: $0 /path/to/app.app"
    print_status "Example: $0 /Applications/Reframe.app"
    exit 1
fi

APP_PATH="$1"

# Check if file exists
if [ ! -e "$APP_PATH" ]; then
    print_error "File not found: $APP_PATH"
    exit 1
fi

# Determine file type
if [[ "$APP_PATH" == *.dmg ]]; then
    FILE_TYPE="DMG"
    print_status "Testing DMG file: $APP_PATH"
elif [[ "$APP_PATH" == *.app ]]; then
    FILE_TYPE="APP"
    print_status "Testing app: $APP_PATH"
else
    print_error "Unsupported file type. Please provide a .app or .dmg file."
    exit 1
fi

echo

# Test 1: Code Signing
print_status "=== Code Signing Check ==="
if codesign -dv --verbose=4 "$APP_PATH" 2>&1 | grep -q "Authority=Developer ID Application"; then
    print_success "$FILE_TYPE is code signed with Developer ID Application"
    AUTHORITY=$(codesign -dv --verbose=4 "$APP_PATH" 2>&1 | grep "Authority=Developer ID Application" | head -1)
    print_status "Authority: $AUTHORITY"
else
    print_error "$FILE_TYPE is not code signed with Developer ID Application"
fi

# Test 2: Hardened Runtime (only for .app files)
if [[ "$FILE_TYPE" == "APP" ]]; then
    print_status "=== Hardened Runtime Check ==="
    if codesign -dv --verbose=4 "$APP_PATH" 2>&1 | grep -q "runtime"; then
        print_success "App has hardened runtime enabled"
    else
        print_warning "App does not have hardened runtime enabled"
    fi
fi

# Test 3: Notarization
print_status "=== Notarization Check ==="
if xcrun stapler validate "$APP_PATH" >/dev/null 2>&1; then
    print_success "$FILE_TYPE has notarization ticket stapled"
else
    if [[ "$FILE_TYPE" == "DMG" ]]; then
        print_warning "DMG does not have notarization ticket stapled (this is normal for DMG files)"
    else
        print_warning "App does not have notarization ticket stapled (this may be normal for installed apps)"
    fi
fi

# Test 4: Gatekeeper
print_status "=== Gatekeeper Check ==="
GATEKEEPER_RESULT=$(spctl --assess --verbose "$APP_PATH" 2>&1)
if echo "$GATEKEEPER_RESULT" | grep -q "accepted"; then
    print_success "$FILE_TYPE is accepted by Gatekeeper"
    SOURCE=$(echo "$GATEKEEPER_RESULT" | grep "source=" | cut -d'=' -f2)
    print_status "Source: $SOURCE"
else
    print_error "$FILE_TYPE is not accepted by Gatekeeper"
    print_status "Gatekeeper result: $GATEKEEPER_RESULT"
fi

# Test 5: Quarantine
print_status "=== Quarantine Check ==="
if xattr -l "$APP_PATH" 2>/dev/null | grep -q "quarantine"; then
    print_warning "$FILE_TYPE has quarantine attributes"
    xattr -l "$APP_PATH" | grep quarantine
else
    print_success "$FILE_TYPE has no quarantine attributes"
fi

# Test 6: Team Identifier
print_status "=== Team Identifier Check ==="
TEAM_ID=$(codesign -dv --verbose=4 "$APP_PATH" 2>&1 | grep "TeamIdentifier=" | cut -d'=' -f2)
if [ ! -z "$TEAM_ID" ]; then
    print_success "Team Identifier: $TEAM_ID"
else
    print_warning "No Team Identifier found"
fi

echo
print_status "=== Summary ==="
if codesign -dv --verbose=4 "$APP_PATH" 2>&1 | grep -q "Authority=Developer ID Application" && echo "$GATEKEEPER_RESULT" | grep -q "accepted"; then
    print_success "✅ $FILE_TYPE is properly signed and notarized!"
    if [[ "$FILE_TYPE" == "DMG" ]]; then
        print_status "Users can download and install this DMG without security warnings."
    else
        print_status "Users can install and run this app without security warnings."
    fi
else
    print_error "❌ $FILE_TYPE has issues with signing or notarization."
    print_status "Users may see security warnings when installing."
fi 