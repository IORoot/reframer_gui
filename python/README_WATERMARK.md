# Watermark Feature Quick Reference

## Quick Start

### Enable Watermark for Beta Testing
```bash
python watermark_config.py --enable --text "BETA" --opacity 0.3
```

### Disable Watermark for Production
```bash
python watermark_config.py --disable
```

### Show Current Settings
```bash
python watermark_config.py --show
```

## Configuration File

Settings are stored in `config.json`:
```json
{
  "watermark": {
    "enabled": false,
    "text": "BETA",
    "position": "bottom-right",
    "opacity": 0.3,
    "font_scale": 1.0,
    "thickness": 2,
    "color": [255, 255, 255],
    "margin": 20
  }
}
```

## Key Features

- ✅ **On/Off Toggle**: Enable/disable watermark via config file
- ✅ **Custom Text**: Set any text (e.g., "BETA", "v1.0", "TESTING")
- ✅ **5 Positions**: top-left, top-right, bottom-left, bottom-right, center
- ✅ **30% Opacity**: Semi-transparent overlay
- ✅ **Configurable**: All settings in JSON config file
- ✅ **Command Line**: Easy CLI management
- ✅ **Production Ready**: Disable for clean production builds

## Files

- `config.py` - Configuration management system
- `watermark.py` - Watermark rendering engine
- `watermark_config.py` - Command line configuration utility
- `config.json` - Configuration file (auto-created)
- `test_watermark.py` - Test script for verification

## Integration

The watermark is automatically applied during video processing when enabled. No changes needed to the main processing pipeline. 