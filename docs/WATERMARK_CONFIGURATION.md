# Watermark Configuration

The Reframer application includes a configurable watermark system that allows you to overlay text on processed videos. This is particularly useful for beta testing and version identification.

## Configuration File

The watermark settings are stored in `python/config.json`. This file is automatically created with default settings when the application first runs.

### Default Configuration

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

## Configuration Options

### Basic Settings

- **enabled**: `boolean` - Enable or disable watermark overlay
  - `true`: Watermark will be applied to all processed videos
  - `false`: No watermark (production mode)

- **text**: `string` - The text to display as watermark
  - Default: "BETA"
  - Examples: "BETA", "v1.0", "TESTING", "PREVIEW"

### Position and Layout

- **position**: `string` - Where to place the watermark
  - Options: `"top-left"`, `"top-right"`, `"bottom-left"`, `"bottom-right"`, `"center"`
  - Default: `"bottom-right"`

- **margin**: `integer` - Distance from the edge in pixels
  - Default: `20`
  - Range: `0` to any positive number

### Visual Appearance

- **opacity**: `float` - Transparency level (0.0 to 1.0)
  - `0.0`: Completely transparent (invisible)
  - `1.0`: Completely opaque
  - Default: `0.3` (30% opacity)

- **font_scale**: `float` - Text size multiplier
  - Default: `1.0`
  - `0.5`: Half size
  - `2.0`: Double size

- **thickness**: `integer` - Text stroke thickness
  - Default: `2`
  - Range: `1` to any positive number

- **color**: `array` - Text color in RGB format
  - Default: `[255, 255, 255]` (white)
  - Format: `[red, green, blue]` where each value is 0-255
  - Examples: `[255, 0, 0]` (red), `[0, 255, 0]` (green), `[0, 0, 255]` (blue)

## Usage Examples

### Beta Testing Configuration

```json
{
  "watermark": {
    "enabled": true,
    "text": "BETA v1.2",
    "position": "bottom-right",
    "opacity": 0.3,
    "font_scale": 1.0,
    "thickness": 2,
    "color": [255, 255, 255],
    "margin": 20
  }
}
```

### Production Configuration

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

### Custom Branding

```json
{
  "watermark": {
    "enabled": true,
    "text": "Reframer",
    "position": "center",
    "opacity": 0.2,
    "font_scale": 1.5,
    "thickness": 3,
    "color": [0, 150, 255],
    "margin": 50
  }
}
```

## Command Line Configuration

You can also configure watermark settings using the command line utility:

### Show Current Configuration

```bash
python python/watermark_config.py --show
```

### Enable Watermark

```bash
python python/watermark_config.py --enable
```

### Disable Watermark

```bash
python python/watermark_config.py --disable
```

### Set Custom Text

```bash
python python/watermark_config.py --text "BETA v1.3"
```

### Set Position

```bash
python python/watermark_config.py --position top-left
```

### Set Opacity

```bash
python python/watermark_config.py --opacity 0.4
```

### Set Color

```bash
python python/watermark_config.py --color 255 0 0
```

### Reset to Defaults

```bash
python python/watermark_config.py --reset
```

### Multiple Settings at Once

```bash
python python/watermark_config.py --enable --text "TESTING" --position center --opacity 0.5
```

## Command Line Arguments

You can also override watermark settings when running the main processing script:

```bash
python python/main.py --input video.mp4 --output output.mp4 --watermark_enabled --watermark_text "BETA" --watermark_position bottom-right --watermark_opacity 0.3
```

## Workflow Examples

### Beta Testing Workflow

1. **Enable watermark for beta testing:**
   ```bash
   python python/watermark_config.py --enable --text "BETA v1.2" --opacity 0.3
   ```

2. **Process videos with watermark:**
   ```bash
   python python/main.py --input input.mp4 --output output_beta.mp4
   ```

3. **Disable watermark for production:**
   ```bash
   python python/watermark_config.py --disable
   ```

4. **Process videos without watermark:**
   ```bash
   python python/main.py --input input.mp4 --output output_production.mp4
   ```

### Version-Specific Watermarks

```bash
# Version 1.0 beta
python python/watermark_config.py --enable --text "v1.0 BETA" --color 255 165 0

# Version 1.0 release candidate
python python/watermark_config.py --enable --text "v1.0 RC" --color 255 255 0

# Version 1.0 production
python python/watermark_config.py --disable
```

## Technical Details

- The watermark is applied to each frame after cropping but before writing to the output video
- The watermark includes a semi-transparent background for better visibility
- Text positioning automatically adjusts based on frame dimensions
- The watermark system is designed to be lightweight and not significantly impact processing speed
- Configuration changes take effect immediately for new video processing jobs

## Troubleshooting

### Watermark Not Appearing

1. Check if watermark is enabled:
   ```bash
   python python/watermark_config.py --show
   ```

2. Verify the configuration file exists:
   ```bash
   ls -la python/config.json
   ```

3. Check for configuration errors in the console output during processing

### Watermark Too Visible/Invisible

- Adjust the `opacity` setting (0.0 to 1.0)
- Try different `color` values for better contrast
- Increase `thickness` for better visibility

### Watermark Position Issues

- Check that the `position` value is one of the valid options
- Adjust `margin` to move the watermark further from or closer to the edge
- Use `font_scale` to make the text larger or smaller

### Performance Issues

- Reduce `font_scale` for smaller text
- Reduce `thickness` for thinner text
- Consider disabling watermark if performance is critical 