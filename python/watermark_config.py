#!/usr/bin/env python3
"""
Watermark Configuration Utility

This script helps manage watermark settings for the Reframer application.
It provides a command-line interface to enable/disable watermarks and configure their properties.
"""

import argparse
import sys
from config import config

def main():
    parser = argparse.ArgumentParser(description='Configure watermark settings for Reframer')
    parser.add_argument('--enable', action='store_true', help='Enable watermark')
    parser.add_argument('--disable', action='store_true', help='Disable watermark')
    parser.add_argument('--text', type=str, help='Set watermark text')
    parser.add_argument('--position', type=str, 
                       choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                       help='Set watermark position')
    parser.add_argument('--opacity', type=float, help='Set watermark opacity (0.0 to 1.0)')
    parser.add_argument('--font-scale', type=float, help='Set font scale')
    parser.add_argument('--thickness', type=int, help='Set text thickness')
    parser.add_argument('--margin', type=int, help='Set margin from edge (pixels)')
    parser.add_argument('--color', type=int, nargs=3, metavar=('R', 'G', 'B'),
                       help='Set text color (RGB values 0-255)')
    parser.add_argument('--show', action='store_true', help='Show current configuration')
    parser.add_argument('--reset', action='store_true', help='Reset to default configuration')
    
    args = parser.parse_args()
    
    if args.show:
        watermark_config = config.get_watermark_config()
        print("Current watermark configuration:")
        for key, value in watermark_config.items():
            print(f"  {key}: {value}")
        return
    
    if args.reset:
        # Reset to default configuration
        config.set("watermark.enabled", False)
        config.set("watermark.text", "BETA")
        config.set("watermark.position", "bottom-right")
        config.set("watermark.opacity", 0.3)
        config.set("watermark.font_scale", 1.0)
        config.set("watermark.thickness", 2)
        config.set("watermark.color", [255, 255, 255])
        config.set("watermark.margin", 20)
        print("Watermark configuration reset to defaults")
        return
    
    # Apply changes
    if args.enable:
        config.set_watermark_enabled(True)
        print("Watermark enabled")
    
    if args.disable:
        config.set_watermark_enabled(False)
        print("Watermark disabled")
    
    if args.text is not None:
        config.set_watermark_text(args.text)
        print(f"Watermark text set to: {args.text}")
    
    if args.position is not None:
        config.set_watermark_position(args.position)
        print(f"Watermark position set to: {args.position}")
    
    if args.opacity is not None:
        if not 0.0 <= args.opacity <= 1.0:
            print("Error: Opacity must be between 0.0 and 1.0")
            sys.exit(1)
        config.set_watermark_opacity(args.opacity)
        print(f"Watermark opacity set to: {args.opacity}")
    
    if args.font_scale is not None:
        config.set("watermark.font_scale", args.font_scale)
        print(f"Font scale set to: {args.font_scale}")
    
    if args.thickness is not None:
        config.set("watermark.thickness", args.thickness)
        print(f"Text thickness set to: {args.thickness}")
    
    if args.margin is not None:
        config.set("watermark.margin", args.margin)
        print(f"Margin set to: {args.margin} pixels")
    
    if args.color is not None:
        r, g, b = args.color
        if not all(0 <= c <= 255 for c in [r, g, b]):
            print("Error: Color values must be between 0 and 255")
            sys.exit(1)
        config.set("watermark.color", [r, g, b])
        print(f"Text color set to: RGB({r}, {g}, {b})")
    
    # Show final configuration if any changes were made
    if any([args.enable, args.disable, args.text, args.position, args.opacity, 
            args.font_scale, args.thickness, args.margin, args.color]):
        print("\nUpdated watermark configuration:")
        watermark_config = config.get_watermark_config()
        for key, value in watermark_config.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main() 