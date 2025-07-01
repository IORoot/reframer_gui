// Build configuration for Reframer
// This file controls build-time features and can be modified before building

module.exports = {
  // BETA watermark settings
  beta: {
    enabled: true,  // Set to false to disable BETA watermark
    text: "BETA",   // Text to display as watermark
    position: "center", // Position: top-left, top-right, bottom-left, bottom-right, center
    opacity: 0.3    // Opacity: 0.0 to 1.0
  },
  
  // Version information
  version: {
    major: 1,
    minor: 0,
    patch: 0,
    beta: true  // Set to false for release builds
  },
  
  // Build information
  build: {
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  }
}; 