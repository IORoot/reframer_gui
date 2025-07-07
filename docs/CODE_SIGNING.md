# Code Signing and Notarization

This project is configured for automated code signing and notarization on macOS.

## Prerequisites

1. **Apple Developer Account** ($99/year)
2. **Developer ID Application Certificate** installed in Keychain
3. **App-Specific Password** for notarization

## Setup

### 1. Install Developer Certificate
1. Go to [Apple Developer Certificates](https://developer.apple.com/account/resources/certificates/list)
2. Download your **Developer ID Application** certificate
3. Double-click to install in Keychain Access

### 2. Create App-Specific Password
1. Go to [Apple ID Security](https://appleid.apple.com/account/manage)
2. Generate an app-specific password for notarization
3. Save it securely

### 3. Set Environment Variables
```bash
export APPLE_ID="your-apple-id@example.com"
export APPLE_APP_SPECIFIC_PASSWORD="your-app-specific-password"
```

## Building

### Full Automated Build (Code Signing + Notarization)
```bash
npm run build:mac
```

This command will:
1. Clean previous builds
2. Build CSS
3. Build and code sign the app
4. Automatically notarize with Apple
5. Staple the notarization ticket

### Build Without Notarization (Testing)
```bash
npm run build:electron
```

### Manual Notarization (if needed)
```bash
node build/notarize.js
```

## Configuration

The app uses:
- **electron-builder 23.6.0** (stable version)
- **Auto-discovery** for Developer ID certificate
- **Hardened runtime** enabled
- **Custom notarization script** using `notarytool`

## Verification

After building, verify your app:
```bash
# Check code signing
codesign -dv --verbose=4 dist/Reframe.app

# Check notarization
xcrun stapler validate dist/Reframe.app
```

## Distribution

The signed and notarized app will:
- ✅ Run without security warnings
- ✅ Pass Gatekeeper checks
- ✅ Install normally for users 