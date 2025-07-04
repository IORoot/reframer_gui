import cv2
import numpy as np
from config import config

class WatermarkRenderer:
    """Handles rendering watermarks on video frames."""
    
    def __init__(self):
        self.watermark_config = config.get_watermark_config()
    
    def update_config(self):
        """Update watermark configuration from config file."""
        self.watermark_config = config.get_watermark_config()
    
    def _get_text_position(self, frame_shape, text_size, position, margin):
        """Calculate text position based on frame dimensions and desired position."""
        frame_height, frame_width = frame_shape[:2]
        text_width, text_height = text_size
        
        if position == "top-left":
            x = margin
            y = margin + text_height
        elif position == "top-right":
            x = frame_width - text_width - margin
            y = margin + text_height
        elif position == "bottom-left":
            x = margin
            y = frame_height - margin
        elif position == "bottom-right":
            x = frame_width - text_width - margin
            y = frame_height - margin
        elif position == "center":
            x = (frame_width - text_width) // 2
            y = (frame_height + text_height) // 2
        else:
            # Default to bottom-right
            x = frame_width - text_width - margin
            y = frame_height - margin
        
        return int(x), int(y)
    
    def _create_watermark_overlay(self, frame, text, position, opacity, font_scale, thickness, color, margin):
        """Create a watermark overlay for the frame."""
        # Create a copy of the frame to work with
        overlay = frame.copy()
        
        # Get text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        
        # Calculate position
        x, y = self._get_text_position(frame.shape, text_size, position, margin)
        
        # Create text with background for better visibility
        # First, draw a semi-transparent background rectangle
        padding = 5
        rect_x1 = x - padding
        rect_y1 = y - text_size[1] - padding
        rect_x2 = x + text_size[0] + padding
        rect_y2 = y + padding
        
        # Ensure rectangle is within frame bounds
        rect_x1 = max(0, rect_x1)
        rect_y1 = max(0, rect_y1)
        rect_x2 = min(frame.shape[1], rect_x2)
        rect_y2 = min(frame.shape[0], rect_y2)
        
        # Draw background rectangle with black color and opacity
        cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 0, 0), -1)
        
        # Draw the text
        cv2.putText(overlay, text, (x, y), font, font_scale, color, thickness)
        
        return overlay
    
    def apply_watermark(self, frame):
        """Apply watermark to a frame if enabled."""
        if not self.watermark_config["enabled"]:
            return frame
        
        # Update config in case it changed
        self.update_config()
        
        # Extract watermark settings
        text = self.watermark_config["text"]
        position = self.watermark_config["position"]
        opacity = self.watermark_config["opacity"]
        font_scale = self.watermark_config["font_scale"]
        thickness = self.watermark_config["thickness"]
        color = tuple(self.watermark_config["color"])
        margin = self.watermark_config["margin"]
        
        # Create watermark overlay
        overlay = self._create_watermark_overlay(
            frame, text, position, opacity, font_scale, thickness, color, margin
        )
        
        # Blend the overlay with the original frame
        alpha = opacity
        beta = 1.0 - alpha
        gamma = 0
        
        watermarked_frame = cv2.addWeighted(frame, beta, overlay, alpha, gamma)
        
        return watermarked_frame
    
    def is_enabled(self):
        """Check if watermark is enabled."""
        self.update_config()
        return self.watermark_config["enabled"]

# Global watermark renderer instance
watermark_renderer = WatermarkRenderer() 