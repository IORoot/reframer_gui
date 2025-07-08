

# Sign the app with the Developer ID Application certificate
# This is the certificate that Apple provides to developers
# You can find it in the Keychain Access app


# Codesign the .app file
codesign --deep --force --verbose \
  --sign "Developer ID Application: Andy Pearson ($TEAM_ID)" \
  --options runtime \
  ./dist/mac-arm64/Reframe.app

# Verify the app
codesign --verify --deep --strict --verbose=2 ./dist/mac-arm64/Reframe.app


# Create the dmg
hdiutil create -volname "Reframe Installer" \
  -srcfolder ./dist/mac-arm64/Reframe.app \
  -ov -format UDZO ./dist/Reframe-1.0.0-RC1-arm64.dmg

# Codesign the DMG
codesign --force --sign "Developer ID Application: Andy Pearson ($TEAM_ID)" \
  --timestamp --verbose \
  ./dist/Reframe-1.0.0-RC1-arm64.dmg

# Verify the DMG
codesign --verify --deep --strict --verbose=2 ./dist/Reframe-1.0.0-RC1-arm64.dmg


# Notarize the DMG
xcrun notarytool submit ./dist/Reframe-1.0.0-RC1-arm64.dmg \
  --apple-id $USERNAME \
  --password PASSWORD \
  --team-id $TEAM_ID \
  --wait \
  --verbose

# See problems
xcrun notarytool log 5c6da71e-9b5a-43ea-ab78-66f619d6d357 --apple-id $USERNAME --password PASSWORD --team-id $TEAM_ID

# Staple the ticket to the DMG
xcrun stapler staple ./dist/Reframe-1.0.0-RC1-arm64.dmg