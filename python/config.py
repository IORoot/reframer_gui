import json
import os
from pathlib import Path

class Config:
    """Configuration management for the Reframer application."""
    
    def __init__(self, config_path=None):
        if config_path is None:
            # Default config path in the python directory
            config_path = Path(__file__).parent / "config.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default if not exists."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                print(f"Loaded configuration from: {self.config_path}")
                return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config file: {e}")
                print("Using default configuration")
                return self._get_default_config()
        else:
            # Create default config file
            default_config = self._get_default_config()
            self._save_config(default_config)
            print(f"Created default configuration at: {self.config_path}")
            return default_config
    
    def _get_default_config(self):
        """Get default configuration settings."""
        return {
            "watermark": {
                "enabled": False,
                "text": "BETA",
                "position": "bottom-right",  # top-left, top-right, bottom-left, bottom-right, center
                "opacity": 0.3,  # 30% opacity
                "font_scale": 1.0,
                "thickness": 2,
                "color": [255, 255, 255],  # White color
                "margin": 20  # pixels from edge
            }
        }
    
    def _save_config(self, config):
        """Save configuration to file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error saving config file: {e}")
    
    def get(self, key, default=None):
        """Get a configuration value using dot notation (e.g., 'watermark.enabled')."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """Set a configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save the updated configuration
        self._save_config(self.config)
    
    def get_watermark_config(self):
        """Get watermark configuration."""
        return {
            "enabled": self.get("watermark.enabled", False),
            "text": self.get("watermark.text", "BETA"),
            "position": self.get("watermark.position", "bottom-right"),
            "opacity": self.get("watermark.opacity", 0.3),
            "font_scale": self.get("watermark.font_scale", 1.0),
            "thickness": self.get("watermark.thickness", 2),
            "color": self.get("watermark.color", [255, 255, 255]),
            "margin": self.get("watermark.margin", 20)
        }
    
    def set_watermark_enabled(self, enabled):
        """Enable or disable watermark."""
        self.set("watermark.enabled", enabled)
    
    def set_watermark_text(self, text):
        """Set watermark text."""
        self.set("watermark.text", text)
    
    def set_watermark_position(self, position):
        """Set watermark position."""
        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
        if position not in valid_positions:
            raise ValueError(f"Invalid position. Must be one of: {valid_positions}")
        self.set("watermark.position", position)
    
    def set_watermark_opacity(self, opacity):
        """Set watermark opacity (0.0 to 1.0)."""
        if not 0.0 <= opacity <= 1.0:
            raise ValueError("Opacity must be between 0.0 and 1.0")
        self.set("watermark.opacity", opacity)

# Global config instance
config = Config() 