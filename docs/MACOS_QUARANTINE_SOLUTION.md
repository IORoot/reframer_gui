# Resolving macOS Quarantine Issues

This document explains how to resolve the "cannot determine the identity of the publisher" quarantine issue when distributing your Electron app on macOS.

## The Problem

When you build and distribute an Electron app on macOS, Gatekeeper (macOS's security system) may quarantine the app because it's not code-signed by a recognized developer. This results in:

- "Cannot determine the identity of the publisher" warning
- App being moved to quarantine
- User must manually allow the app to run

## Solutions

### Solution 1: Code Signing (Recommended for Distribution)

For proper distribution, you should code-sign your app with an Apple Developer certificate.

#### Prerequisites
1. **Apple Developer Account**: You need a paid Apple Developer account ($99/year)
2. **Developer ID Certificate**: Request a Developer ID Application certificate from Apple
3. **Notarization**: Submit your app to Apple for notarization

#### Steps

1. **Get your Developer ID certificate**:
   ```bash
   # List available certificates
   security find-identity -v -p codesigning
   ```

2. **Update package.json** (already done):
   ```json
   "mac": {
     "category": "public.app-category.video",
     "target": ["dmg"],
     "icon": "build/icon.icns",
     "hardenedRuntime": true,
     "entitlements": "build/entitlements.mac.plist",
     "entitlementsInherit": "build/entitlements.mac.plist",
     "identity": "Developer ID Application: Your Name (TEAM_ID)"
   }
   ```

3. **Build with code signing**:
   ```bash
   npm run build:mac
   ```

4. **Notarize the app** (required for distribution):
   ```bash
   # Create app-specific password in Apple ID settings
   xcrun notarytool submit dist/Reframe-1.0.0.dmg --apple-id "your-apple-id@example.com" --password "app-specific-password" --team-id "TEAM_ID"
   ```

5. **Staple the notarization ticket**:
   ```bash
   xcrun stapler staple dist/Reframe-1.0.0.dmg
   ```

### Solution 2: Self-Signing (For Development/Testing)

For development and testing purposes, you can self-sign your app:

1. **Create a self-signed certificate**:
   ```bash
   # Create a certificate in Keychain Access
   # Or use this command:
   security create-certificate -k login.keychain -c "Self Signed" -u "C" -t "CSSM_CERT_X_509v3" -x -f "DER" -n "Self Signed Certificate"
   ```

2. **Update package.json**:
   ```json
   "mac": {
     "category": "public.app-category.video",
     "target": ["dmg"],
     "icon": "build/icon.icns",
     "hardenedRuntime": true,
     "entitlements": "build/entitlements.mac.plist",
     "entitlementsInherit": "build/entitlements.mac.plist",
     "identity": "Self Signed Certificate"
   }
   ```

3. **Build the app**:
   ```bash
   npm run build:mac
   ```

### Solution 3: Remove Quarantine Attribute (Quick Fix)

For immediate testing, you can remove the quarantine attribute:

1. **Build without code signing**:
   ```bash
   npm run build:mac
   ```

2. **Remove quarantine attribute**:
   ```bash
   xattr -rd com.apple.quarantine dist/mac/Reframe.app
   ```

3. **For DMG files**:
   ```bash
   xattr -rd com.apple.quarantine dist/Reframe-1.0.0.dmg
   ```

### Solution 4: User Instructions (For End Users)

If you're distributing to users who can handle the security warning:

1. **Right-click the app** and select "Open"
2. **Click "Open"** in the security dialog
3. **The app will run normally** after the first time

Or users can run this command in Terminal:
```bash
sudo spctl --master-disable
```
(Note: This disables Gatekeeper entirely, which is not recommended for security)

## Build Scripts

### For Development (Self-Signed)
```bash
# Add to package.json scripts
"build:mac-dev": "npm run clean && npm run build:css && electron-builder build --mac --config.mac.identity='Self Signed Certificate'"
```

### For Production (Code-Signed)
```bash
# Add to package.json scripts  
"build:mac-prod": "npm run clean && npm run build:css && electron-builder build --mac --config.mac.identity='Developer ID Application: Your Name (TEAM_ID)'"
```

## Troubleshooting

### Common Issues

1. **"No identity found" error**:
   - Check available certificates: `security find-identity -v -p codesigning`
   - Ensure the certificate name matches exactly

2. **Hardened Runtime errors**:
   - Verify entitlements file is correct
   - Check that all required entitlements are included

3. **Notarization failures**:
   - Ensure app is properly code-signed first
   - Check that all dependencies are included
   - Verify Apple ID and app-specific password

### Verification Commands

```bash
# Check if app is code-signed
codesign -dv --verbose=4 dist/mac/Reframe.app

# Check entitlements
codesign -d --entitlements :- dist/mac/Reframe.app

# Verify notarization
spctl --assess --type exec --verbose dist/mac/Reframe.app
```

## Security Considerations

- **Code signing** is the most secure and professional approach
- **Self-signing** is acceptable for development but not for distribution
- **Removing quarantine** should only be used for testing
- **Disabling Gatekeeper** is not recommended for end users

## Recommended Workflow

1. **Development**: Use self-signing or remove quarantine attribute
2. **Beta Testing**: Use self-signing with clear instructions to users
3. **Production**: Use proper code signing and notarization

## Additional Resources

- [Apple Developer Documentation](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [Electron Builder Code Signing](https://www.electron.build/code-signing)
- [macOS Security and Privacy](https://support.apple.com/en-us/HT202491) 