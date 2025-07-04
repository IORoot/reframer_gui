# Build Configuration

This document explains how to configure build-time features for Reframer.

## BETA Watermark Configuration

The BETA watermark feature is controlled by the `build-config.js` file. This allows you to enable/disable the watermark for different builds without modifying the source code.

### Configuration Options

Edit `build-config.js` to control the BETA watermark:

```javascript
module.exports = {
  // BETA watermark settings
  beta: {
    enabled: true,  // Set to false to disable BETA watermark
    text: "BETA",   // Text to display as watermark
    position: "bottom-right", // Position: top-left, top-right, bottom-left, bottom-right, center
    opacity: 0.8    // Opacity: 0.0 to 1.0
  },
  // ... other settings
};
```

### Build Commands

The build configuration is automatically processed when you run any of these commands:

- `npm run build:mac` - Build for macOS
- `npm run build:win` - Build for Windows  
- `npm run build:linux` - Build for Linux

### Usage Examples

#### For Beta Testing (with watermark):
```javascript
// build-config.js
module.exports = {
  beta: {
    enabled: true,
    text: "BETA",
    position: "bottom-right",
    opacity: 0.8
  }
};
```

#### For Release (no watermark):
```javascript
// build-config.js
module.exports = {
  beta: {
    enabled: false
  }
};
```

#### Custom Watermark:
```javascript
// build-config.js
module.exports = {
  beta: {
    enabled: true,
    text: "PREVIEW",
    position: "top-right",
    opacity: 0.6
  }
};
```

### How It Works

1. The `build-config.js` file contains your build settings
2. When you run a build command, `scripts/build-processor.js` reads this configuration
3. The processor modifies the Python source code to include or exclude the watermark
4. The modified code is then built into the final application

### Important Notes

- The watermark is **hardcoded** into the built application - users cannot disable it
- Changes to `build-config.js` only affect new builds, not existing installations
- The watermark appears on **all output videos** when enabled
- The watermark is positioned in the bottom-right corner by default with 80% opacity

### Troubleshooting

If the watermark doesn't appear:
1. Check that `beta.enabled` is set to `true` in `build-config.js`
2. Ensure you're running a fresh build (not using cached files)
3. Check the console output during build for any processing errors 